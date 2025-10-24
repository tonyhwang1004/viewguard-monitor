"""
ROI Manager - 좌석 위치 설정 GUI
마우스로 클릭하여 각 좌석의 위치를 지정
"""
import cv2
import numpy as np
from capture import ViewGuardCapture
from typing import List, Tuple, Optional


class ROIManager:
    """좌석 위치 설정 GUI"""
    
    def __init__(self, capture: ViewGuardCapture):
        """
        초기화
        Args:
            capture: ViewGuardCapture 인스턴스
        """
        self.capture = capture
        self.seats = {}
        self.current_seat_id = 1
        
        # 마우스 드래그 관련
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.temp_rect = None
        
        # 화면
        self.screen = None
        self.display = None
        
        print("=" * 60)
        print("🎯 ROI Manager - 좌석 위치 설정")
        print("=" * 60)
        print("사용법:")
        print("  1. 마우스로 드래그하여 좌석 영역 지정")
        print("  2. Enter: 현재 영역을 좌석으로 저장")
        print("  3. D: 마지막 좌석 삭제")
        print("  4. R: 화면 새로고침 (다시 캡처)")
        print("  5. S: 저장하고 종료")
        print("  6. ESC: 저장하지 않고 종료")
        print("=" * 60)
    
    def mouse_callback(self, event, x, y, flags, param):
        """마우스 이벤트 처리"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # 드래그 시작
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            # 드래그 중
            if self.drawing:
                self.end_point = (x, y)
                
        elif event == cv2.EVENT_LBUTTONUP:
            # 드래그 종료
            self.drawing = False
            self.end_point = (x, y)
            
            # 최소 크기 체크 (너무 작은 영역 제외)
            if self.is_valid_rect():
                self.temp_rect = self.get_rect()
    
    def is_valid_rect(self) -> bool:
        """유효한 사각형인지 확인"""
        if not self.start_point or not self.end_point:
            return False
        
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # 최소 크기: 50x50
        return width >= 50 and height >= 50
    
    def get_rect(self) -> Tuple[int, int, int, int]:
        """현재 사각형 좌표 반환 (x, y, width, height)"""
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return (x, y, width, height)
    
    def draw_interface(self):
        """화면에 UI 그리기"""
        self.display = self.screen.copy()
        
        # 기존 좌석들 그리기
        for seat_id, seat in self.seats.items():
            x, y, w, h = seat['x'], seat['y'], seat['width'], seat['height']
            
            # 저장된 좌석 (초록색)
            cv2.rectangle(self.display, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(self.display, f"Seat {seat_id}", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 현재 그리는 중인 사각형 (노란색)
        if self.drawing and self.start_point and self.end_point:
            cv2.rectangle(self.display, self.start_point, self.end_point, 
                         (0, 255, 255), 2)
        
        # 임시 사각형 (빨간색)
        if self.temp_rect:
            x, y, w, h = self.temp_rect
            cv2.rectangle(self.display, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(self.display, f"Next: Seat {self.current_seat_id}", 
                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 상태 정보 표시
        info_y = 30
        cv2.rectangle(self.display, (10, 10), (400, 120), (0, 0, 0), -1)
        cv2.putText(self.display, f"Total Seats: {len(self.seats)}", 
                   (20, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        info_y += 30
        cv2.putText(self.display, f"Next Seat: {self.current_seat_id}", 
                   (20, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        info_y += 30
        cv2.putText(self.display, "Enter: Save | D: Delete | S: Save&Exit", 
                   (20, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def add_seat(self):
        """현재 사각형을 좌석으로 추가"""
        if not self.temp_rect:
            print("⚠️  먼저 영역을 지정하세요")
            return
        
        x, y, w, h = self.temp_rect
        
        seat_info = {
            'x': int(x),
            'y': int(y),
            'width': int(w),
            'height': int(h),
            'channel': f"CH{self.current_seat_id:02d}",
            'enabled': True
        }
        
        self.seats[str(self.current_seat_id)] = seat_info
        print(f"✅ 좌석 {self.current_seat_id} 추가: ({x}, {y}, {w}, {h})")
        
        self.current_seat_id += 1
        self.temp_rect = None
        self.start_point = None
        self.end_point = None
    
    def delete_last_seat(self):
        """마지막 좌석 삭제"""
        if not self.seats:
            print("⚠️  삭제할 좌석이 없습니다")
            return
        
        # 가장 큰 seat_id 찾기
        max_id = max(int(k) for k in self.seats.keys())
        del self.seats[str(max_id)]
        
        print(f"🗑️  좌석 {max_id} 삭제됨")
        
        # current_seat_id 조정
        if self.seats:
            self.current_seat_id = max(int(k) for k in self.seats.keys()) + 1
        else:
            self.current_seat_id = 1
    
    def save_and_exit(self) -> bool:
        """좌석 정보 저장하고 종료"""
        if not self.seats:
            print("⚠️  저장할 좌석이 없습니다")
            return False
        
        success = self.capture.save_seats(self.seats)
        
        if success:
            print(f"✅ {len(self.seats)}개 좌석 저장 완료!")
            print(f"📁 저장 위치: {self.capture.config_path}")
            return True
        else:
            print("❌ 저장 실패")
            return False
    
    def refresh_screen(self):
        """화면 다시 캡처"""
        print("🔄 화면 새로고침...")
        self.screen = self.capture.capture_screen()
        if self.screen is None:
            print("❌ 화면 캡처 실패")
            return False
        return True
    
    def run(self):
        """ROI Manager 실행"""
        # 초기 화면 캡처
        if not self.refresh_screen():
            return
        
        # 기존 좌석 정보 로드
        if self.capture.seats:
            print(f"📋 기존 좌석 {len(self.capture.seats)}개 로드됨")
            response = input("기존 설정을 사용하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                self.seats = self.capture.seats.copy()
                self.current_seat_id = max(int(k) for k in self.seats.keys()) + 1
        
        # OpenCV 윈도우 생성
        window_name = 'ROI Manager - 좌석 설정'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        # 화면 크기 조정 (큰 화면인 경우)
        h, w = self.screen.shape[:2]
        if w > 1920 or h > 1080:
            cv2.resizeWindow(window_name, 1920, 1080)
        
        print("\n✅ ROI Manager 시작!")
        
        while True:
            # 화면 업데이트
            self.draw_interface()
            cv2.imshow(window_name, self.display)
            
            # 키 입력 처리
            key = cv2.waitKey(1) & 0xFF
            
            if key == 13:  # Enter
                self.add_seat()
                
            elif key == ord('d') or key == ord('D'):
                self.delete_last_seat()
                
            elif key == ord('r') or key == ord('R'):
                self.refresh_screen()
                
            elif key == ord('s') or key == ord('S'):
                if self.save_and_exit():
                    break
                
            elif key == 27:  # ESC
                print("❌ 저장하지 않고 종료")
                break
        
        cv2.destroyAllWindows()


def main():
    """메인 함수"""
    # ViewGuardCapture 초기화
    capture = ViewGuardCapture()
    
    # ROI Manager 실행
    manager = ROIManager(capture)
    manager.run()


if __name__ == "__main__":
    main()
