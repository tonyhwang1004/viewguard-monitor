"""
채널 버튼 위치 설정 GUI
뷰가드웹 하단의 채널 버튼(1-16) 위치를 마우스로 클릭하여 저장
"""
import cv2
import numpy as np
from PIL import ImageGrab
import json
import os
import sys
sys.path.append('src')

from channel_controller import ChannelController


class ChannelSetup:
    """채널 버튼 위치 설정"""
    
    def __init__(self):
        """초기화"""
        self.channel_buttons = {}  # {채널번호: (x, y)}
        self.capture_region = None  # 캡처 영역
        self.screen = None
        self.display = None
        
        # 설정 단계
        self.setup_stage = "capture_region"  # capture_region -> buttons
        
        # 캡처 영역 설정용
        self.drawing = False
        self.start_point = None
        self.end_point = None
        
        print("=" * 70)
        print("🎮 채널 버튼 위치 설정")
        print("=" * 70)
        print("\n단계 1: 캡처 영역 설정")
        print("  - 뷰가드웹 영상 영역을 드래그로 지정")
        print("  - Enter: 영역 확정 및 다음 단계")
        print("\n단계 2: 채널 버튼 클릭")
        print("  - 화면 하단의 CH 01 버튼부터 CH 16까지 순서대로 클릭")
        print("  - 각 버튼을 정확히 클릭하세요")
        print("  - D: 마지막 버튼 삭제")
        print("  - S: 저장하고 종료")
        print("  - ESC: 취소")
        print("=" * 70)
    
    def capture_screen(self):
        """전체 화면 캡처"""
        screen = ImageGrab.grab()
        screen_np = np.array(screen)
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        return screen_bgr
    
    def mouse_callback(self, event, x, y, flags, param):
        """마우스 이벤트 처리"""
        if self.setup_stage == "capture_region":
            # 캡처 영역 설정 모드
            if event == cv2.EVENT_LBUTTONDOWN:
                self.drawing = True
                self.start_point = (x, y)
                self.end_point = (x, y)
            
            elif event == cv2.EVENT_MOUSEMOVE:
                if self.drawing:
                    self.end_point = (x, y)
            
            elif event == cv2.EVENT_LBUTTONUP:
                self.drawing = False
                self.end_point = (x, y)
        
        elif self.setup_stage == "buttons":
            # 버튼 클릭 모드
            if event == cv2.EVENT_LBUTTONDOWN:
                self.add_button(x, y)
    
    def add_button(self, x, y):
        """채널 버튼 추가"""
        # 다음 채널 번호
        next_channel = len(self.channel_buttons) + 1
        
        if next_channel > 16:
            print("⚠️  이미 16개 버튼이 모두 설정되었습니다")
            return
        
        self.channel_buttons[str(next_channel)] = (x, y)
        print(f"✅ CH{next_channel:02d} 버튼 위치 저장: ({x}, {y})")
    
    def delete_last_button(self):
        """마지막 버튼 삭제"""
        if not self.channel_buttons:
            print("⚠️  삭제할 버튼이 없습니다")
            return
        
        # 가장 큰 채널 번호 찾기
        max_ch = max(int(k) for k in self.channel_buttons.keys())
        del self.channel_buttons[str(max_ch)]
        print(f"🗑️  CH{max_ch:02d} 버튼 삭제됨")
    
    def get_capture_region_rect(self):
        """캡처 영역 사각형 반환"""
        if not self.start_point or not self.end_point:
            return None
        
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        
        # 최소 크기 체크
        if w < 100 or h < 100:
            return None
        
        return (x, y, w, h)
    
    def draw_interface(self):
        """화면에 UI 그리기"""
        self.display = self.screen.copy()
        
        if self.setup_stage == "capture_region":
            # 캡처 영역 표시
            if self.drawing and self.start_point and self.end_point:
                cv2.rectangle(self.display, self.start_point, self.end_point,
                             (0, 255, 255), 3)
            
            elif self.capture_region:
                x, y, w, h = self.capture_region
                cv2.rectangle(self.display, (x, y), (x+w, y+h),
                             (0, 255, 0), 3)
            
            # 안내 텍스트
            cv2.rectangle(self.display, (10, 10), (500, 100), (0, 0, 0), -1)
            cv2.putText(self.display, "Step 1: Drag to select capture region",
                       (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(self.display, "Press ENTER to confirm",
                       (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        elif self.setup_stage == "buttons":
            # 설정된 버튼들 표시
            for ch_str, (x, y) in self.channel_buttons.items():
                cv2.circle(self.display, (x, y), 10, (0, 255, 0), -1)
                cv2.putText(self.display, ch_str, (x-10, y-15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 캡처 영역 표시
            if self.capture_region:
                x, y, w, h = self.capture_region
                cv2.rectangle(self.display, (x, y), (x+w, y+h),
                             (0, 255, 0), 2)
            
            # 안내 텍스트
            count = len(self.channel_buttons)
            cv2.rectangle(self.display, (10, 10), (500, 130), (0, 0, 0), -1)
            cv2.putText(self.display, f"Step 2: Click channel buttons ({count}/16)",
                       (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(self.display, f"Next: CH {count+1:02d}",
                       (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(self.display, "D: Delete last | S: Save & Exit",
                       (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def save_config(self):
        """설정 저장"""
        if not self.capture_region:
            print("❌ 캡처 영역이 설정되지 않았습니다")
            return False
        
        if len(self.channel_buttons) < 16:
            print(f"⚠️  {len(self.channel_buttons)}개 버튼만 설정되었습니다")
            response = input("저장하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                return False
        
        try:
            data = {
                'buttons': self.channel_buttons,
                'total_channels': 16,
                'capture_region': self.capture_region,
                'comment': '채널 버튼 위치 및 캡처 영역'
            }
            
            config_path = 'config/channel_positions.json'
            os.makedirs('config', exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 설정 저장 완료: {config_path}")
            print(f"   - 채널 버튼: {len(self.channel_buttons)}개")
            print(f"   - 캡처 영역: {self.capture_region}")
            return True
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
            return False
    
    def run(self):
        """설정 프로그램 실행"""
        # 초기 화면 캡처
        print("\n📸 화면 캡처 중...")
        self.screen = self.capture_screen()
        
        # OpenCV 윈도우 생성
        window_name = 'Channel Setup'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        # 화면 크기 조정
        h, w = self.screen.shape[:2]
        if w > 1920 or h > 1080:
            cv2.resizeWindow(window_name, 1920, 1080)
        
        print("✅ 설정 시작!\n")
        
        while True:
            # 화면 업데이트
            self.draw_interface()
            cv2.imshow(window_name, self.display)
            
            # 키 입력
            key = cv2.waitKey(1) & 0xFF
            
            if key == 13:  # Enter
                if self.setup_stage == "capture_region":
                    # 캡처 영역 확정
                    region = self.get_capture_region_rect()
                    if region:
                        self.capture_region = region
                        self.setup_stage = "buttons"
                        print("\n✅ 캡처 영역 설정 완료!")
                        print("이제 채널 버튼을 클릭하세요 (CH 01부터 시작)\n")
                    else:
                        print("⚠️  유효한 영역을 지정하세요 (최소 100x100)")
            
            elif key == ord('d') or key == ord('D'):
                self.delete_last_button()
            
            elif key == ord('r') or key == ord('R'):
                # 화면 새로고침
                print("🔄 화면 새로고침...")
                self.screen = self.capture_screen()
            
            elif key == ord('s') or key == ord('S'):
                if self.save_config():
                    break
            
            elif key == 27:  # ESC
                print("❌ 취소됨")
                break
        
        cv2.destroyAllWindows()


def main():
    """메인 함수"""
    setup = ChannelSetup()
    setup.run()


if __name__ == "__main__":
    main()
