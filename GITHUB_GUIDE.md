# 🐙 GitHub 무료 클라우드 가이드

**완전 무료**로 관리자와 담당자 모두가 조는 학생 정보를 확인할 수 있습니다!

---

## 🎯 GitHub로 할 수 있는 것

### ✅ 1. GitHub Issues - 알림 & 이력 관리
- 졸음 감지 시 자동으로 Issue 생성
- 모든 담당자가 웹/모바일에서 확인
- 체크리스트로 조치 사항 관리
- 영구 보관 (삭제 전까지)
- **완전 무료!**

### ✅ 2. GitHub Pages - 실시간 대시보드
- 실시간 통계 웹 페이지
- 채널별 현황 확인
- 그래프 및 차트
- **완전 무료!**

### ✅ 3. GitHub Actions - 자동화
- 일일 리포트 자동 생성
- 주간 통계 자동 정리
- **완전 무료!**

---

## 🚀 빠른 시작 (10분)

### Step 1: GitHub 레포지토리 생성

1. [GitHub](https://github.com) 접속 및 로그인
2. 우측 상단 `+` → `New repository` 클릭
3. 정보 입력:
   - **Repository name**: `viewguard-monitor`
   - **Description**: `독서실 학생 모니터링 시스템`
   - **Public** 또는 **Private** 선택 (Private 추천)
4. `Create repository` 클릭

### Step 2: Personal Access Token 생성

1. GitHub 우측 상단 프로필 → `Settings`
2. 좌측 메뉴 맨 아래 `Developer settings`
3. `Personal access tokens` → `Tokens (classic)`
4. `Generate new token` → `Generate new token (classic)`
5. 정보 입력:
   - **Note**: `ViewGuard Monitor`
   - **Expiration**: `No expiration` (만료 없음)
   - **Select scopes**: 
     - ✅ `repo` (전체 체크)
     - ✅ `workflow`
6. `Generate token` 클릭
7. **토큰 복사** (한 번만 보임!)

### Step 3: 설정 파일 수정

`config/settings.json`:
```json
{
  "github": {
    "enabled": true,
    "token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "repo_owner": "your-github-username",
    "repo_name": "viewguard-monitor"
  }
}
```

**예시:**
```json
{
  "github": {
    "enabled": true,
    "token": "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
    "repo_owner": "tony-hwang",
    "repo_name": "viewguard-monitor"
  }
}
```

### Step 4: 테스트

```bash
python test_github_alert.py
```

✅ 성공하면 GitHub 레포지토리의 `Issues` 탭에 테스트 Issue가 생성됩니다!

---

## 📱 실제 사용 모습

### Issue 예시 (졸음 알림)

**제목:**
```
🚨 졸음 감지: CH03 (85%) - 10/24 14:30
```

**내용:**
```markdown
## 졸음 알림

### 기본 정보
- **채널**: CH03
- **시간**: 2025-10-24 14:30:00
- **신뢰도**: 85.0%

### 상세 분석
- **EAR (눈 감김)**: `0.182`
- **Head Tilt (고개 각도)**: `0.612`
- **눈 상태**: 😴 감음
- **고개 상태**: 😴 숙임

### 조치 사항
- [ ] 담당자 현장 확인
- [ ] 학생 깨우기
- [ ] 상담 필요 여부 체크

---
*자동 생성된 알림 - ViewGuard Monitor*
```

**라벨:**
- `drowsy` (졸음)
- `urgent` (긴급 - 신뢰도 90% 이상)

---

## 👥 팀원 추가 방법

### 담당자들에게 알림 받게 하기

#### 방법 1: GitHub Watch (추천)

1. 레포지토리 페이지 우측 상단 `Watch` 클릭
2. `All Activity` 선택
3. ✅ Issues 알림 켜기

**효과:**
- 새 Issue 생성 시 이메일/모바일 알림
- GitHub 앱에서도 푸시 알림

#### 방법 2: Collaborators 추가

1. 레포지토리 → `Settings` → `Collaborators`
2. `Add people` 클릭
3. 담당자 GitHub 계정 추가

**권한:**
- **Read**: 보기만 가능
- **Write**: Issue 닫기/수정 가능
- **Admin**: 전체 관리 가능

---

## 📊 Issue 관리

### 조치 완료 시

담당자가 학생을 확인하고 깨웠다면:

1. Issue 페이지 열기
2. 체크박스 클릭:
   - [x] 담당자 현장 확인
   - [x] 학생 깨우기
3. 코멘트 추가: "확인 완료. 학생 깨움"
4. `Close issue` 클릭

### 필터링

Issues 탭에서:
- `is:open label:drowsy` → 미조치 졸음 알림
- `is:closed label:drowsy` → 조치 완료
- `is:open label:urgent` → 긴급 알림만
- `created:>2025-10-24` → 특정 날짜 이후

---

## 📈 GitHub Pages 대시보드 (선택)

### 실시간 통계 웹 페이지 만들기

#### Step 1: docs 폴더 생성

레포지토리에 다음 파일 생성:

**docs/index.html**
```html
<!DOCTYPE html>
<html>
<head>
    <title>ViewGuard Monitor</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .channel {
            display: inline-block;
            width: 150px;
            padding: 15px;
            margin: 10px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .channel.drowsy {
            background: #ffebee;
            border: 2px solid #f44336;
        }
        .channel.alert {
            background: #e8f5e9;
        }
        h1 { color: #333; }
        .stats {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>🎯 ViewGuard Monitor</h1>
    
    <div class="stats">
        <h2>📊 오늘의 통계</h2>
        <p>총 체크: <strong id="total-checks">0</strong>회</p>
        <p>졸음 감지: <strong id="drowsy-count">0</strong>회</p>
        <p>마지막 업데이트: <span id="last-update">-</span></p>
    </div>
    
    <h2>📺 채널 상태</h2>
    <div id="channels"></div>
    
    <script>
        // data.json 로드 (시스템이 자동 업데이트)
        fetch('data.json')
            .then(r => r.json())
            .then(data => {
                document.getElementById('total-checks').textContent = data.total_checks;
                document.getElementById('drowsy-count').textContent = data.drowsy_count;
                document.getElementById('last-update').textContent = data.last_update;
                
                // 채널 상태 표시
                const channelsDiv = document.getElementById('channels');
                for (let i = 1; i <= 16; i++) {
                    const ch = data.channels[`CH${i.toString().padStart(2, '0')}`];
                    const div = document.createElement('div');
                    div.className = `channel ${ch.status}`;
                    div.innerHTML = `
                        <h3>CH ${i.toString().padStart(2, '0')}</h3>
                        <p>${ch.status === 'drowsy' ? '😴' : '✅'}</p>
                        <small>${ch.last_check}</small>
                    `;
                    channelsDiv.appendChild(div);
                }
            });
        
        // 30초마다 자동 새로고침
        setInterval(() => location.reload(), 30000);
    </script>
</body>
</html>
```

#### Step 2: GitHub Pages 활성화

1. 레포지토리 → `Settings` → `Pages`
2. **Source**: `Deploy from a branch`
3. **Branch**: `main` → `/docs` 선택
4. `Save` 클릭

#### Step 3: 접속

5분 후:
```
https://your-username.github.io/viewguard-monitor/
```

**효과:**
- 실시간 채널 상태 확인
- 오늘의 통계 표시
- 모든 담당자가 웹으로 접근 가능

---

## 🤖 GitHub Actions 자동화 (고급)

### 일일 리포트 자동 생성

**.github/workflows/daily-report.yml**
```yaml
name: Daily Report

on:
  schedule:
    - cron: '0 18 * * *'  # 매일 18시 (한국 시간 03시)

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Report
        run: |
          # Python 스크립트 실행
          # 일일 통계 Issue 자동 생성
```

---

## 💡 장점

### ✅ 완전 무료
- GitHub는 Private Repo도 무료
- Issue 무제한
- Pages 무료 호스팅

### ✅ 접근성
- 웹 브라우저로 어디서나 접근
- GitHub 모바일 앱 지원
- 이메일/푸시 알림

### ✅ 협업
- 여러 담당자 동시 확인
- 코멘트로 의사소통
- 체크리스트로 조치 관리

### ✅ 이력 관리
- 모든 알림 영구 보관
- 검색 및 필터링
- 통계 및 분석 가능

---

## 🆚 다른 방법과 비교

| | GitHub | 텔레그램 | 구글 시트 |
|---|---|---|---|
| **비용** | 무료 | 무료 | 무료 |
| **알림** | 이메일/앱 | 즉시 푸시 | ❌ |
| **이력** | ✅ 영구 | ⚠️ 제한 | ✅ |
| **협업** | ✅ 최고 | ✅ | ⚠️ |
| **검색** | ✅ 강력 | ⚠️ | ✅ |
| **대시보드** | ✅ Pages | ❌ | ⚠️ |
| **설정** | 10분 | 5분 | 15분 |

---

## 🎯 Tony님께 추천

### 조합 1: GitHub + 텔레그램
```
- 텔레그램: 즉시 알림 (5초)
- GitHub: 이력 관리 및 협업
```

### 조합 2: GitHub만 사용
```
- GitHub Issues: 알림 + 이력
- GitHub Pages: 대시보드
- GitHub Mobile: 푸시 알림
```

**Tony님의 독서실에는 GitHub만으로도 충분합니다!**

---

## 🧪 테스트

```bash
# GitHub 연결 테스트
python test_github_alert.py

# 실제 알림 테스트
python -c "
from src.alert_system_github import GitHubAlert
alert = GitHubAlert()
alert.send_drowsy_alert('TEST', 0.85, {
    'ear': 0.182,
    'head_tilt': 0.612,
    'eyes_closed': True,
    'head_down': True
})
"
```

---

## 🔧 문제 해결

### Q: Issue가 생성되지 않아요
**A**: 
1. Token이 `repo` 권한을 가지고 있는지 확인
2. repo_owner와 repo_name이 정확한지 확인
3. `python test_github_alert.py`로 연결 테스트

### Q: 담당자가 알림을 못 받아요
**A**:
- 레포지토리를 `Watch` → `All Activity`로 설정
- 또는 Collaborator로 추가

### Q: Private Repo는 유료 아닌가요?
**A**:
- 개인 계정은 Private Repo 무제한 무료!
- 팀 계정도 3명까지 무료

---

## 📞 다음 단계

1. **GitHub 레포지토리 생성** (2분)
2. **Personal Access Token 생성** (3분)
3. **settings.json 설정** (1분)
4. **테스트 실행** (1분)
5. **담당자 초대** (3분)

**총 10분이면 완료!** ✅

---

**완전 무료 클라우드 시스템 완성! 🎉**

*Made with ❤️ for 김엄마독서실 & 수리딩클럽*
