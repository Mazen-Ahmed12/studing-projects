import cv2
import mediapipe as mp
import os

os.chdir(r"mediapipe/meshFace")

mp_face_mesh = mp.solutions.face_mesh.FaceMesh()
cap = cv2.VideoCapture(0)

while True:
    ret, image = cap.read()
    if ret is not True:
        break

    height, width, _ = image.shape
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    results = mp_face_mesh.process(rgb_image)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for i in range (0, 468):   #bec there is 468 points in human face
                pt1 = face_landmarks.landmark[i]
                print(pt1)
                x= int(pt1.x * width)
                y= int(pt1.y * height)
                cv2.circle(image, (x, y), 2, (100, 100, 0), -1)

    cv2.imshow("image", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
        
