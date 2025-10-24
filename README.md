# 🎯 ViewGuard Student Monitor

**고정확도 학생 졸음 감지 시스템**

MediaPipe 기반 다중 지표 분석을 통한 정확한 졸음 감지 및 실시간 알림

---

## ✨ 주요 기능

### 🔍 고정확도 졸음 감지
- **MediaPipe Face Mesh**: 478개 얼굴 랜드마크 추적
- **다중 지표 복합 판단**:
  - EAR (Eye Aspect Ratio): 눈 감김 감지
  - Head Tilt: 고개 숙임 각도 측정 ⭐ 핵심!
  - 신뢰도 기반 필터링 (75% 이상)
- **거짓 알림 최소화**: 연속 5회 감지 후 알림

### 📹 다채널 CCTV 지원
- 뷰가드웹 16채널 화면 지원
- 좌석별 개별 ROI 설정
- 빈 좌석 자동 필터링

### 📱 알림 시스템
- 텔레그램 실시간 알림
- 알림 쿨다운 (5분 중복 방지)
- 상세 정보 포함 (EAR, 머리 각도 등)

### 📊 통계 및 모니터링
- 좌석별 졸음 감지 통계
- 실시간 디버그 화면 (선택)
- 주기적 리포트 출력

---

## 🚀 설치 및 실행

### 1. 필수 패키지 설치

```bash
cd viewguard-student-monitor
pip install -r requirements.txt
```

**필수 요구사항**:
- Python 3.8 이상
- Windows (화면 캡처 기능)

### 2. 좌석 위치 설정

```bash
python src/roi_manager.py
```

**사용법**:
1. 마우스로 드래그하여 각 좌석 영역 지정
2. `Enter`: 현재 영역을 좌석으로 저장
3. `D`: 마지막 좌석 삭제
4. `R`: 화면 새로고침
5. `S`: 저장하고 종료

좌석 정보는 `config/seats.json`에 저장됩니다.

### 3. 텔레그램 설정 (선택)

`config/settings.json` 파일을 수정:

```json
{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  }
}
```

**텔레그램 봇 생성 방법**:
1. [@BotFather](https://t.me/botfather)에서 `/newbot` 명령
2. 봇 이름 설정
3. 받은 토큰을 `bot_token`에 입력
4. [@userinfobot](https://t.me/userinfobot)에서 chat_id 확인

### 4. 모니터링 시작

**기본 모드**:
```bash
python src/main.py
```

**디버그 모드** (화면 표시):
```bash
python src/main.py --debug
```

---

## 🧪 테스트

### 웹캠으로 감지기 테스트

```bash
python test_detector.py
```

웹캠으로 실시간 졸음 감지 테스트를 할 수 있습니다.

---

## ⚙️ 설정

### config/settings.json

```json
{
  "detection": {
    "ear_threshold": 0.2,           // 눈 감김 임계값 (작을수록 민감)
    "head_tilt_threshold": 0.58,    // 고개 숙임 임계값 (클수록 둔감)
    "confidence_threshold": 0.75,   // 최소 신뢰도 (0.0 ~ 1.0)
    "drowsy_count_threshold": 5,    // 연속 감지 횟수
    "check_interval": 2,            // 체크 주기 (초)
    "alert_cooldown": 300           // 알림 쿨다운 (초)
  },
  "seat_detection": {
    "brightness_threshold": 180,    // 빈 좌석 밝기 임계값
    "edge_density_threshold": 0.05  // 에지 밀도 임계값
  }
}
```

---

## 📁 프로젝트 구조

```
viewguard-student-monitor/
├── src/
│   ├── advanced_detector.py    # 고정확도 졸음 감지기
│   ├── capture.py              # 화면 캡처 및 ROI 관리
│   ├── roi_manager.py          # 좌석 설정 GUI
│   ├── alert_system.py         # 텔레그램 알림
│   └── main.py                 # 메인 시스템
├── config/
│   ├── settings.json           # 시스템 설정
│   └── seats.json              # 좌석 좌표 (자동 생성)
├── test_detector.py            # 웹캠 테스트
├── requirements.txt            # 필요 패키지
└── README.md                   # 이 파일
```

---

## 🎯 작동 원리

### 졸음 감지 알고리즘

1. **얼굴 감지**: MediaPipe Face Mesh로 478개 랜드마크 추적
2. **EAR 계산**: 
   ```
   EAR = (수직거리1 + 수직거리2) / (2 × 수평거리)
   정상: 0.25~0.3, 감김: <0.2
   ```
3. **머리 각도 계산**:
   ```
   Head Tilt = (코-이마 거리) / (턱-이마 거리)
   정상: ~0.5, 숙임: >0.58
   ```
4. **종합 판단**:
   - 눈 감김 + 고개 숙임: 95% 신뢰도
   - 고개만 숙임: 80% 신뢰도
   - 눈만 감음: 60% 신뢰도

### 알림 로직

```
1. 졸음 감지 (신뢰도 75% 이상)
2. 카운터 증가
3. 연속 5회 감지 시
4. 쿨다운 체크 (5분 이내 알림 안함)
5. 텔레그램 알림 발송
6. 카운터 초기화
```

---

## 📊 통계 정보

모니터링 중 다음 정보가 추적됩니다:
- 총 체크 횟수
- 졸음 감지 횟수
- 알림 발송 횟수
- 좌석별 사용률 및 졸음률

5분마다 자동으로 통계가 출력됩니다.

---

## 🐛 문제 해결

### 화면 캡처가 안돼요
- Windows만 지원합니다
- 관리자 권한으로 실행해보세요

### 좌석이 감지되지 않아요
- `roi_manager.py`를 먼저 실행하여 좌석을 설정하세요
- `config/seats.json` 파일이 있는지 확인하세요

### MediaPipe 오류
```bash
pip install --upgrade mediapipe
```

### 텔레그램 알림이 안와요
- `config/settings.json`에 올바른 토큰과 chat_id를 입력했는지 확인
- 텔레그램 없이도 콘솔 알림으로 작동합니다

---

## 🔧 커스터마이징

### 감지 민감도 조정

**더 민감하게** (졸음을 빨리 감지):
```json
{
  "detection": {
    "ear_threshold": 0.25,          // 증가
    "head_tilt_threshold": 0.55,    // 감소
    "drowsy_count_threshold": 3     // 감소
  }
}
```

**덜 민감하게** (거짓 알림 줄이기):
```json
{
  "detection": {
    "ear_threshold": 0.18,          // 감소
    "head_tilt_threshold": 0.60,    // 증가
    "drowsy_count_threshold": 7     // 증가
  }
}
```

---

## 📝 개발자 정보

**프로젝트**: ViewGuard Student Monitor  
**개발자**: Tony (황성웅)  
**목적**: 김엄마독서실/수리딩클럽 학생 관리  
**기술 스택**: Python, MediaPipe, OpenCV, Telegram Bot

---

## 📄 라이선스

MIT License

---

## 🙏 감사합니다

이 프로젝트는 다음 오픈소스를 활용합니다:
- [MediaPipe](https://github.com/google/mediapipe) by Google
- [OpenCV](https://opencv.org/)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

---

## 📞 지원

문제가 있으시면 GitHub Issues에 등록해주세요.

**Happy Monitoring! 🎓**
