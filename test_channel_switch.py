"""
채널 전환 테스트
설정한 채널 버튼들이 제대로 작동하는지 테스트
"""
import sys
sys.path.append('src')

import time
from channel_controller import ChannelController


def test_channel_switching():
    """채널 전환 테스트"""
    print("=" * 60)
    print("🧪 채널 전환 테스트")
    print("=" * 60)
    
    # 컨트롤러 초기화
    controller = ChannelController()
    
    if not controller.channel_buttons:
        print("❌ 채널 버튼이 설정되지 않았습니다")
        print("   먼저 channel_setup.py를 실행하세요")
        return
    
    print(f"\n✅ {len(controller.channel_buttons)}개 채널 버튼 로드됨")
    print(f"테스트 시작...\n")
    
    # 각 채널로 순차 전환
    for ch_num in range(1, controller.total_channels + 1):
        print(f"[{ch_num}/16] CH{ch_num:02d}로 전환 중...")
        
        if controller.switch_to_channel(ch_num):
            print(f"  ✅ 성공")
        else:
            print(f"  ❌ 실패")
        
        # 확인을 위한 짧은 대기
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
    print("\n채널들이 제대로 전환되었나요?")
    print("문제가 있다면 channel_setup.py를 다시 실행하세요.")


def test_cycle():
    """순환 테스트 - 1-2-3...16-1-2-3..."""
    print("=" * 60)
    print("🔄 순환 테스트 (Ctrl+C로 중지)")
    print("=" * 60)
    
    controller = ChannelController()
    
    if not controller.channel_buttons:
        print("❌ 채널 버튼이 설정되지 않았습니다")
        return
    
    print("\n채널을 무한 순환합니다...")
    print("Ctrl+C를 눌러 종료하세요\n")
    
    try:
        while True:
            for ch_num in range(1, controller.total_channels + 1):
                controller.switch_to_channel(ch_num)
                time.sleep(2)  # 2초마다 전환
    except KeyboardInterrupt:
        print("\n\n✅ 테스트 종료")


def test_specific_channel():
    """특정 채널 테스트"""
    print("=" * 60)
    print("🎯 특정 채널 테스트")
    print("=" * 60)
    
    controller = ChannelController()
    
    if not controller.channel_buttons:
        print("❌ 채널 버튼이 설정되지 않았습니다")
        return
    
    while True:
        ch = input("\n테스트할 채널 번호 (1-16, 0=종료): ")
        
        try:
            ch_num = int(ch)
            
            if ch_num == 0:
                break
            
            if ch_num < 1 or ch_num > 16:
                print("❌ 1-16 사이의 숫자를 입력하세요")
                continue
            
            print(f"\nCH{ch_num:02d}로 전환...")
            if controller.switch_to_channel(ch_num):
                print("✅ 전환 성공!")
            else:
                print("❌ 전환 실패")
        except ValueError:
            print("❌ 숫자를 입력하세요")
    
    print("✅ 테스트 종료")


def main():
    """메인 함수"""
    print("ViewGuard 채널 전환 테스트\n")
    print("1. 전체 채널 순차 테스트 (1회)")
    print("2. 순환 테스트 (무한)")
    print("3. 특정 채널 테스트")
    print("4. 종료")
    
    choice = input("\n선택: ")
    
    if choice == "1":
        test_channel_switching()
    elif choice == "2":
        test_cycle()
    elif choice == "3":
        test_specific_channel()
    else:
        print("종료")


if __name__ == "__main__":
    main()
