"""
뷰가드웹 화면 캡처 모듈
"""
import cv2
import numpy as np
from PIL import ImageGrab
import json
from typing import Dict, Tuple, Optional
import os


class ViewGuardCapture:
    """뷰가드웹 화면 캡처 및 ROI 관리"""
    
    def __init__(self, config_path: str = 'config/seats.json'):
        """
        초기화
        Args:
            config_path: 좌석 설정 파일 경로
        """
        self.config_path = config_path
        self.seats = self.load_seats()
        
    def load_seats(self) -> Dict:
        """
        저장된 좌석 좌표 불러오기
        
        Returns:
            좌석 정보 딕셔너리
        """
        if not os.path.exists(self.config_path):
            print(f"⚠️  좌석 설정 파일이 없습니다: {self.config_path}")
            print("ROI Manager를 먼저 실행하여 좌석을 설정하세요.")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('seats', {})
        except Exception as e:
            print(f"❌ 좌석 설정 로드 실패: {e}")
            return {}
    
    def save_seats(self, seats: Dict) -> bool:
        """
        좌석 정보 저장
        
        Args:
            seats: 저장할 좌석 정보
            
        Returns:
            성공 여부
        """
        try:
            data = {
                "comment": "ROI Manager로 생성된 좌석 설정",
                "seats": seats
            }
            
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.seats = seats
            return True
        except Exception as e:
            print(f"❌ 좌석 설정 저장 실패: {e}")
            return False
    
    def capture_screen(self, bbox: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        화면 캡처
        
        Args:
            bbox: 캡처할 영역 (x1, y1, x2, y2). None이면 전체 화면
            
        Returns:
            캡처된 이미지 (BGR)
        """
        try:
            if bbox:
                screen = ImageGrab.grab(bbox=bbox)
            else:
                screen = ImageGrab.grab()
            
            # PIL to OpenCV (RGB -> BGR)
            screen_np = np.array(screen)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            
            return screen_bgr
        except Exception as e:
            print(f"❌ 화면 캡처 실패: {e}")
            return None
    
    def get_seat_roi(self, screen: np.ndarray, seat_id: str) -> Optional[np.ndarray]:
        """
        특정 좌석 영역만 추출
        
        Args:
            screen: 전체 화면 이미지
            seat_id: 좌석 ID
            
        Returns:
            ROI 이미지 또는 None
        """
        if seat_id not in self.seats:
            return None
        
        seat = self.seats[seat_id]
        
        # 좌석이 비활성화되어 있으면 None 반환
        if not seat.get('enabled', True):
            return None
        
        try:
            x = seat['x']
            y = seat['y']
            w = seat['width']
            h = seat['height']
            
            # 범위 체크
            if y + h > screen.shape[0] or x + w > screen.shape[1]:
                print(f"⚠️  좌석 {seat_id} 좌표가 화면을 벗어남")
                return None
            
            roi = screen[y:y+h, x:x+w]
            return roi
        except Exception as e:
            print(f"❌ 좌석 {seat_id} ROI 추출 실패: {e}")
            return None
    
    def get_all_seat_rois(self, screen: np.ndarray) -> Dict[str, np.ndarray]:
        """
        모든 좌석의 ROI 추출
        
        Args:
            screen: 전체 화면 이미지
            
        Returns:
            {seat_id: roi_image} 딕셔너리
        """
        rois = {}
        
        for seat_id in self.seats.keys():
            roi = self.get_seat_roi(screen, seat_id)
            if roi is not None:
                rois[seat_id] = roi
        
        return rois
    
    def draw_seat_boxes(self, screen: np.ndarray, 
                       highlight_seats: Dict[str, Tuple[int, int, int]] = None) -> np.ndarray:
        """
        화면에 좌석 박스 그리기 (디버깅용)
        
        Args:
            screen: 화면 이미지
            highlight_seats: {seat_id: (B, G, R)} 특정 좌석 하이라이트
            
        Returns:
            박스가 그려진 이미지
        """
        screen_copy = screen.copy()
        
        for seat_id, seat in self.seats.items():
            if not seat.get('enabled', True):
                continue
            
            x, y, w, h = seat['x'], seat['y'], seat['width'], seat['height']
            
            # 색상 결정
            if highlight_seats and seat_id in highlight_seats:
                color = highlight_seats[seat_id]
                thickness = 3
            else:
                color = (0, 255, 0)  # 초록색
                thickness = 2
            
            # 사각형 그리기
            cv2.rectangle(screen_copy, (x, y), (x+w, y+h), color, thickness)
            
            # 좌석 ID 텍스트
            cv2.putText(screen_copy, str(seat_id), (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # 채널 정보
            if 'channel' in seat:
                cv2.putText(screen_copy, seat['channel'], (x, y+h+20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return screen_copy
    
    def get_seat_count(self) -> int:
        """활성화된 좌석 수 반환"""
        return sum(1 for seat in self.seats.values() if seat.get('enabled', True))
    
    def get_seat_info(self, seat_id: str) -> Optional[Dict]:
        """좌석 정보 반환"""
        return self.seats.get(seat_id)
