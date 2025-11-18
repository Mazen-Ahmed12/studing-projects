import cv2
import mediapipe
import numpy
import autopy

cap = cv2.VideoCapture(0)

initHand = mediapipe.solutions.hands
mainHands = initHand.Hands()
draw = mediapipe.solutions.drawing_utils
wScr, hSrc = autopy.screen.size()
px, py = 0, 0
cx, cy = 0, 0


def handLandmarks(colorImg):
    landmarkList = []

    landmarkPositions = mainHands.process(colorImg)
    landmarkCheck = landmarkPositions.multi_hand_landmarks
    if landmarkCheck:
        for handLms in landmarkCheck:
            for idd, lm in enumerate(handLms.landmark):
                draw.draw_landmarks(img, handLms, initHand.HAND_CONNECTIONS)
                h, w, c = colorImg.shape
                centerX, centerY = int(lm.x * w), int(lm.y * h)
                landmarkList.append([idd, centerX, centerY])

    return landmarkList


def fingers(landmarks):
    fingerTips = []
    tipIds = [4, 8, 12, 16, 20]  # indexes for the tips of each finger

    # check if thumb is up
    if (landmarks[tipIds[0]][1] > landmarks[tipIds[0] - 1][1]):  # tipIds[0] means the first index in tipIds and tipIds[0][1] the [1] means the second index of the tipIds and the index of landmark has 3 indices [index, x-axis, y-axis]
        fingerTips.append(1)
    else:
        fingerTips.append(0)

    for id in range(1, 5):  # Check fingers 1-4 (index, middle, ring, pinky)
        if (landmarks[tipIds[id]][2] < landmarks[tipIds[id] - 3][2]):  # Compare y-coordinates
            fingerTips.append(1)
        else:
            fingerTips.append(0)
    return fingerTips


while True:
    check, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    lmList = handLandmarks(imgRGB)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        finger = fingers(lmList)

        if finger[1] == 1 and finger[2] == 0:
            x3 = numpy.interp(x1, (0, 640), (0, wScr))
            y3 = numpy.interp(y1, (0, 480), (0, hSrc))

            cx = px + (x3 - px) / 7  # 7 can be any number form 1-10 doesn't matter
            cy = py + (y3 - py) / 7  # those 2 are for smoothing to make mouse not viberate to be fixed
 
            autopy.mouse.move(wScr - cx, cy)
            px, py = cx, cy

        if finger[1] == 0 and finger[0] == 1:
            autopy.mouse.click()

    cv2.imshow("Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
cap.release()
