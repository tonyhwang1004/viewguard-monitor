"""
ViewGuard Student Monitor - 메인 시스템
고정확도 졸음 감지 및 알림
"""
import cv2
import numpy as np
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

from advanced_detector import AdvancedDrowsinessDetector
from capture import ViewGuardCapture
from alert_system import TelegramAlert, ConsoleAlert


class AccurateStudentMonitor:
    """고정확도 학생 모니터링 시스템"""
    
    def __init__(self, config_path: str = 'config/settings.json'):
        """
        초기화
        Args:
            config_path: 설정 파일 경로
        """
        print("=" * 70)
        print("🎯 ViewGuard Student Monitor - 고정확도 졸음 감지 시스템")
        print("=" * 70)
        
        # 설정 로드
        self.config = self.load_config(config_path)
        detection_config = self.config.get('detection', {})
        
        # 컴포넌트 초기화
        print("📦 컴포넌트 초기화 중...")
        self.capture = ViewGuardCapture()
        self.detector = AdvancedDrowsinessDetector(detection_config)
        
        # 알림 시스템
        self.alert = TelegramAlert(config_path)
        if not self.alert.enabled:
            self.alert = ConsoleAlert()
            print("📱 콘솔 알림 모드로 실행")
        
        # 좌석별 상태 추적
        self.seat_states: Dict[str, Dict] = {}
        
        # 설정값
        self.CONFIDENCE_THRESHOLD = detection_config.get('confidence_threshold', 0.75)
        self.DROWSY_THRESHOLD = detection_config.get('drowsy_count_threshold', 5)
        self.CHECK_INTERVAL = detection_config.get('check_interval', 2)
        self.ALERT_COOLDOWN = detection_config.get('alert_cooldown', 300)
        
        # 빈 좌석 감지 설정
        seat_config = self.config.get('seat_detection', {})
        self.BRIGHTNESS_THRESHOLD = seat_config.get('brightness_threshold', 180)
        self.EDGE_DENSITY_THRESHOLD = seat_config.get('edge_density_threshold', 0.05)
        
        # 통계
        self.stats = {
            'total_checks': 0,
            'drowsy_detections': 0,
            'alerts_sent': 0,
            'start_time': datetime.now()
        }
        
        print(f"✅ 초기화 완료!")
        print(f"📊 설정:")
        print(f"   - 신뢰도 임계값: {self.CONFIDENCE_THRESHOLD*100}%")
        print(f"   - 연속 감지 횟수: {self.DROWSY_THRESHOLD}회")
        print(f"   - 체크 주기: {self.CHECK_INTERVAL}초")
        print(f"   - 알림 쿨다운: {self.ALERT_COOLDOWN}초")
        print(f"📍 활성 좌석: {self.capture.get_seat_count()}개")
        print("=" * 70)
    
    def load_config(self, config_path: str) -> dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  설정 파일 로드 실패, 기본값 사용: {e}")
            return {}
    
    def initialize_seat_state(self, seat_id: str) -> Dict:
        """좌석 상태 초기화"""
        return {
            'drowsy_count': 0,
            'last_alert_time': None,
            'is_occupied': False,
            'history': [],  # 최근 10개 감지 결과
            'total_checks': 0,
            'total_drowsy': 0
        }
    
    def is_seat_occupied(self, roi: np.ndarray) -> bool:
        """
        빈 좌석 감지
        
        Args:
            roi: 좌석 영역 이미지
            
        Returns:
            사람이 있으면 True
        """
        # 방법 1: 밝기 기반
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        brightness = gray.mean()
        
        # 방법 2: 에지 밀도 (사람이 있으면 에지가 많음)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        
        # 두 조건 모두 만족해야 사람 있음으로 판단
        occupied = (brightness < self.BRIGHTNESS_THRESHOLD) and \
                   (edge_density > self.EDGE_DENSITY_THRESHOLD)
        
        return occupied
    
    def update_seat_history(self, seat_id: str, is_drowsy: bool, 
                           confidence: float, details: dict):
        """좌석 히스토리 업데이트"""
        state = self.seat_states[seat_id]
        
        state['history'].append({
            'timestamp': datetime.now(),
            'drowsy': is_drowsy,
            'confidence': confidence,
            'details': details
        })
        
        # 최근 10개만 유지
        if len(state['history']) > 10:
            state['history'].pop(0)
    
    def should_send_alert(self, seat_id: str) -> bool:
        """알림을 보내야 하는지 확인 (쿨다운 체크)"""
        state = self.seat_states[seat_id]
        last_alert = state['last_alert_time']
        
        if last_alert is None:
            return True
        
        elapsed = (datetime.now() - last_alert).seconds
        return elapsed >= self.ALERT_COOLDOWN
    
    def send_alert(self, seat_id: str, confidence: float, details: dict):
        """알림 발송"""
        if not self.should_send_alert(seat_id):
            return
        
        # 알림 전송
        success = self.alert.send_drowsy_alert(seat_id, confidence, details)
        
        if success:
            self.seat_states[seat_id]['last_alert_time'] = datetime.now()
            self.stats['alerts_sent'] += 1
            print(f"✅ [좌석 {seat_id}] 알림 발송 완료")
    
    def process_seat(self, seat_id: str, roi: np.ndarray):
        """
        개별 좌석 처리
        
        Args:
            seat_id: 좌석 ID
            roi: 좌석 영역 이미지
        """
        state = self.seat_states[seat_id]
        state['total_checks'] += 1
        
        # 빈 좌석 체크
        if not self.is_seat_occupied(roi):
            state['is_occupied'] = False
            state['drowsy_count'] = 0
            return
        
        state['is_occupied'] = True
        
        # 졸음 감지
        is_drowsy, confidence, details = self.detector.detect_drowsiness(roi)
        
        # 히스토리 업데이트
        self.update_seat_history(seat_id, is_drowsy, confidence, details)
        
        # 신뢰도가 충분히 높은 경우만 처리
        if is_drowsy and confidence >= self.CONFIDENCE_THRESHOLD:
            state['drowsy_count'] += 1
            state['total_drowsy'] += 1
            self.stats['drowsy_detections'] += 1
            
            print(f"💤 [좌석 {seat_id}] 졸음 감지! "
                  f"(카운트: {state['drowsy_count']}/{self.DROWSY_THRESHOLD}, "
                  f"신뢰도: {confidence:.1%}, "
                  f"EAR: {details['ear']:.3f}, "
                  f"Tilt: {details['head_tilt']:.3f})")
            
            # 연속 감지 임계값 도달 시 알림
            if state['drowsy_count'] >= self.DROWSY_THRESHOLD:
                self.send_alert(seat_id, confidence, details)
                state['drowsy_count'] = 0  # 카운터 리셋
        else:
            # 정상 상태면 카운터 점진적 감소
            if state['drowsy_count'] > 0:
                state['drowsy_count'] -= 1
    
    def print_statistics(self):
        """통계 출력"""
        elapsed = datetime.now() - self.stats['start_time']
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60
        
        print("\n" + "=" * 70)
        print("📊 모니터링 통계")
        print("=" * 70)
        print(f"⏱️  실행 시간: {hours}시간 {minutes}분")
        print(f"🔍 총 체크: {self.stats['total_checks']}회")
        print(f"💤 졸음 감지: {self.stats['drowsy_detections']}회")
        print(f"🚨 알림 발송: {self.stats['alerts_sent']}회")
        print()
        
        # 좌석별 통계
        print("좌석별 상태:")
        for seat_id, state in self.seat_states.items():
            status = "✅ 사용중" if state['is_occupied'] else "⚪ 비어있음"
            drowsy_rate = 0
            if state['total_checks'] > 0:
                drowsy_rate = (state['total_drowsy'] / state['total_checks']) * 100
            
            print(f"  좌석 {seat_id}: {status} | "
                  f"체크: {state['total_checks']}회 | "
                  f"졸음: {state['total_drowsy']}회 ({drowsy_rate:.1f}%)")
        
        print("=" * 70 + "\n")
    
    def run(self, debug_mode: bool = False):
        """
        메인 모니터링 루프
        
        Args:
            debug_mode: True면 화면 표시
        """
        print("🚀 모니터링 시작!")
        print("   Ctrl+C로 종료")
        print()
        
        # 좌석 확인
        if not self.capture.seats:
            print("❌ 좌석이 설정되지 않았습니다!")
            print("   먼저 roi_manager.py를 실행하여 좌석을 설정하세요.")
            return
        
        # 디버그 윈도우
        if debug_mode:
            cv2.namedWindow('Monitor Debug', cv2.WINDOW_NORMAL)
        
        last_stats_time = datetime.now()
        
        try:
            while True:
                loop_start = time.time()
                
                # 1. 전체 화면 캡처
                screen = self.capture.capture_screen()
                
                if screen is None:
                    print("⚠️  화면 캡처 실패, 재시도...")
                    time.sleep(5)
                    continue
                
                self.stats['total_checks'] += 1
                
                # 2. 각 좌석 처리
                for seat_id in self.capture.seats.keys():
                    # 좌석 상태 초기화
                    if seat_id not in self.seat_states:
                        self.seat_states[seat_id] = self.initialize_seat_state(seat_id)
                    
                    # ROI 추출
                    roi = self.capture.get_seat_roi(screen, seat_id)
                    
                    if roi is None:
                        continue
                    
                    # 좌석 처리
                    self.process_seat(seat_id, roi)
                
                # 3. 디버그 화면 표시
                if debug_mode:
                    # 졸음 감지된 좌석 하이라이트
                    highlight = {}
                    for seat_id, state in self.seat_states.items():
                        if state['is_occupied'] and state['drowsy_count'] > 0:
                            # 졸음 카운트에 따라 색상 변경
                            if state['drowsy_count'] >= self.DROWSY_THRESHOLD:
                                highlight[seat_id] = (0, 0, 255)  # 빨강
                            else:
                                highlight[seat_id] = (0, 165, 255)  # 주황
                    
                    debug_screen = self.capture.draw_seat_boxes(screen, highlight)
                    
                    # 화면 크기 조정
                    h, w = debug_screen.shape[:2]
                    if w > 1920:
                        scale = 1920 / w
                        new_w = 1920
                        new_h = int(h * scale)
                        debug_screen = cv2.resize(debug_screen, (new_w, new_h))
                    
                    cv2.imshow('Monitor Debug', debug_screen)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  # ESC
                        print("\n사용자 종료")
                        break
                
                # 4. 주기적 통계 출력 (5분마다)
                if (datetime.now() - last_stats_time).seconds >= 300:
                    self.print_statistics()
                    last_stats_time = datetime.now()
                
                # 5. 대기
                elapsed = time.time() - loop_start
                sleep_time = max(0, self.CHECK_INTERVAL - elapsed)
                time.sleep(sleep_time)
                
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
    
    parser = argparse.ArgumentParser(description='ViewGuard Student Monitor')
    parser.add_argument('--debug', action='store_true', 
                       help='디버그 모드 (화면 표시)')
    parser.add_argument('--config', type=str, 
                       default='config/settings.json',
                       help='설정 파일 경로')
    
    args = parser.parse_args()
    
    # 모니터 실행
    monitor = AccurateStudentMonitor(args.config)
    monitor.run(debug_mode=args.debug)


if __name__ == "__main__":
    main()
