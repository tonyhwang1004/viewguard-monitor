@echo off
chcp 65001 > nul
echo ============================================
echo ViewGuard Student Monitor
echo ============================================
echo.
echo [초기 설정]
echo 1. 채널 버튼 위치 설정 (순차 모드용)
echo 2. 좌석 위치 설정 (16분할 모드용)
echo.
echo [모니터링 시작]
echo 3. 순차 모드 (고화질 추천!) ⭐
echo 4. 순차 모드 (디버그)
echo 5. 16분할 모드 (기본)
echo 6. 16분할 모드 (디버그)
echo.
echo [테스트]
echo 7. 웹캠 테스트
echo.
echo 8. 종료
echo.
set /p choice=선택: 

if "%choice%"=="1" (
    echo.
    echo 🎮 채널 버튼 위치 설정...
    python channel_setup.py
) else if "%choice%"=="2" (
    echo.
    echo 📍 좌석 위치 설정...
    python src\roi_manager.py
) else if "%choice%"=="3" (
    echo.
    echo 🚀 순차 모드 시작 (고화질)
    python src\main_sequential.py
) else if "%choice%"=="4" (
    echo.
    echo 🔍 순차 모드 (디버그)
    python src\main_sequential.py --debug
) else if "%choice%"=="5" (
    echo.
    echo 🚀 16분할 모드 시작
    python src\main.py
) else if "%choice%"=="6" (
    echo.
    echo 🔍 16분할 모드 (디버그)
    python src\main.py --debug
) else if "%choice%"=="7" (
    echo.
    echo 🎥 웹캠 테스트...
    python test_detector.py
) else if "%choice%"=="8" (
    exit
) else (
    echo 잘못된 선택입니다.
    pause
)

pause
