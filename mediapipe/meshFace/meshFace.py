import cv2
import mediapipe as mp
import os

os.chdir(r"mediapipe/meshFace")
image = cv2.imread("images.png")

mp_face_mesh = mp.solutions.face_mesh.FaceMesh()
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

results = mp_face_mesh.process(rgb_image)

height, width, _ = image.shape

for face_landmarks in results.multi_face_landmarks:
    for i in range (0, 468):   # bec there is 468 points in human face somethimes it calculated as 68 points
        pt1 = face_landmarks.landmark[i]
        print(pt1)
        x= int(pt1.x * width)
        y= int(pt1.y * height)
        cv2.circle(image, (x, y), 2, (100, 100, 0), -1)

cv2.imshow("image", image)

cv2.waitKey(0)
cv2.destroyAllWindows()
    