"""
웹캠으로 졸음 감지기 테스트
"""
import cv2
import sys
sys.path.append('src')

from advanced_detector import AdvancedDrowsinessDetector


def test_with_webcam():
    """웹캠으로 테스트"""
    print("=" * 60)
    print("🎥 웹캠 테스트 모드")
    print("=" * 60)
    print("ESC 키로 종료")
    print()
    
    # 감지기 초기화
    detector = AdvancedDrowsinessDetector()
    
    # 웹캠 열기
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 웹캠을 열 수 없습니다")
        return
    
    print("✅ 웹캠 시작!")
    
    cv2.namedWindow('Drowsiness Test', cv2.WINDOW_NORMAL)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("⚠️  프레임 읽기 실패")
            break
        
        # 졸음 감지
        is_drowsy, confidence, details = detector.detect_drowsiness(frame)
        
        # 결과 표시
        if 'status' in details and details['status'] != 'no_face_detected':
            # 상태 텍스트
            status_text = "😴 DROWSY!" if is_drowsy else "✅ ALERT"
            status_color = (0, 0, 255) if is_drowsy else (0, 255, 0)
            
            cv2.putText(frame, status_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 3)
            
            # 신뢰도
            cv2.putText(frame, f"Confidence: {confidence:.1%}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 상세 정보
            y_offset = 110
            cv2.putText(frame, f"EAR: {details['ear']:.3f}", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30
            
            cv2.putText(frame, f"Head Tilt: {details['head_tilt']:.3f}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                       (255, 255, 255), 2)
            y_offset += 30
            
            eye_status = "CLOSED" if details['eyes_closed'] else "OPEN"
            cv2.putText(frame, f"Eyes: {eye_status}", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30
            
            head_status = "DOWN" if details['head_down'] else "UP"
            cv2.putText(frame, f"Head: {head_status}", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "No Face Detected", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 화면 표시
        cv2.imshow('Drowsiness Test', frame)
        
        # 종료 키
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ 테스트 종료")


if __name__ == "__main__":
    test_with_webcam()
