"""
GitHub 기반 무료 클라우드 알림 시스템
- GitHub Issues: 알림 및 이력 관리
- GitHub API: 자동 Issue 생성
- 완전 무료!
"""
import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional, List
import base64


class GitHubAlert:
    """GitHub Issues 기반 알림 시스템"""
    
    def __init__(self, config_path: str = 'config/settings.json'):
        """
        초기화
        Args:
            config_path: 설정 파일 경로
        """
        self.config = self.load_config(config_path)
        self.github_config = self.config.get('github', {})
        
        # GitHub 설정
        self.token = self.github_config.get('token', '')
        self.repo_owner = self.github_config.get('repo_owner', '')
        self.repo_name = self.github_config.get('repo_name', '')
        
        # API URL
        self.api_base = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
        # 헤더
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 활성화 여부
        self.enabled = bool(self.token and self.repo_owner and self.repo_name)
        
        if self.enabled:
            print(f"✅ GitHub 알림 활성화: {self.repo_owner}/{self.repo_name}")
        else:
            print("⚠️  GitHub 설정이 필요합니다")
    
    def load_config(self, config_path: str) -> dict:
        """설정 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def create_issue(self, title: str, body: str, labels: List[str] = None) -> Optional[str]:
        """
        GitHub Issue 생성
        
        Args:
            title: Issue 제목
            body: Issue 내용
            labels: 라벨 리스트 (예: ['drowsy', 'urgent'])
            
        Returns:
            Issue URL 또는 None
        """
        if not self.enabled:
            print(f"📝 [GitHub] {title}")
            print(body)
            return None
        
        url = f"{self.api_base}/issues"
        
        data = {
            'title': title,
            'body': body,
            'labels': labels or []
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_url = issue_data['html_url']
                print(f"✅ GitHub Issue 생성: {issue_url}")
                return issue_url
            else:
                print(f"❌ GitHub Issue 생성 실패: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"❌ GitHub API 오류: {e}")
            return None
    
    def send_drowsy_alert(self, channel: str, confidence: float, details: dict) -> Optional[str]:
        """
        졸음 알림 Issue 생성
        
        Args:
            channel: 채널 번호
            confidence: 신뢰도
            details: 상세 정보
            
        Returns:
            Issue URL
        """
        now = datetime.now()
        
        # Issue 제목
        title = f"🚨 졸음 감지: {channel} ({confidence:.0%}) - {now.strftime('%m/%d %H:%M')}"
        
        # Issue 본문
        body = f"""
## 졸음 알림

### 기본 정보
- **채널**: {channel}
- **시간**: {now.strftime('%Y-%m-%d %H:%M:%S')}
- **신뢰도**: {confidence:.1%}

### 상세 분석
- **EAR (눈 감김)**: `{details.get('ear', 0):.3f}`
- **Head Tilt (고개 각도)**: `{details.get('head_tilt', 0):.3f}`
- **눈 상태**: {'😴 감음' if details.get('eyes_closed') else '👀 뜸'}
- **고개 상태**: {'😴 숙임' if details.get('head_down') else '✅ 정상'}

### 조치 사항
- [ ] 담당자 현장 확인
- [ ] 학생 깨우기
- [ ] 상담 필요 여부 체크

