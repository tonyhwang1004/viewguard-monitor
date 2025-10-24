"""
GitHub 알림 시스템 테스트
"""
import sys
sys.path.append('src')

from alert_system_github import GitHubAlert
from datetime import datetime


def test_connection():
    """GitHub 연결 테스트"""
    print("\n" + "=" * 60)
    print("🔗 GitHub 연결 테스트")
    print("=" * 60)
    
    alert = GitHubAlert()
    
    if alert.test_connection():
        print("\n✅ 성공! GitHub와 연결되었습니다")
        print(f"   Repo: {alert.repo_owner}/{alert.repo_name}")
        print(f"   URL: https://github.com/{alert.repo_owner}/{alert.repo_name}")
        return True
    else:
        print("\n❌ 실패! 설정을 확인하세요")
        print("\n설정 방법:")
        print("1. GitHub Personal Access Token 생성")
        print("2. config/settings.json 수정:")
        print('   {')
        print('     "github": {')
        print('       "enabled": true,')
        print('       "token": "YOUR_GITHUB_TOKEN",')
        print('       "repo_owner": "YOUR_USERNAME",')
        print('       "repo_name": "viewguard-monitor"')
        print('     }')
        print('   }')
        return False


def test_create_issue():
    """Issue 생성 테스트"""
    print("\n" + "=" * 60)
    print("📝 Issue 생성 테스트")
    print("=" * 60)
    
    alert = GitHubAlert()
    
    if not alert.enabled:
        print("❌ GitHub 설정이 필요합니다")
        return False
    
    # 테스트 졸음 알림
    test_details = {
        'ear': 0.182,
        'head_tilt': 0.612,
        'eyes_closed': True,
        'head_down': True
    }
    
    print("\n테스트 Issue를 생성합니다...")
    issue_url = alert.send_drowsy_alert("TEST-CH01", 0.85, test_details)
    
    if issue_url:
        print(f"\n✅ 성공! Issue가 생성되었습니다")
        print(f"   URL: {issue_url}")
        print("\n이제 GitHub에서 확인하세요:")
        print(f"   https://github.com/{alert.repo_owner}/{alert.repo_name}/issues")
        return True
    else:
        print("\n❌ Issue 생성 실패")
        return False


def test_today_issues():
    """오늘 생성된 Issue 조회"""
    print("\n" + "=" * 60)
    print("📋 오늘의 Issue 조회")
    print("=" * 60)
    
    alert = GitHubAlert()
    
    if not alert.enabled:
        print("❌ GitHub 설정이 필요합니다")
        return
    
    issues = alert.get_today_issues()
    
    print(f"\n오늘 생성된 졸음 알림: {len(issues)}개")
    
    if issues:
        print("\n최근 5개:")
        for i, issue in enumerate(issues[:5], 1):
            print(f"\n{i}. {issue['title']}")
            print(f"   URL: {issue['html_url']}")
            print(f"   상태: {'열림' if issue['state'] == 'open' else '닫힘'}")
            print(f"   생성: {issue['created_at']}")


def test_daily_summary():
    """일일 리포트 테스트"""
    print("\n" + "=" * 60)
    print("📊 일일 리포트 테스트")
    print("=" * 60)
    
    alert = GitHubAlert()
    
    if not alert.enabled:
        print("❌ GitHub 설정이 필요합니다")
        return
    
    # 테스트 통계 데이터
    test_stats = {
        'total_checks': 320,
        'drowsy_detections': 45,
        'alerts_sent': 12,
        'detection_rate': 14.1,
        'channel_stats': {
            'CH01': {'checks': 20, 'drowsy': 3},
            'CH02': {'checks': 20, 'drowsy': 1},
            'CH03': {'checks': 20, 'drowsy': 5},
        },
        'peak_hour': '14:00-15:00',
        'peak_channel': 'CH03'
    }
    
    print("\n일일 리포트 Issue를 생성합니다...")
    issue_url = alert.send_daily_summary(test_stats)
    
    if issue_url:
        print(f"\n✅ 성공! 일일 리포트가 생성되었습니다")
        print(f"   URL: {issue_url}")
    else:
        print("\n❌ 일일 리포트 생성 실패")


def interactive_test():
    """대화형 테스트"""
    print("\n" + "=" * 70)
    print("🧪 ViewGuard GitHub 알림 테스트")
    print("=" * 70)
    print()
    print("1. GitHub 연결 테스트")
    print("2. Issue 생성 테스트 (졸음 알림)")
    print("3. 오늘의 Issue 조회")
    print("4. 일일 리포트 테스트")
    print("5. 전체 테스트")
    print("6. 종료")
    print()
    
    choice = input("선택 (1-6): ")
    
    if choice == "1":
        test_connection()
    elif choice == "2":
        if test_connection():
            test_create_issue()
    elif choice == "3":
        test_today_issues()
    elif choice == "4":
        test_daily_summary()
    elif choice == "5":
        print("\n" + "=" * 60)
        print("🚀 전체 테스트 실행")
        print("=" * 60)
        
        if test_connection():
            test_create_issue()
            test_today_issues()
            
            print("\n" + "=" * 60)
            print("✅ 모든 테스트 완료!")
            print("=" * 60)
    else:
        print("종료")


if __name__ == "__main__":
    interactive_test()
