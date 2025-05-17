import cv2

# 카메라 객체 생성 (기본 카메라)
cap = cv2.VideoCapture(0)

# 카메라 접근 확인
if not cap.isOpened():
    print("카메라에 접근할 수 없습니다.")
    exit()

# 카메라 사용 (예시)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("카메라", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 객체 해제
cap.release()
cv2.destroyAllWindows()