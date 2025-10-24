"""
텔레그램 알림 시스템
"""
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from typing import Optional
import json
import os
from datetime import datetime


class TelegramAlert:
    """텔레그램 알림 발송"""
    
    def __init__(self, config_path: str = 'config/settings.json'):
        """
        초기화
        Args:
            config_path: 설정 파일 경로
        """
        self.config = self.load_config(config_path)
        
        self.bot_token = self.config.get('bot_token')
        self.chat_id = self.config.get('chat_id')
        
        self.bot = None
        self.enabled = False
        
        if self.bot_token and self.chat_id:
            if self.bot_token != "YOUR_BOT_TOKEN_HERE" and self.chat_id != "YOUR_CHAT_ID_HERE":
                try:
                    self.bot = Bot(token=self.bot_token)
                    self.enabled = True
                    print("✅ 텔레그램 알림 활성화")
                except Exception as e:
                    print(f"⚠️  텔레그램 봇 초기화 실패: {e}")
            else:
                print("⚠️  텔레그램 설정이 필요합니다 (config/settings.json)")
        else:
            print("⚠️  텔레그램 알림 비활성화")
    
    def load_config(self, config_path: str) -> dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('telegram', {})
        except Exception as e:
            print(f"⚠️  설정 파일 로드 실패: {e}")
            return {}
    
    def send(self, message: str, parse_mode: str = None) -> bool:
        """
        메시지 전송 (동기 방식)
        
        Args:
            message: 전송할 메시지
            parse_mode: 'Markdown' 또는 'HTML'
            
        Returns:
            성공 여부
        """
        if not self.enabled:
            print(f"📱 [알림] {message}")
            return False
        
        try:
            # 비동기 함수를 동기적으로 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._send_async(message, parse_mode)
            )
            loop.close()
            return result
        except Exception as e:
            print(f"❌ 알림 전송 실패: {e}")
            return False
    
    async def _send_async(self, message: str, parse_mode: str = None) -> bool:
        """비동기 메시지 전송"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            print(f"✅ 텔레그램 알림 전송 완료")
            return True
        except TelegramError as e:
            print(f"❌ 텔레그램 오류: {e}")
            return False
    
    def send_drowsy_alert(self, seat_id: str, confidence: float, details: dict) -> bool:
        """
        졸음 알림 전송
        
        Args:
            seat_id: 좌석 ID
            confidence: 신뢰도
            details: 상세 정보
            
        Returns:
            성공 여부
        """
        now = datetime.now()
        
        message = f"""
🚨 *졸음 알림* 🚨

📍 좌석: {seat_id}
⏰ 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}
📊 신뢰도: {confidence:.1%}

*상세정보:*
• 눈 감김(EAR): {details.get('ear', 0):.3f}
• 고개 각도: {details.get('head_tilt', 0):.3f}
• 눈 상태: {'감음 😴' if details.get('eyes_closed') else '뜸 👀'}
• 고개 상태: {'숙임 😴' if details.get('head_down') else '정상 ✅'}
        """
        
        return self.send(message.strip(), parse_mode='Markdown')
    
    def send_system_message(self, message: str) -> bool:
        """시스템 메시지 전송"""
        formatted = f"🤖 *시스템 알림*\n\n{message}"
        return self.send(formatted, parse_mode='Markdown')
    
    def test_connection(self) -> bool:
        """연결 테스트"""
        if not self.enabled:
            print("❌ 텔레그램이 활성화되지 않았습니다")
            return False
        
        test_message = f"✅ 텔레그램 연결 테스트 성공!\n시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self.send_system_message(test_message)


class ConsoleAlert:
    """콘솔 출력 알림 (텔레그램 없을 때)"""
    
    def send(self, message: str) -> bool:
        """콘솔에 메시지 출력"""
        print("=" * 60)
        print(message)
        print("=" * 60)
        return True
    
    def send_drowsy_alert(self, seat_id: str, confidence: float, details: dict) -> bool:
        """졸음 알림 출력"""
        now = datetime.now()
        
        message = f"""
🚨 졸음 알림 🚨
📍 좌석: {seat_id}
⏰ 시간: {now.strftime('%H:%M:%S')}
📊 신뢰도: {confidence:.1%}

상세정보:
• EAR: {details.get('ear', 0):.3f}
• Head Tilt: {details.get('head_tilt', 0):.3f}
• Eyes: {'CLOSED' if details.get('eyes_closed') else 'OPEN'}
• Head: {'DOWN' if details.get('head_down') else 'UP'}
        """
        
        return self.send(message.strip())
