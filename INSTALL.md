# 📦 설치 가이드

## 🎯 시스템 요구사항

- **OS**: Windows 10/11 (화면 캡처 기능)
- **Python**: 3.8 이상
- **RAM**: 4GB 이상 권장
- **CPU**: 멀티코어 권장 (MediaPipe 처리)

---

## 📥 설치 단계

### 1. Python 설치 확인

```bash
python --version
```

Python 3.8 이상이 없다면 [python.org](https://www.python.org/downloads/)에서 설치

### 2. 프로젝트 다운로드

**Git 사용:**
```bash
git clone https://github.com/YOUR_USERNAME/viewguard-student-monitor.git
cd viewguard-student-monitor
```

**또는 ZIP 다운로드:**
- GitHub에서 "Code" → "Download ZIP"
- 압축 해제 후 폴더로 이동

### 3. 가상환경 생성 (권장)

```bash
python -m venv venv
```

**활성화:**
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

**시간 소요**: 약 2-5분 (MediaPipe가 큰 패키지입니다)

### 5. 설치 확인

```bash
python test_detector.py
```

웹캠이 작동하고 얼굴 감지가 되면 설치 성공!

---

## 🔧 설정

### 1. 텔레그램 봇 설정 (선택)

#### 봇 생성:
1. 텔레그램에서 [@BotFather](https://t.me/botfather) 검색
2. `/newbot` 명령 입력
3. 봇 이름 입력 (예: ViewGuard Monitor)
4. 봇 사용자명 입력 (예: viewguard_monitor_bot)
5. 받은 **토큰** 저장

#### Chat ID 확인:
1. [@userinfobot](https://t.me/userinfobot) 검색
2. 시작 버튼 클릭
3. 받은 **ID** 저장

#### 설정 파일 수정:
`config/settings.json` 열기:
```json
{
  "telegram": {
    "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "123456789"
  }
}
```

### 2. 좌석 위치 설정

```bash
python src/roi_manager.py
```

**조작법:**
1. 뷰가드웹 화면을 열어둔 상태에서 실행
2. 마우스로 드래그하여 각 좌석 영역 지정
3. `Enter` 키로 저장
4. 모든 좌석 지정 후 `S` 키로 종료

---

## 🚀 실행

### Windows 사용자 (추천)

```bash
start.bat
```

메뉴에서 선택:
- `1`: 좌석 설정
- `2`: 모니터링 시작
- `3`: 디버그 모드
- `4`: 웹캠 테스트

### 직접 실행

**좌석 설정:**
```bash
python src/roi_manager.py
```

**모니터링 시작:**
```bash
python src/main.py
```

**디버그 모드:**
```bash
python src/main.py --debug
```

---

## ❗ 문제 해결

### ModuleNotFoundError: mediapipe

```bash
pip install --upgrade mediapipe
```

### ImportError: cv2

```bash
pip install opencv-python
```

### 화면 캡처가 안됨

- Windows만 지원됩니다
- 관리자 권한으로 실행:
  ```bash
  # PowerShell을 관리자로 실행 후
  python src/main.py
  ```

### MediaPipe가 너무 느림

`config/settings.json`에서 체크 주기 증가:
```json
{
  "detection": {
    "check_interval": 5  // 2초 → 5초
  }
}
```

### pip install이 느림

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

---

## 🔄 업데이트

### Git 사용:
```bash
git pull origin main
pip install -r requirements.txt  # 새 패키지 확인
```

### 수동:
1. 새 버전 다운로드
2. `config/` 폴더 백업
3. 새 파일로 교체
4. `config/` 폴더 복원

---

## 📞 지원

설치 중 문제가 있으면:
1. [Issues](https://github.com/YOUR_USERNAME/viewguard-student-monitor/issues) 확인
2. 새 이슈 등록
3. 다음 정보 포함:
   - Python 버전
   - 오류 메시지
   - OS 정보

---

**설치 완료! 이제 모니터링을 시작하세요! 🎉**
