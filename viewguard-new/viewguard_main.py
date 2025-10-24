"""
ViewGuard - 졸음 감지 모니터링 시스템
CCTV 화면 캡처 및 실시간 분석
"""

import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import time
import json
import requests
from pathlib import Path


class DrowsinessDetector:
    """졸음 감지 클래스"""
    
    def __init__(self):
        # MediaPipe 초기화
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 설정 로드
        self.load_settings()
        
        # 상태 변수
        self.drowsy_count = 0
        self.last_alert_time = 0
        
    def load_settings(self):
        """설정 파일 로드"""
        try:
            with open('config/settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            self.ear_threshold = settings['detection']['ear_threshold']
            self.head_tilt_threshold = settings['detection']['head_tilt_threshold']
            self.drowsy_threshold = settings['detection']['drowsy_count_threshold']
            self.alert_cooldown = settings['detection']['alert_cooldown']
            
            # GitHub 설정
            self.github_enabled = settings['github']['enabled']
            self.github_token = settings['github']['token']
            self.github_owner = settings['github']['repo_owner']
            self.github_repo = settings['github']['repo_name']
            
        except Exception as e:
            print(f"⚠️ 설정 파일 로드 실패: {e}")
            # 기본값 사용
            self.ear_threshold = 0.2
            self.head_tilt_threshold = 0.58
            self.drowsy_threshold = 5
            self.alert_cooldown = 300
            self.github_enabled = False
    
    def calculate_ear(self, landmarks, indices):
        """EAR (Eye Aspect Ratio) 계산"""
        # 눈의 수직 거리
        vertical1 = np.linalg.norm(landmarks[indices[1]] - landmarks[indices[5]])
        vertical2 = np.linalg.norm(landmarks[indices[2]] - landmarks[indices[4]])
        
        # 눈의 수평 거리
        horizontal = np.linalg.norm(landmarks[indices[0]] - landmarks[indices[3]])
        
        # EAR 계산
        ear = (vertical1 + vertical2) / (2.0 * horizontal)
        return ear
    
    def calculate_head_tilt(self, landmarks):
        """머리 기울기 계산"""
        # 얼굴의 주요 포인트
        nose_tip = landmarks[1]
        chin = landmarks[152]
        
        # 수직선과의 각도 계산
        dy = chin[1] - nose_tip[1]
        dx = chin[0] - nose_tip[0]
        
        angle = abs(np.arctan2(dx, dy))
        return angle
    
    def detect_drowsiness(self, frame):
        """졸음 감지"""
        # RGB로 변환 (MediaPipe는 RGB 사용)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        is_drowsy = False
        ear_value = 0
        head_tilt = 0
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # 랜드마크를 numpy 배열로 변환
            h, w = frame.shape[:2]
            landmarks = np.array([
                [landmark.x * w, landmark.y * h]
                for landmark in face_landmarks.landmark
            ])
            
            # 왼쪽 눈 EAR (랜드마크 인덱스)
            left_eye_indices = [362, 385, 387, 263, 373, 380]
            # 오른쪽 눈 EAR
            right_eye_indices = [33, 160, 158, 133, 153, 144]
            
            left_ear = self.calculate_ear(landmarks, left_eye_indices)
            right_ear = self.calculate_ear(landmarks, right_eye_indices)
            
            # 평균 EAR
            ear_value = (left_ear + right_ear) / 2.0
            
            # 머리 기울기
            head_tilt = self.calculate_head_tilt(landmarks)
            
            # 졸음 판단
            if ear_value < self.ear_threshold or head_tilt > self.head_tilt_threshold:
                self.drowsy_count += 1
            else:
                self.drowsy_count = max(0, self.drowsy_count - 1)
            
            # 임계값 초과 시 졸음으로 판단
            if self.drowsy_count >= self.drowsy_threshold:
                is_drowsy = True
            
            # 화면에 정보 표시
            self.draw_info(frame, ear_value, head_tilt, is_drowsy)
        
        return is_drowsy, ear_value, head_tilt
    
    def draw_info(self, frame, ear, head_tilt, is_drowsy):
        """화면에 정보 표시"""
        # 배경 박스
        cv2.rectangle(frame, (10, 10), (400, 120), (0, 0, 0), -1)
        
        # EAR 정보
        color = (0, 0, 255) if ear < self.ear_threshold else (0, 255, 0)
        cv2.putText(frame, f"EAR: {ear:.3f}", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # 머리 기울기
        color = (0, 0, 255) if head_tilt > self.head_tilt_threshold else (0, 255, 0)
        cv2.putText(frame, f"Head Tilt: {head_tilt:.3f}", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # 졸음 카운터
        cv2.putText(frame, f"Count: {self.drowsy_count}/{self.drowsy_threshold}",
                   (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 졸음 경고
        if is_drowsy:
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 80), (0, 0, 255), -1)
            cv2.putText(frame, "!!! DROWSY DETECTED !!!", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    def send_github_alert(self, ear, head_tilt, seat_id="CH01"):
        """GitHub Issue로 알림 전송"""
        if not self.github_enabled:
            print("⚠️ GitHub 알림이 비활성화되어 있습니다.")
            return
        
        # 쿨다운 체크
        current_time = time.time()
        if current_time - self.last_alert_time < self.alert_cooldown:
            print("⏳ 알림 쿨다운 중...")
            return
        
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Issue 제목
        title = f"🚨 [졸음 감지] {timestamp} - {seat_id}"
        
        # Issue 본문
        body = f"""
## 🚨 졸음 감지 알림

**감지 시간:** {timestamp}  
**좌석:** {seat_id}

### 📊 감지 정보
- **EAR:** {ear:.3f} (기준: {self.ear_threshold})
- **Head Tilt:** {head_tilt:.3f} (기준: {self.head_tilt_threshold})

### ✅ 조치 사항
- [ ] 학생 확인
- [ ] 상황 파악
- [ ] 필요 시 조치

---
*자동 생성된 알림입니다.*
"""
        
        # GitHub API 호출
        url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/issues"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "title": title,
            "body": body,
            "labels": ["drowsiness", "alert"]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                issue_url = response.json()['html_url']
                print(f"✅ GitHub Issue 생성: {issue_url}")
                self.last_alert_time = current_time
            else:
                print(f"❌ GitHub Issue 생성 실패: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ 알림 전송 오류: {e}")


class CCTVMonitor:
    """CCTV 모니터링 메인 클래스"""
    
    def __init__(self, camera_index=0):
        """
        camera_index: 
        - 0: 웹캠
        - 1, 2, ...: 추가 카메라
        - 'rtsp://...' : RTSP 스트림 URL
        """
        self.camera_index = camera_index
        self.detector = DrowsinessDetector()
        self.running = False
        
    def start(self):
        """모니터링 시작"""
        print("=" * 60)
        print("ViewGuard 졸음 모니터링 시스템 시작")
        print("=" * 60)
        print(f"카메라: {self.camera_index}")
        print(f"EAR 임계값: {self.detector.ear_threshold}")
        print(f"Head Tilt 임계값: {self.detector.head_tilt_threshold}")
        print(f"GitHub 알림: {'활성화' if self.detector.github_enabled else '비활성화'}")
        print("-" * 60)
        print("종료하려면 'q' 키를 누르세요")
        print("=" * 60)
        
        # 카메라 열기
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            print("❌ 카메라를 열 수 없습니다!")
            return
        
        # 해상도 설정 (선택사항)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.running = True
        
        try:
            while self.running:
                ret, frame = cap.read()
                
                if not ret:
                    print("❌ 프레임을 읽을 수 없습니다!")
                    break
                
                # 졸음 감지
                is_drowsy, ear, head_tilt = self.detector.detect_drowsiness(frame)
                
                # 졸음 감지 시 알림
                if is_drowsy:
                    print(f"🚨 졸음 감지! EAR: {ear:.3f}, Tilt: {head_tilt:.3f}")
                    self.detector.send_github_alert(ear, head_tilt)
                
                # 화면 표시
                cv2.imshow('ViewGuard - Drowsiness Monitor', frame)
                
                # 'q' 키로 종료
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\n⚠️ 사용자가 중단했습니다.")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("✅ 모니터링 종료")


def main():
    """메인 함수"""
    print("""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║            👁️  ViewGuard v1.0                   ║
    ║        졸음 감지 모니터링 시스템                 ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    # 카메라 선택
    print("카메라 옵션:")
    print("  0: 기본 웹캠")
    print("  1: USB 카메라 1")
    print("  2: USB 카메라 2")
    print("  또는 RTSP URL 입력 (예: rtsp://192.168.0.100:554/stream)")
    
    camera_input = input("\n카메라 선택 (기본값: 0): ").strip()
    
    if camera_input == "":
        camera_index = 0
    elif camera_input.startswith("rtsp://"):
        camera_index = camera_input
    else:
        try:
            camera_index = int(camera_input)
        except:
            print("⚠️ 잘못된 입력입니다. 기본 웹캠(0)을 사용합니다.")
            camera_index = 0
    
    # 모니터링 시작
    monitor = CCTVMonitor(camera_index)
    monitor.start()


if __name__ == "__main__":
    main()
