# 📱 다중 알림 시스템 가이드

관리자와 담당자 모두가 조는 학생 정보를 실시간으로 확인할 수 있는 시스템입니다!

---

## 🎯 지원하는 알림 방식

### 1️⃣ 텔레그램 (필수) ⭐⭐⭐
- ✅ 실시간 알림
- ✅ 여러 명에게 동시 전송
- ✅ 그룹 채팅 지원
- ✅ 무료

### 2️⃣ 구글 스프레드시트 (추천) ⭐⭐
- ✅ 자동 기록 및 이력 관리
- ✅ 통계 분석 가능
- ✅ 실시간 동기화
- ✅ 무료

### 3️⃣ 웹훅 / n8n 연동 (고급) ⭐
- ✅ 다른 자동화 도구 연결
- ✅ 커스텀 워크플로우
- ✅ 무료 (n8n self-hosted)

---

## 🚀 방법 1: 텔레그램 그룹 (가장 쉬움)

### Step 1: 그룹 생성

1. 텔레그램 앱 열기
2. 새 그룹 만들기
3. 이름: "김엄마독서실 모니터링" (예시)
4. 멤버 추가:
   - Tony (관리자)
   - 담당자 1
   - 담당자 2
   - ...

### Step 2: 봇을 그룹에 추가

