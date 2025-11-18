import cv2

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame , cv2.COLOR_BGR2HSV)
    height, width, _ = frame.shape
    
    cx=int(width/2) #center of X
    cy=int(height/2) #center of Y
    
    pixel_center = hsv[cy, cx]   #Extracts the H, S, and V values of the center pixel from the HSV image.
    hue_value = pixel_center[0]  #Selects the Hue component, which is the first element (index 0) of the pixel array.
    
    color="undefined"
    if hue_value < 5:
        color="red"
    elif hue_value < 22:
        color="orange"
    elif hue_value < 38:
        color="yellow"
    elif hue_value < 75:
        color="green"
    elif hue_value < 150:
        color="blue"
    else:
        color="red"

    pixel_center_bgr = frame[cy, cx]    
    b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2]) #Extracts the B, G, and R values of the center pixel from the BGR image.
    
    cv2.rectangle(frame, (cx - 220, 10), (cx + 200, 120), (255, 255, 255), -1)
    cv2.putText(frame, color, (cx -200,100), 0, 3, (b, g, r), 5)
    cv2.circle(frame, (cx, cy), 5, (25, 25, 25), 3)
    cv2.imshow("frame", frame)
    k = cv2.waitKey(1)
    if k==27:
        break
    
cap.release()
cv2.destroyAllWindows()