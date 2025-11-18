import numpy as np
import cv2

cap = cv2.VideoCapture("D:/mazen/EagleVision/projects/test-project/openCV/Detect-red-traffic-violation-using-openCV-yolov10/tr.mp4")

green_lower_range = np.array([58, 97, 222])
green_upper_range = np.array([179, 255, 255])
red_lower_range = np.array([0, 43, 184])
red_upper_range = np.array([56, 132, 255])

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (1020,600))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    green_mask = cv2.inRange(hsv, green_lower_range, green_upper_range)
    red_mask = cv2.inRange(hsv, red_lower_range, red_upper_range)
        

    combined_mask = cv2.bitwise_or(green_mask, red_mask)

    _, final_mask = cv2.threshold(combined_mask, 127, 255, cv2.THRESH_BINARY )
    detect_label = None

    conts, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for c in conts:
        if cv2.contourArea(c) >50 :
            x,y,w,h = cv2.boundingRect(c)

            cx = x+w//2
            cy = y+h//2

        if cv2.countNonZero(green_mask[y:y+h, x:x+w]) > 0:
            color = (0,255,0)
            text_color = (0,255,0)
            label = "Green"
        elif cv2.countNonZero(red_mask[y:y+h, x:x+w]) > 0:
            color = (0,0,255)
            text_color = (0,0,255)
            label = "Red" 
        else:
            continue

        detect_label = label

        cv2.rectangle(frame, (x,y), (x+w, y+h), color, 2)
        cv2.circle(frame, (cx, cy), 1, (255,0,0), -1)

        cv2.putText(frame, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        cv2.imshow("green_mask", green_mask)
        cv2.imshow("red_mask", red_mask)
        cv2.imshow("combined_mask", combined_mask)
        cv2.imshow("final_mask", final_mask)
        cv2.imshow("frame", frame)
            
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