1. [@BotFather](https://t.me/botfather)에서 봇 생성 (이미 있으면 생략)
2. 봇을 그룹에 초대
3. 봇을 **관리자**로 승격 (메시지 보내기 권한 필요)

### Step 3: 그룹 Chat ID 확인

```bash
# 봇에게 메시지 보내기
/my_id @your_bot_name

# 또는 이 봇 사용
@getidsbot
```

그룹 ID는 `-100`으로 시작합니다 (예: `-1001234567890`)

### Step 4: 설정 파일 수정

`config/settings.json`:
```json
{
  "telegram": {
    "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_ids": {
      "admin": "123456789",           // Tony 개인
      "staff1": "987654321",          // 담당자 1
      "group": "-1001234567890"       // 그룹 채팅
    },
    "alert_to": "group"  // 그룹으로 전송
  }
}
```

### 알림 전송 대상 옵션

```json
"alert_to": "group"   // 그룹에만 전송 (모두가 봄)
"alert_to": "all"     // 모든 개인에게 개별 전송
"alert_to": "admin"   // 관리자에게만
"alert_to": "staff1"  // 특정 담당자에게만
```

---

## 📊 방법 2: 구글 스프레드시트

### Step 1: Google Cloud 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. Google Sheets API 활성화
4. Google Drive API 활성화

### Step 2: 서비스 계정 생성

1. "IAM 및 관리자" → "서비스 계정"
2. 서비스 계정 만들기
3. 역할: "편집자"
4. 키 생성 (JSON) → 다운로드
5. 파일명: `google_credentials.json`

### Step 3: 스프레드시트 준비

1. 구글 시트 새로 만들기
2. 이름: "독서실_졸음_기록"
3. 첫 번째 시트: "실시간기록"
4. 헤더 행:

| 시간 | 채널 | 신뢰도 | EAR | Head Tilt | 상태 | 알림여부 |
|------|------|--------|-----|-----------|------|----------|

5. 서비스 계정 이메일을 **편집자**로 공유

### Step 4: 설정

`config/settings.json`:
```json
{
  "google_sheets": {
    "enabled": true,
    "credentials_file": "config/google_credentials.json",
    "sheet_name": "독서실_졸음_기록",
    "worksheet": "실시간기록"
  }
}
```

### Step 5: 패키지 설치

```bash
pip install gspread oauth2client
```

---

## 🔗 방법 3: n8n 웹훅 연동

### Tony님의 기존 n8n에 연결!

### Step 1: n8n에서 Webhook 노드 추가

1. n8n 워크플로우 열기
2. "Webhook" 노드 추가
3. HTTP Method: POST
4. Path: `/drowsy-alert`
5. URL 복사 (예: `https://n8n.your-domain.com/webhook/drowsy-alert`)

### Step 2: 설정

`config/settings.json`:
```json
{
  "webhook": {
    "enabled": true,
    "url": "https://n8n.your-domain.com/webhook/drowsy-alert",
    "method": "POST"
  }
}
```

### Step 3: n8n에서 처리

웹훅으로 받은 데이터:
```json
{
  "type": "drowsy_alert",
  "channel": "CH01",
  "confidence": 0.85,
  "timestamp": "2025-10-24T14:30:00",
  "details": {
    "ear": 0.182,
    "head_tilt": 0.612,
    "eyes_closed": true,
    "head_down": true
  }
}
```

**n8n에서 할 수 있는 일:**
- 카카오톡 메시지 (비즈니스 API)
- 이메일 발송
- 슬랙 알림
- 구글 시트 기록
- 커스텀 로직

---

## 🎯 추천 조합

### 🥇 Tony님께 추천: 텔레그램 그룹 + 구글 시트

```json
{
  "telegram": {
    "bot_token": "YOUR_TOKEN",
    "chat_ids": {
      "group": "-1001234567890"
    },
    "alert_to": "group"
  },
  "google_sheets": {
    "enabled": true,
    "credentials_file": "config/google_credentials.json",
    "sheet_name": "독서실_졸음_기록"
  }
}
```

**장점:**
- ✅ 실시간 알림 (텔레그램)
- ✅ 이력 관리 (구글 시트)
- ✅ 둘 다 무료
- ✅ 모바일/PC 모두 사용 가능

---

## 📱 실제 사용 시나리오

### 시나리오 1: 학생이 조는 경우

```
1. 시스템이 CH03 학생 졸음 감지
   ↓
2. 텔레그램 그룹에 알림 전송
   "🚨 CH03 학생 졸는 중 (신뢰도 85%)"
   ↓
3. 관리자 & 모든 담당자가 동시에 확인
   ↓
4. 담당자가 현장 확인
   ↓
5. 구글 시트에 자동 기록
```

### 시나리오 2: 퇴근 후 확인

```
1. 하루 종료 후 구글 시트 열기
   ↓
2. 오늘 졸음 감지 통계 확인
   ↓
3. 자주 조는 학생 파악
   ↓
4. 다음날 개별 상담
```

---

## 🧪 테스트 방법

### 전체 시스템 테스트

```bash
python src/test_multi_alert.py
```

### 개별 테스트

```python
from alert_system_multi import MultiAlert

alert = MultiAlert()

# 모든 채널 테스트
alert.test_all_channels()

# 실제 알림 테스트
alert.send_drowsy_alert("TEST", 0.85, {
    'ear': 0.180,
    'head_tilt': 0.620,
    'eyes_closed': True,
    'head_down': True
})
```

---

## 🔧 문제 해결

### Q: 텔레그램 그룹에 메시지가 안와요

**A**: 
1. 봇이 그룹의 관리자인지 확인
2. 그룹 ID가 맞는지 확인 (`-100`으로 시작)
3. 봇에게 그룹에서 메시지 보내기: `/start`

### Q: 구글 시트에 기록이 안돼요

**A**:
1. 서비스 계정이 시트에 편집 권한이 있는지 확인
2. API가 활성화되었는지 확인
3. credentials 파일 경로가 맞는지 확인

### Q: 담당자가 알림을 못 받아요

**A**:
- 그룹 모드 사용: 그룹에 담당자 초대
- 개별 모드 사용: `chat_ids`에 담당자 ID 추가

---

## 📊 구글 시트 활용 예시

### 시간대별 통계

```
=COUNTIF(A:A, ">=2025-10-24 09:00")  # 오전 9시 이후
```

### 채널별 통계

```
=COUNTIF(B:B, "CH01")  # CH01 졸음 횟수
```

### 평균 신뢰도

```
=AVERAGE(C:C)
```

### 시각화

- 그래프: 시간대별 졸음 추이
- 파이 차트: 채널별 비율
- 히트맵: 시간/채널 교차 분석

---

## 🎯 다음 단계

1. **텔레그램 그룹 만들기** (5분)
2. **봇 추가 및 설정** (5분)
3. **테스트** (1분)
4. **실제 운영** ✅

또는:

1. **구글 시트 준비** (10분)
2. **서비스 계정 생성** (10분)
3. **패키지 설치 및 설정** (5분)
4. **테스트** (1분)
5. **실제 운영** ✅

---

## 📞 지원

문제가 있으면:
1. 설정 파일 확인 (`settings.json`)
2. 테스트 실행 (`test_multi_alert.py`)
3. 로그 확인

**모두가 함께 학생들을 케어할 수 있습니다! 🎓✨**