---
*자동 생성된 알림 - ViewGuard Monitor*
        """
        
        # 라벨 결정
        labels = ['drowsy']
        
        if confidence >= 0.9:
            labels.append('urgent')  # 매우 확실한 경우
        elif confidence >= 0.8:
            labels.append('high-confidence')
        
        return self.create_issue(title.strip(), body.strip(), labels)
    
    def update_dashboard_data(self, data: dict) -> bool:
        """
        대시보드 데이터 업데이트 (JSON 파일로 저장)
        GitHub Pages에서 읽을 수 있도록
        
        Args:
            data: 대시보드 데이터
            
        Returns:
            성공 여부
        """
        if not self.enabled:
            return False
        
        try:
            # data.json 파일 생성/업데이트
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Base64 인코딩
            content_encoded = base64.b64encode(json_content.encode()).decode()
            
            # 파일 존재 여부 확인
            file_url = f"{self.api_base}/contents/docs/data.json"
            response = requests.get(file_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # 파일이 있으면 업데이트
                file_data = response.json()
                sha = file_data['sha']
                
                update_data = {
                    'message': f'Update dashboard data - {datetime.now().isoformat()}',
                    'content': content_encoded,
                    'sha': sha
                }
            else:
                # 파일이 없으면 생성
                update_data = {
                    'message': 'Create dashboard data',
                    'content': content_encoded
                }
            
            response = requests.put(
                file_url,
                headers=self.headers,
                json=update_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print("✅ 대시보드 데이터 업데이트 완료")
                return True
            else:
                print(f"❌ 대시보드 업데이트 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 대시보드 업데이트 오류: {e}")
            return False
    
    def get_today_issues(self) -> List[dict]:
        """
        오늘 생성된 Issue 목록 조회
        
        Returns:
            Issue 목록
        """
        if not self.enabled:
            return []
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.api_base}/issues"
            params = {
                'labels': 'drowsy',
                'state': 'all',
                'since': f"{today}T00:00:00Z"
            }
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                issues = response.json()
                return issues
            else:
                return []
        except Exception as e:
            print(f"❌ Issue 조회 오류: {e}")
            return []
    
    def close_issue(self, issue_number: int, comment: str = None) -> bool:
        """
        Issue 닫기 (조치 완료 시)
        
        Args:
            issue_number: Issue 번호
            comment: 닫기 전 코멘트
            
        Returns:
            성공 여부
        """
        if not self.enabled:
            return False
        
        try:
            # 코멘트 추가
            if comment:
                comment_url = f"{self.api_base}/issues/{issue_number}/comments"
                requests.post(
                    comment_url,
                    headers=self.headers,
                    json={'body': comment},
                    timeout=10
                )
            
            # Issue 닫기
            issue_url = f"{self.api_base}/issues/{issue_number}"
            response = requests.patch(
                issue_url,
                headers=self.headers,
                json={'state': 'closed'},
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Issue 닫기 오류: {e}")
            return False
    
    def send_daily_summary(self, stats: dict) -> Optional[str]:
        """
        일일 통계 Issue 생성
        
        Args:
            stats: 통계 데이터
            
        Returns:
            Issue URL
        """
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        
        title = f"📊 일일 리포트: {date_str}"
        
        body = f"""
## 일일 모니터링 리포트

### 📅 날짜
{date_str}

### 📊 통계
- **총 체크**: {stats.get('total_checks', 0)}회
- **졸음 감지**: {stats.get('drowsy_detections', 0)}회
- **알림 발송**: {stats.get('alerts_sent', 0)}회
- **감지율**: {stats.get('detection_rate', 0):.1f}%

### 📍 채널별 통계
"""
        
        # 채널별 통계 추가
        channel_stats = stats.get('channel_stats', {})
        for channel, data in channel_stats.items():
            body += f"\n**{channel}**\n"
            body += f"- 체크: {data.get('checks', 0)}회\n"
            body += f"- 졸음: {data.get('drowsy', 0)}회\n"
        
        body += f"""

### 💡 인사이트
- 가장 많이 조는 시간대: {stats.get('peak_hour', 'N/A')}
- 가장 많이 조는 채널: {stats.get('peak_channel', 'N/A')}

---
*자동 생성된 일일 리포트 - ViewGuard Monitor*
        """
        
        return self.create_issue(title, body.strip(), ['daily-report'])
    
    def test_connection(self) -> bool:
        """
        GitHub 연결 테스트
        
        Returns:
            성공 여부
        """
        if not self.enabled:
            print("❌ GitHub 설정이 필요합니다")
            return False
        
        try:
            # Repo 정보 확인
            response = requests.get(
                self.api_base,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                repo_data = response.json()
                print(f"✅ GitHub 연결 성공!")
                print(f"   Repo: {repo_data['full_name']}")
                print(f"   URL: {repo_data['html_url']}")
                return True
            else:
                print(f"❌ GitHub 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ GitHub 연결 오류: {e}")
            return False


# 사용 예시
if __name__ == "__main__":
    alert = GitHubAlert()
    
    # 연결 테스트
    if alert.test_connection():
        # 테스트 알림
        test_details = {
            'ear': 0.182,
            'head_tilt': 0.612,
            'eyes_closed': True,
            'head_down': True
        }
        
        alert.send_drowsy_alert("TEST-CH01", 0.85, test_details)
