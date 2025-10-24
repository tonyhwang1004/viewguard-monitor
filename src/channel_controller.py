"""
뷰가드웹 채널 자동 전환 컨트롤러
하단 번호 클릭으로 채널을 순차 전환하여 고화질 캡처
"""
import pyautogui
import time
import json
import os
from typing import List, Tuple, Optional, Dict
import cv2
import numpy as np
from PIL import ImageGrab


class ChannelController:
    """채널 자동 전환 컨트롤러"""
    
    def __init__(self, config_path: str = 'config/channel_positions.json'):
        """
        초기화
        Args:
            config_path: 채널 버튼 위치 설정 파일
        """
        self.config_path = config_path
        self.channel_buttons = {}  # 채널 버튼 위치 {1: (x, y), 2: (x, y), ...}
        self.current_channel = 1
        self.total_channels = 16
        
        # 화면 안정화 대기 시간
        self.SWITCH_DELAY = 1.2  # 채널 전환 후 대기 (초)
        self.CAPTURE_DELAY = 0.3  # 캡처 전 추가 대기 (초)
        
        # 캡처 영역 (전체 화면 또는 특정 영역)
        self.capture_region = None  # None이면 전체 화면
        
        # PyAutoGUI 설정
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True  # 마우스를 모서리로 이동하면 중단
        
        # 설정 로드
        self.load_config()
        
        print("🎮 채널 컨트롤러 초기화 완료")
        
    def load_config(self) -> bool:
        """저장된 설정 로드"""
        if not os.path.exists(self.config_path):
            print("⚠️  채널 버튼 위치가 설정되지 않았습니다")
            print("   channel_setup.py를 먼저 실행하세요")
            return False
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.channel_buttons = data.get('buttons', {})
                self.total_channels = data.get('total_channels', 16)
                self.capture_region = data.get('capture_region')
                
                if self.channel_buttons:
                    print(f"✅ 채널 버튼 {len(self.channel_buttons)}개 로드됨")
                    return True
                else:
                    print("⚠️  채널 버튼 정보가 비어있습니다")
                    return False
        except Exception as e:
            print(f"❌ 설정 로드 실패: {e}")
            return False
    
    def save_config(self) -> bool:
        """설정 저장"""
        try:
            data = {
                'buttons': self.channel_buttons,
                'total_channels': self.total_channels,
                'capture_region': self.capture_region,
                'comment': '채널 버튼 위치 및 캡처 영역 설정'
            }
            
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 설정 저장 완료: {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")
            return False
    
    def switch_to_channel(self, channel_num: int) -> bool:
        """
        특정 채널로 전환
        
        Args:
            channel_num: 채널 번호 (1-16)
            
        Returns:
            성공 여부
        """
        if channel_num < 1 or channel_num > self.total_channels:
            print(f"❌ 잘못된 채널 번호: {channel_num}")
            return False
        
        channel_key = str(channel_num)
        
        if channel_key not in self.channel_buttons:
            print(f"❌ 채널 {channel_num} 버튼 위치가 설정되지 않음")
            return False
        
        try:
            # 버튼 위치 가져오기
            x, y = self.channel_buttons[channel_key]
            
            # 클릭
            pyautogui.click(x, y)
            
            # 화면 전환 대기
            time.sleep(self.SWITCH_DELAY)
            
            self.current_channel = channel_num
            print(f"✅ CH{channel_num:02d}로 전환 완료")
            
            return True
        except Exception as e:
            print(f"❌ 채널 전환 실패: {e}")
            return False
    
    def capture_current_channel(self) -> Optional[np.ndarray]:
        """
        현재 채널 화면 캡처 (고화질)
        
        Returns:
            캡처된 이미지 (BGR) 또는 None
        """
        try:
            # 안정화 대기
            time.sleep(self.CAPTURE_DELAY)
            
            # 화면 캡처
            if self.capture_region:
                x, y, w, h = self.capture_region
                screen = ImageGrab.grab(bbox=(x, y, x+w, y+h))
            else:
                screen = ImageGrab.grab()
            
            # OpenCV 포맷으로 변환
            screen_np = np.array(screen)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            
            return screen_bgr
        except Exception as e:
            print(f"❌ 화면 캡처 실패: {e}")
            return None
    
    def capture_all_channels(self, progress_callback=None) -> Dict[int, np.ndarray]:
        """
        모든 채널을 순차적으로 전환하면서 캡처
        
        Args:
            progress_callback: 진행상황 콜백 함수(channel_num, total)
            
        Returns:
            {채널번호: 이미지} 딕셔너리
        """
        print("=" * 60)
        print("🎥 전체 채널 순차 캡처 시작")
        print("=" * 60)
        
        captured_images = {}
        
        for ch_num in range(1, self.total_channels + 1):
            # 진행상황 출력
            print(f"\n[{ch_num}/{self.total_channels}] CH{ch_num:02d} 캡처 중...")
            
            # 콜백 호출
            if progress_callback:
                progress_callback(ch_num, self.total_channels)
            
            # 채널 전환
            if not self.switch_to_channel(ch_num):
                print(f"⚠️  CH{ch_num:02d} 전환 실패, 건너뜀")
                continue
            
            # 화면 캡처
            image = self.capture_current_channel()
            
            if image is not None:
                captured_images[ch_num] = image
                h, w = image.shape[:2]
                print(f"✅ CH{ch_num:02d} 캡처 완료 ({w}x{h})")
            else:
                print(f"⚠️  CH{ch_num:02d} 캡처 실패")
        
        print("\n" + "=" * 60)
        print(f"✅ 캡처 완료: {len(captured_images)}/{self.total_channels}개 채널")
        print("=" * 60)
        
        return captured_images
    
    def switch_next_channel(self) -> int:
        """
        다음 채널로 전환 (순환)
        
        Returns:
            새로운 채널 번호
        """
        next_ch = self.current_channel + 1
        if next_ch > self.total_channels:
            next_ch = 1
        
        self.switch_to_channel(next_ch)
        return next_ch
    
    def switch_previous_channel(self) -> int:
        """
        이전 채널로 전환 (순환)
        
        Returns:
            새로운 채널 번호
        """
        prev_ch = self.current_channel - 1
        if prev_ch < 1:
            prev_ch = self.total_channels
        
        self.switch_to_channel(prev_ch)
        return prev_ch
    
    def get_channel_label(self, image: np.ndarray) -> Optional[str]:
        """
        이미지에서 채널 라벨 추출 (OCR 또는 위치 기반)
        예: "CH 01", "CH 02" 등
        
        Args:
            image: 캡처된 이미지
            
        Returns:
            채널 라벨 문자열 또는 None
        """
        # 간단한 방법: 왼쪽 상단 고정 위치에서 추출
        # 실제로는 pytesseract 등으로 OCR 가능
        try:
            # 왼쪽 상단 영역 (예: 0-150, 0-50)
            label_region = image[0:50, 0:150]
            
            # 여기서는 간단히 None 반환
            # 실제 구현시 OCR 추가 가능
            return None
        except:
            return None
