@echo off
chcp 65001 > nul
echo ╔══════════════════════════════════════════════════╗
echo ║                                                  ║
echo ║            👁️  ViewGuard 시작                   ║
echo ║        졸음 감지 모니터링 시스템                 ║
echo ║                                                  ║
echo ╚══════════════════════════════════════════════════╝
echo.

REM 가상환경이 있으면 활성화
if exist venv\Scripts\activate.bat (
    echo [INFO] 가상환경 활성화...
    call venv\Scripts\activate.bat
)

REM 프로그램 실행
echo [INFO] ViewGuard 실행 중...
echo.
python viewguard_main.py

pause
