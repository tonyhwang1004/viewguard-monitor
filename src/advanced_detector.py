"""
고정확도 졸음 감지 시스템
MediaPipe 기반 다중 지표 복합 판단
"""
import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance
from typing import Tuple, Dict, List


class AdvancedDrowsinessDetector:
    """MediaPipe 기반 고정확도 졸음 감지기"""
    
    def __init__(self, config: Dict = None):
        """
        초기화
        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}
        
        # MediaPipe Face Mesh 초기화
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 눈 랜드마크 인덱스 (MediaPipe 468 포인트 기준)
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        # 입 랜드마크 (하품 감지용)
        self.MOUTH_TOP = 13
        self.MOUTH_BOTTOM = 14
        self.MOUTH_LEFT = 78
        self.MOUTH_RIGHT = 308
        
        # 머리 포즈 계산용 포인트
        self.NOSE_TIP = 1
        self.CHIN = 152
        self.FOREHEAD = 10
        
        # 임계값
        self.EAR_THRESHOLD = self.config.get('ear_threshold', 0.2)
        self.HEAD_TILT_THRESHOLD = self.config.get('head_tilt_threshold', 0.58)
        
    def calculate_EAR(self, eye_points: List[Tuple[float, float]]) -> float:
        """
        Eye Aspect Ratio 계산
        눈이 감기면 값이 작아짐 (정상: 0.25~0.3, 감김: <0.2)
        
        Args:
            eye_points: 눈의 6개 랜드마크 좌표 [(x,y), ...]
            
        Returns:
            EAR 값
        """
        # 수직 거리 2개
        A = distance.euclidean(eye_points[1], eye_points[5])
        B = distance.euclidean(eye_points[2], eye_points[4])
        
        # 수평 거리
        C = distance.euclidean(eye_points[0], eye_points[3])
        
        # EAR 공식
        ear = (A + B) / (2.0 * C)
        return ear
    
    def calculate_head_tilt(self, landmarks, image_shape: Tuple[int, int]) -> float:
        """
        머리 기울기 계산 (핵심 지표!)
        고개를 숙이면 코와 이마의 비율이 변함
        
        Args:
            landmarks: MediaPipe 랜드마크
            image_shape: 이미지 크기 (h, w)
            
        Returns:
            머리 기울기 비율 (정상: ~0.5, 숙임: >0.58)
        """
        h, w = image_shape[:2]
        
        # 주요 포인트 추출
        nose_tip = landmarks[self.NOSE_TIP]
        chin = landmarks[self.CHIN]
        forehead = landmarks[self.FOREHEAD]
        
        # Y 좌표를 픽셀로 변환
        nose_y = nose_tip.y * h
        chin_y = chin.y * h
        forehead_y = forehead.y * h
        
        # 코가 얼굴 전체에서 차지하는 위치 비율
        # 정상적으로 앉아있으면 약 0.5
        # 고개 숙이면 0.6 이상으로 증가
        if chin_y - forehead_y == 0:
            return 0.5
            
        head_ratio = (nose_y - forehead_y) / (chin_y - forehead_y)
        
        return head_ratio
    
    def calculate_MAR(self, mouth_landmarks) -> float:
        """
        Mouth Aspect Ratio 계산
        하품 감지용 (선택적)
        
        Args:
            mouth_landmarks: 입 랜드마크
            
        Returns:
            MAR 값
        """
        # 입의 수직/수평 비율
        vertical = distance.euclidean(
            (mouth_landmarks[0].x, mouth_landmarks[0].y),
            (mouth_landmarks[1].x, mouth_landmarks[1].y)
        )
        horizontal = distance.euclidean(
            (mouth_landmarks[2].x, mouth_landmarks[2].y),
            (mouth_landmarks[3].x, mouth_landmarks[3].y)
        )
        
        if horizontal == 0:
            return 0
        
        mar = vertical / horizontal
        return mar
    
    def get_eye_coordinates(self, landmarks, eye_indices: List[int], 
                           frame_shape: Tuple[int, int]) -> List[Tuple[float, float]]:
        """
        눈 랜드마크를 픽셀 좌표로 변환
        
        Args:
            landmarks: MediaPipe 랜드마크
            eye_indices: 눈 포인트 인덱스
            frame_shape: 프레임 크기 (h, w)
            
        Returns:
            픽셀 좌표 리스트
        """
        h, w = frame_shape[:2]
        coords = []
        
        for idx in eye_indices:
            landmark = landmarks[idx]
            x = landmark.x * w
            y = landmark.y * h
            coords.append((x, y))
        
        return coords
    
    def detect_drowsiness(self, frame: np.ndarray) -> Tuple[bool, float, Dict]:
        """
        졸음 감지 - 다중 지표 복합 판단
        
        Args:
            frame: 입력 이미지 (BGR)
            
        Returns:
            (is_drowsy, confidence, details)
            - is_drowsy: 졸음 여부
            - confidence: 신뢰도 (0.0 ~ 1.0)
            - details: 상세 정보 딕셔너리
        """
        # RGB 변환
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # MediaPipe 처리
        results = self.face_mesh.process(rgb_frame)
        
        # 얼굴 미감지
        if not results.multi_face_landmarks:
            return False, 0.0, {"status": "no_face_detected"}
        
        face_landmarks = results.multi_face_landmarks[0].landmark
        
        # 1. EAR 계산 (눈 감김)
        left_eye_coords = self.get_eye_coordinates(
            face_landmarks, self.LEFT_EYE, frame.shape
        )
        right_eye_coords = self.get_eye_coordinates(
            face_landmarks, self.RIGHT_EYE, frame.shape
        )
        
        left_ear = self.calculate_EAR(left_eye_coords)
        right_ear = self.calculate_EAR(right_eye_coords)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # 2. 머리 기울기 계산 (핵심!)
        head_tilt = self.calculate_head_tilt(face_landmarks, frame.shape)
        
        # 3. 판단 기준
        eyes_closed = avg_ear < self.EAR_THRESHOLD
        head_down = head_tilt > self.HEAD_TILT_THRESHOLD
        
        # 4. 종합 판단
        is_drowsy = False
        confidence = 0.0
        
        if eyes_closed and head_down:
            # 두 조건 모두 만족: 매우 높은 확신
            is_drowsy = True
            confidence = 0.95
        elif head_down:
            # 고개만 숙임: 높은 확신
            is_drowsy = True
            confidence = 0.80
        elif eyes_closed:
            # 눈만 감음: 중간 확신 (눈 깜빡일 수도 있음)
            is_drowsy = True
            confidence = 0.60
        
        # 상세 정보
        details = {
            'ear': float(avg_ear),
            'left_ear': float(left_ear),
            'right_ear': float(right_ear),
            'head_tilt': float(head_tilt),
            'eyes_closed': eyes_closed,
            'head_down': head_down,
            'status': 'drowsy' if is_drowsy else 'alert'
        }
        
        return is_drowsy, confidence, details
    
    def draw_debug_info(self, frame: np.ndarray, details: Dict) -> np.ndarray:
        """
        디버그 정보를 프레임에 그리기
        
        Args:
            frame: 입력 프레임
            details: 감지 결과 상세 정보
            
        Returns:
            정보가 그려진 프레임
        """
        frame_copy = frame.copy()
        h, w = frame.shape[:2]
        
        # 텍스트 배경
        overlay = frame_copy.copy()
        cv2.rectangle(overlay, (10, 10), (300, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame_copy, 0.4, 0, frame_copy)
        
        # 정보 출력
        y_offset = 30
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        if 'status' in details and details['status'] == 'no_face_detected':
            cv2.putText(frame_copy, "No Face Detected", (15, y_offset),
                       font, 0.6, (0, 0, 255), 2)
        else:
            cv2.putText(frame_copy, f"EAR: {details['ear']:.3f}", (15, y_offset),
                       font, 0.6, (255, 255, 255), 2)
            y_offset += 25
            
            cv2.putText(frame_copy, f"Head Tilt: {details['head_tilt']:.3f}", 
                       (15, y_offset), font, 0.6, (255, 255, 255), 2)
            y_offset += 25
            
            status_color = (0, 0, 255) if details['status'] == 'drowsy' else (0, 255, 0)
            cv2.putText(frame_copy, f"Status: {details['status'].upper()}", 
                       (15, y_offset), font, 0.6, status_color, 2)
            y_offset += 25
            
            cv2.putText(frame_copy, f"Eyes: {'CLOSED' if details['eyes_closed'] else 'OPEN'}", 
                       (15, y_offset), font, 0.5, (255, 255, 255), 2)
            y_offset += 25
            
            cv2.putText(frame_copy, f"Head: {'DOWN' if details['head_down'] else 'UP'}", 
                       (15, y_offset), font, 0.5, (255, 255, 255), 2)
        
        return frame_copy
    
    def __del__(self):
        """리소스 정리"""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
