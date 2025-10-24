"""
다중 알림 시스템
- 텔레그램 그룹/개별 알림
- 구글 스프레드시트 자동 기록
- 웹훅 지원 (n8n 연동)
"""
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from typing import List, Optional, Dict
import json
import os
from datetime import datetime
import requests


class MultiAlert:
    """다중 채널 알림 시스템"""
    
    def __init__(self, config_path: str = 'config/settings.json'):
        """초기화"""
        self.config = self.load_config(config_path)
        
        # 텔레그램 설정
        self.telegram_config = self.config.get('telegram', {})
        self.telegram_enabled = False
        self.bots = {}
        
        # 구글 시트 설정
        self.gsheet_config = self.config.get('google_sheets', {})
        self.gsheet_enabled = self.gsheet_config.get('enabled', False)
        
        # 웹훅 설정
        self.webhook_config = self.config.get('webhook', {})
        self.webhook_enabled = self.webhook_config.get('enabled', False)
        
        # 초기화
        self.init_telegram()
        self.init_google_sheets()
        
        print("📱 다중 알림 시스템 초기화")
        print(f"   - 텔레그램: {'✅' if self.telegram_enabled else '❌'}")
        print(f"   - 구글 시트: {'✅' if self.gsheet_enabled else '❌'}")
        print(f"   - 웹훅: {'✅' if self.webhook_enabled else '❌'}")
    
    def load_config(self, config_path: str) -> dict:
        """설정 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def init_telegram(self):
        """텔레그램 초기화"""
        bot_token = self.telegram_config.get('bot_token')
        
        if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
            return
        
        try:
            self.bot = Bot(token=bot_token)
            self.telegram_enabled = True
            print("✅ 텔레그램 봇 연결 성공")
        except Exception as e:
            print(f"⚠️  텔레그램 봇 초기화 실패: {e}")
    
    def init_google_sheets(self):
        """구글 시트 초기화"""
        if not self.gsheet_enabled:
            return
        
        try:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            
            creds_file = self.gsheet_config.get('credentials_file')
            sheet_name = self.gsheet_config.get('sheet_name', '독서실_졸음_기록')
            
            if not creds_file or not os.path.exists(creds_file):
                print("⚠️  구글 시트 인증 파일이 없습니다")
                self.gsheet_enabled = False
                return
            
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                creds_file, scope
            )
            
            self.gsheet_client = gspread.authorize(creds)
            self.sheet = self.gsheet_client.open(sheet_name).sheet1
            
            print(f"✅ 구글 시트 연결 성공: {sheet_name}")
        except ImportError:
            print("⚠️  gspread 패키지를 설치하세요: pip install gspread oauth2client")
            self.gsheet_enabled = False
        except Exception as e:
            print(f"⚠️  구글 시트 초기화 실패: {e}")
            self.gsheet_enabled = False
    
    def get_telegram_targets(self) -> List[str]:
        """텔레그램 전송 대상 목록"""
        alert_to = self.telegram_config.get('alert_to', 'group')
        chat_ids = self.telegram_config.get('chat_ids', {})
        
        if alert_to == 'all':
            # 모든 개별 사용자에게 전송
            return [v for k, v in chat_ids.items() if k != 'group']
        elif alert_to == 'group':
            # 그룹에만 전송
            group_id = chat_ids.get('group')
            return [group_id] if group_id else []
        elif alert_to == 'admin':
            # 관리자에게만
            admin_id = chat_ids.get('admin')
            return [admin_id] if admin_id else []
        else:
            # 특정 대상
            target_id = chat_ids.get(alert_to)
            return [target_id] if target_id else []
    
    async def send_telegram_async(self, message: str, targets: List[str]) -> int:
        """텔레그램 비동기 전송"""
        success_count = 0
        
        for chat_id in targets:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                success_count += 1
            except TelegramError as e:
                print(f"❌ 텔레그램 전송 실패 ({chat_id}): {e}")
        
        return success_count
    
    def send_telegram(self, message: str) -> bool:
        """텔레그램 전송 (동기)"""
        if not self.telegram_enabled:
            return False
        
        targets = self.get_telegram_targets()
        
        if not targets:
            print("⚠️  텔레그램 전송 대상이 없습니다")
            return False
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success_count = loop.run_until_complete(
                self.send_telegram_async(message, targets)
            )
            loop.close()
            
            print(f"✅ 텔레그램 전송 완료 ({success_count}/{len(targets)})")
            return success_count > 0
        except Exception as e:
            print(f"❌ 텔레그램 전송 실패: {e}")
            return False
    
    def log_to_google_sheets(self, channel: str, confidence: float, 
                            details: dict) -> bool:
        """구글 시트에 기록"""
        if not self.gsheet_enabled:
            return False
        
        try:
            now = datetime.now()
            
            row = [
                now.strftime('%Y-%m-%d %H:%M:%S'),  # 시간
                channel,                              # 채널
                f"{confidence:.1%}",                  # 신뢰도
                f"{details.get('ear', 0):.3f}",      # EAR
                f"{details.get('head_tilt', 0):.3f}", # Head Tilt
                "조는중",                             # 상태
                "발송"                                # 알림여부
            ]
            
            self.sheet.append_row(row)
            print(f"✅ 구글 시트 기록 완료: {channel}")
            return True
        except Exception as e:
            print(f"❌ 구글 시트 기록 실패: {e}")
            return False
    
    def send_webhook(self, data: dict) -> bool:
        """웹훅 전송 (n8n 등)"""
        if not self.webhook_enabled:
            return False
        
        url = self.webhook_config.get('url')
        
        if not url:
            return False
        
        try:
            response = requests.post(
                url,
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ 웹훅 전송 완료")
                return True
            else:
                print(f"⚠️  웹훅 응답 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 웹훅 전송 실패: {e}")
            return False
    
    def send_drowsy_alert(self, channel: str, confidence: float, 
                         details: dict) -> Dict[str, bool]:
        """
        졸음 알림 전송 (모든 채널)
        
        Returns:
            각 채널별 성공 여부
        """
        results = {}
        now = datetime.now()
        
        # 메시지 생성
        message = f"""
