"""
ViewGuard Student Monitor - 순차 채널 전환 방식
16개 채널을 하나씩 고화질로 캡처하여 분석
"""
import cv2
import numpy as np
import time
import json
import os
import sys
sys.path.append('src')

from datetime import datetime, timedelta
from typing import Dict, Optional

from advanced_detector import AdvancedDrowsinessDetector
from channel_controller import ChannelController
from alert_system import TelegramAlert, ConsoleAlert


class SequentialStudentMonitor:
    """순차 채널 전환 방식 모니터링 시스템"""
    
    def __init__(self, config_path: str = 'config/settings.json'):
        """
        초기화
        Args:
            config_path: 설정 파일 경로
        """
        print("=" * 70)
        print("🎯 ViewGuard Monitor - 순차 채널 전환 방식 (고화질)")
        print("=" * 70)
        
        # 설정 로드
        self.config = self.load_config(config_path)
        detection_config = self.config.get('detection', {})
        
        # 컴포넌트 초기화
        print("\n📦 컴포넌트 초기화 중...")
        
        # 채널 컨트롤러
        self.controller = ChannelController()
        
        # 졸음 감지기
        self.detector = AdvancedDrowsinessDetector(detection_config)
        
        # 알림 시스템
        self.alert = TelegramAlert(config_path)
        if not self.alert.enabled:
            self.alert = ConsoleAlert()
            print("📱 콘솔 알림 모드")
        
        # 좌석별 상태 (채널 = 좌석)
        self.channel_states: Dict[int, Dict] = {}
        
        # 설정값
        self.CONFIDENCE_THRESHOLD = detection_config.get('confidence_threshold', 0.75)
        self.DROWSY_THRESHOLD = detection_config.get('drowsy_count_threshold', 5)
        self.CHECK_INTERVAL = detection_config.get('check_interval', 2)
        self.ALERT_COOLDOWN = detection_config.get('alert_cooldown', 300)
        
        # 순차 캡처 설정
        self.FULL_CYCLE_INTERVAL = 60  # 전체 사이클 주기 (초) - 16개 채널 순회
        
        # 통계
        self.stats = {
            'total_cycles': 0,
            'total_checks': 0,
            'drowsy_detections': 0,
            'alerts_sent': 0,
            'start_time': datetime.now()
        }
        
        print(f"✅ 초기화 완료!")
        print(f"\n📊 설정:")
        print(f"   - 신뢰도 임계값: {self.CONFIDENCE_THRESHOLD*100}%")
        print(f"   - 연속 감지 횟수: {self.DROWSY_THRESHOLD}회")
        print(f"   - 전체 사이클 주기: {self.FULL_CYCLE_INTERVAL}초")
        print(f"   - 알림 쿨다운: {self.ALERT_COOLDOWN}초")
        print(f"📺 활성 채널: {self.controller.total_channels}개")
        print("=" * 70)
    
    def load_config(self, config_path: str) -> dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  설정 파일 로드 실패, 기본값 사용: {e}")
            return {}
    
    def initialize_channel_state(self, channel_num: int) -> Dict:
        """채널 상태 초기화"""
        return {
            'drowsy_count': 0,
            'last_alert_time': None,
            'has_person': False,
            'history': [],
            'total_checks': 0,
            'total_drowsy': 0,
            'last_check_time': None
        }
    
    def detect_person(self, image: np.ndarray) -> bool:
        """
        이미지에 사람이 있는지 감지
        
        Args:
            image: 캡처 이미지
            
        Returns:
            사람이 있으면 True
        """
        # MediaPipe 감지 결과로 판단
        is_drowsy, confidence, details = self.detector.detect_drowsiness(image)
        
        # 얼굴이 감지되면 사람 있음
        if 'status' in details and details['status'] != 'no_face_detected':
            return True
        
        return False
    
    def process_channel(self, channel_num: int, image: np.ndarray):
        """
        개별 채널 처리
        
        Args:
            channel_num: 채널 번호
            image: 캡처된 이미지
        """
        # 상태 초기화
        if channel_num not in self.channel_states:
            self.channel_states[channel_num] = self.initialize_channel_state(channel_num)
        
        state = self.channel_states[channel_num]
        state['total_checks'] += 1
        state['last_check_time'] = datetime.now()
        
        # 졸음 감지
        is_drowsy, confidence, details = self.detector.detect_drowsiness(image)
        
        # 사람 없음
        if 'status' in details and details['status'] == 'no_face_detected':
            state['has_person'] = False
            state['drowsy_count'] = 0
            return
        
        state['has_person'] = True
        
        # 히스토리 업데이트
        state['history'].append({
            'timestamp': datetime.now(),
            'drowsy': is_drowsy,
            'confidence': confidence,
            'details': details
        })
        
        if len(state['history']) > 10:
            state['history'].pop(0)
        
        # 신뢰도 높은 경우만 처리
        if is_drowsy and confidence >= self.CONFIDENCE_THRESHOLD:
            state['drowsy_count'] += 1
            state['total_drowsy'] += 1
            self.stats['drowsy_detections'] += 1
            
            print(f"💤 [CH{channel_num:02d}] 졸음 감지! "
                  f"(카운트: {state['drowsy_count']}/{self.DROWSY_THRESHOLD}, "
                  f"신뢰도: {confidence:.1%}, "
                  f"EAR: {details['ear']:.3f}, "
                  f"Tilt: {details['head_tilt']:.3f})")
            
            # 연속 감지 임계값 도달 시 알림
            if state['drowsy_count'] >= self.DROWSY_THRESHOLD:
                if self.should_send_alert(channel_num):
                    self.send_alert(channel_num, confidence, details)
                    state['drowsy_count'] = 0
        else:
            # 정상 상태면 카운터 점진적 감소
            if state['drowsy_count'] > 0:
                state['drowsy_count'] -= 1
    
    def should_send_alert(self, channel_num: int) -> bool:
        """알림을 보내야 하는지 확인"""
        state = self.channel_states[channel_num]
        last_alert = state['last_alert_time']
        
        if last_alert is None:
            return True
        
        elapsed = (datetime.now() - last_alert).seconds
        return elapsed >= self.ALERT_COOLDOWN
    
    def send_alert(self, channel_num: int, confidence: float, details: dict):
        """알림 발송"""
        success = self.alert.send_drowsy_alert(f"CH{channel_num:02d}", confidence, details)
        
        if success:
            self.channel_states[channel_num]['last_alert_time'] = datetime.now()
            self.stats['alerts_sent'] += 1
            print(f"✅ [CH{channel_num:02d}] 알림 발송 완료")
    
    def run_single_cycle(self, debug_mode: bool = False):
        """
        한 번의 전체 사이클 실행 (16개 채널 순회)
        
        Args:
            debug_mode: True면 화면 표시
            
        Returns:
            성공 여부
        """
        print("\n" + "=" * 70)
        print(f"🔄 사이클 #{self.stats['total_cycles'] + 1} 시작")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        cycle_start_time = time.time()
        
        for ch_num in range(1, self.controller.total_channels + 1):
            try:
                # 채널 전환
                print(f"\n[{ch_num}/16] CH{ch_num:02d} 처리 중...")
                
                if not self.controller.switch_to_channel(ch_num):
                    print(f"⚠️  CH{ch_num:02d} 전환 실패")
                    continue
                
                # 화면 캡처
                image = self.controller.capture_current_channel()
                
                if image is None:
                    print(f"⚠️  CH{ch_num:02d} 캡처 실패")
                    continue
                
                h, w = image.shape[:2]
                print(f"📸 캡처 완료 ({w}x{h})")
                
                # 졸음 분석
                self.process_channel(ch_num, image)
                self.stats['total_checks'] += 1
                
                # 디버그 모드: 화면 표시
                if debug_mode:
                    # 감지 결과 그리기
                    is_drowsy, confidence, details = self.detector.detect_drowsiness(image)
                    debug_img = self.detector.draw_debug_info(image, details)
                    
                    # 채널 정보 추가
                    cv2.putText(debug_img, f"CH {ch_num:02d}", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
                    
                    # 화면 크기 조정
                    if w > 1280:
                        scale = 1280 / w
                        new_w = 1280
                        new_h = int(h * scale)
                        debug_img = cv2.resize(debug_img, (new_w, new_h))
                    
                    cv2.imshow('Sequential Monitor Debug', debug_img)
                    
                    key = cv2.waitKey(100) & 0xFF
                    if key == 27:  # ESC
                        print("\n사용자 종료")
                        return False
            
            except Exception as e:
                print(f"❌ CH{ch_num:02d} 처리 중 오류: {e}")
                continue
        
        # 사이클 완료
        cycle_time = time.time() - cycle_start_time
        self.stats['total_cycles'] += 1
        
        print("\n" + "=" * 70)
        print(f"✅ 사이클 #{self.stats['total_cycles']} 완료")
        print(f"⏱️  소요 시간: {cycle_time:.1f}초")
        print(f"📊 이번 사이클: 체크 {self.controller.total_channels}회, "
              f"졸음 감지 {sum(1 for s in self.channel_states.values() if s.get('drowsy_count', 0) > 0)}건")
        print("=" * 70)
        
        return True
    
    def print_statistics(self):
        """통계 출력"""
        elapsed = datetime.now() - self.stats['start_time']
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60
        
        print("\n" + "=" * 70)
        print("📊 모니터링 통계")
        print("=" * 70)
        print(f"⏱️  실행 시간: {hours}시간 {minutes}분")
        print(f"🔄 완료된 사이클: {self.stats['total_cycles']}회")
        print(f"🔍 총 체크: {self.stats['total_checks']}회")
        print(f"💤 졸음 감지: {self.stats['drowsy_detections']}회")
        print(f"🚨 알림 발송: {self.stats['alerts_sent']}회")
        print()
        
        # 채널별 통계
        print("채널별 상태:")
        for ch_num in range(1, self.controller.total_channels + 1):
            if ch_num not in self.channel_states:
                continue
            
            state = self.channel_states[ch_num]
            status = "👤 사용중" if state['has_person'] else "⚪ 비어있음"
            drowsy_rate = 0
            if state['total_checks'] > 0:
                drowsy_rate = (state['total_drowsy'] / state['total_checks']) * 100
            
            print(f"  CH{ch_num:02d}: {status} | "
                  f"체크: {state['total_checks']}회 | "
                  f"졸음: {state['total_drowsy']}회 ({drowsy_rate:.1f}%)")
        
        print("=" * 70 + "\n")
    
    def run(self, debug_mode: bool = False):
        """
        메인 모니터링 루프
        
        Args:
            debug_mode: True면 화면 표시
        """
        print("\n🚀 순차 모니터링 시작!")
        print(f"   - 전체 사이클 주기: 약 {self.FULL_CYCLE_INTERVAL}초")
        print(f"   - Ctrl+C로 종료")
        print()
        
        # 채널 버튼 설정 확인
        if not self.controller.channel_buttons:
            print("❌ 채널 버튼이 설정되지 않았습니다!")
            print("   먼저 channel_setup.py를 실행하여 채널 버튼을 설정하세요.")
            return
        
        last_stats_time = datetime.now()
        
        try:
            while True:
                # 한 사이클 실행
                if not self.run_single_cycle(debug_mode):
                    break
                
                # 주기적 통계 (10분마다)
                if (datetime.now() - last_stats_time).seconds >= 600:
                    self.print_statistics()
                    last_stats_time = datetime.now()
                
                # 다음 사이클까지 대기
                # (사이클 소요 시간을 고려하여 조정)
                print(f"\n⏸️  다음 사이클까지 대기 중...\n")
                time.sleep(max(5, self.FULL_CYCLE_INTERVAL / 16))  # 최소 5초
        
        except KeyboardInterrupt:
            print("\n\n⏹️  모니터링 종료")
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 최종 통계
            self.print_statistics()
            
            if debug_mode:
                cv2.destroyAllWindows()
            
            print("✅ 시스템 종료")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ViewGuard Sequential Monitor - 순차 채널 전환 방식'
    )
    parser.add_argument('--debug', action='store_true',
                       help='디버그 모드 (화면 표시)')
    parser.add_argument('--config', type=str,
                       default='config/settings.json',
                       help='설정 파일 경로')
    
    args = parser.parse_args()
    
    # 모니터 실행
    monitor = SequentialStudentMonitor(args.config)
    monitor.run(debug_mode=args.debug)


if __name__ == "__main__":
    main()
