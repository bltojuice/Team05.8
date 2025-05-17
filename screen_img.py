# screan_img.py

import cv2

def capture_image_bytes():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("카메라를 열 수 없습니다.")

    print("스페이스바를 눌러 캡처 / ESC로 종료")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("캡처화면", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break
        elif key == 32:  # Space
            _, buffer = cv2.imencode('.jpg', frame)
            image_bytes = buffer.tobytes()
            cap.release()
            cv2.destroyAllWindows()
            return image_bytes

    cap.release()
    cv2.destroyAllWindows()
    return None

capture_image_bytes()