🚨 *졸음 알림* 🚨

📍 좌석: {channel}
⏰ 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}
📊 신뢰도: {confidence:.1%}

*상세정보:*
• 눈 감김(EAR): {details.get('ear', 0):.3f}
• 고개 각도: {details.get('head_tilt', 0):.3f}
• 눈 상태: {'감음 😴' if details.get('eyes_closed') else '뜸 👀'}
• 고개 상태: {'숙임 😴' if details.get('head_down') else '정상 ✅'}
        """
        
        # 1. 텔레그램
        results['telegram'] = self.send_telegram(message.strip())
        
        # 2. 구글 시트
        results['google_sheets'] = self.log_to_google_sheets(
            channel, confidence, details
        )
        
        # 3. 웹훅 (n8n 등)
        webhook_data = {
            'type': 'drowsy_alert',
            'channel': channel,
            'confidence': confidence,
            'timestamp': now.isoformat(),
            'details': details
        }
        results['webhook'] = self.send_webhook(webhook_data)
        
        return results
    
    def send_system_message(self, message: str) -> bool:
        """시스템 메시지 전송 (텔레그램만)"""
        if not self.telegram_enabled:
            print(f"📱 [시스템] {message}")
            return False
        
        formatted = f"🤖 *시스템 알림*\n\n{message}"
        return self.send_telegram(formatted)
    
    def test_all_channels(self) -> Dict[str, bool]:
        """모든 알림 채널 테스트"""
        print("\n" + "=" * 60)
        print("🧪 알림 시스템 테스트")
        print("=" * 60)
        
        results = {}
        
        # 텔레그램 테스트
        if self.telegram_enabled:
            test_msg = f"✅ 텔레그램 연결 테스트\n시간: {datetime.now().strftime('%H:%M:%S')}"
            results['telegram'] = self.send_telegram(test_msg)
        
        # 구글 시트 테스트
        if self.gsheet_enabled:
            test_data = {
                'ear': 0.180,
                'head_tilt': 0.620,
                'eyes_closed': True,
                'head_down': True
            }
            results['google_sheets'] = self.log_to_google_sheets(
                "TEST", 0.95, test_data
            )
        
        # 웹훅 테스트
        if self.webhook_enabled:
            test_data = {
                'type': 'test',
                'message': 'Webhook connection test',
                'timestamp': datetime.now().isoformat()
            }
            results['webhook'] = self.send_webhook(test_data)
        
        print("\n테스트 결과:")
        for channel, success in results.items():
            status = "✅ 성공" if success else "❌ 실패"
            print(f"  {channel}: {status}")
        
        print("=" * 60)
        
        return results


# 사용 예시
if __name__ == "__main__":
    alert = MultiAlert()
    
    # 테스트
    alert.test_all_channels()
