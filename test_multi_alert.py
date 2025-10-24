"""
다중 알림 시스템 테스트
"""
import sys
sys.path.append('src')

from alert_system_multi import MultiAlert
from datetime import datetime


def test_telegram_group():
    """텔레그램 그룹 테스트"""
    print("\n" + "=" * 60)
    print("📱 텔레그램 그룹 알림 테스트")
    print("=" * 60)
    
    alert = MultiAlert()
    
    if not alert.telegram_enabled:
        print("❌ 텔레그램이 설정되지 않았습니다")
        print("   config/settings.json에서 텔레그램 설정을 완료하세요")
        return
    
    # 테스트 메시지
    test_msg = f"""
✅ *텔레그램 연결 테스트*

시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

이 메시지를 받았다면 설정이 올바릅니다!
관리자와 담당자 모두 확인하세요.
    """
    
    result = alert.send_telegram(test_msg.strip())
    
    if result:
        print("✅ 텔레그램 전송 성공!")
        print("   그룹/개인 채팅에서 메시지를 확인하세요")
    else:
        print("❌ 텔레그램 전송 실패")
        print("   설정을 다시 확인하세요")


def test_google_sheets():
    """구글 시트 테스트"""
    print("\n" + "=" * 60)
    print("📊 구글 스프레드시트 테스트")
    print("=" * 60)
    
    alert = MultiAlert()
    
    if not alert.gsheet_enabled:
        print("❌ 구글 시트가 설정되지 않았습니다")
        print("   MULTI_ALERT_GUIDE.md를 참고하여 설정하세요")
        return
    
    # 테스트 데이터
    test_data = {
        'ear': 0.180,
        'head_tilt': 0.620,
        'eyes_closed': True,
        'head_down': True
    }
    
    result = alert.log_to_google_sheets("TEST", 0.95, test_data)
    
    if result:
        print("✅ 구글 시트 기록 성공!")
        print(f"   시트 이름: {alert.gsheet_config.get('sheet_name')}")
        print("   스프레드시트에서 확인하세요")
    else:
        print("❌ 구글 시트 기록 실패")


def test_drowsy_alert():
    """실제 졸음 알림 테스트"""
    print("\n" + "=" * 60)
    print("🚨 실제 졸음 알림 테스트")
    print("=" * 60)
    
    alert = MultiAlert()
    
    # 실제 졸음 데이터 시뮬레이션
    test_data = {
        'ear': 0.182,
        'head_tilt': 0.612,
        'eyes_closed': True,
        'head_down': True
    }
    
    print("테스트 알림을 전송합니다...")
    results = alert.send_drowsy_alert("CH03", 0.85, test_data)
    
    print("\n결과:")
    for channel, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {channel}: {status}")


def test_all():
    """전체 시스템 테스트"""
    print("\n" + "=" * 70)
    print("🧪 ViewGuard 다중 알림 시스템 전체 테스트")
    print("=" * 70)
    
    alert = MultiAlert()
    results = alert.test_all_channels()
    
    print("\n📊 테스트 요약:")
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"   성공: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n✅ 모든 알림 채널이 정상 작동합니다!")
    elif success_count > 0:
        print("\n⚠️  일부 알림 채널만 작동합니다")
    else:
        print("\n❌ 알림 채널 설정이 필요합니다")


def interactive_test():
    """대화형 테스트"""
    print("\n" + "=" * 60)
    print("🎯 ViewGuard 다중 알림 테스트")
    print("=" * 60)
    print()
    print("1. 텔레그램 그룹 테스트")
    print("2. 구글 시트 테스트")
    print("3. 실제 졸음 알림 테스트")
    print("4. 전체 시스템 테스트")
    print("5. 종료")
    print()
    
    choice = input("선택 (1-5): ")
    
    if choice == "1":
        test_telegram_group()
    elif choice == "2":
        test_google_sheets()
    elif choice == "3":
        test_drowsy_alert()
    elif choice == "4":
        test_all()
    else:
        print("종료")


if __name__ == "__main__":
    interactive_test()
