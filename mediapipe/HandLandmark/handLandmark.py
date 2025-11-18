import cv2
import mediapipe
import time

result = cv2.VideoWriter('./mediapipe/HandLandmark/handLandmark.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))

cap = cv2.VideoCapture(0)

mp_hands = mediapipe.solutions.hands
hands = mp_hands.Hands()
mp_draw = mediapipe.solutions.drawing_utils

pTime = 0 #Previous Time
cTime = 0 #Current Time
 
while True:
    _ , img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for idd, lm in enumerate(handLms.landmark): # this used for cv2.circle is used to select speceific landmarks and idd is the index of the landmark and the llm is the dimensions of the landmanrk 
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                if idd == 0:  # this is the if condition that i will select the landmark with 
                    cv2.circle(img, (cx, cy), 9, (255, 255, 0), cv2.FILLED)

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)   
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (15, 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    
    result.write(img)
    cv2.imshow("Image", img)
    
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
