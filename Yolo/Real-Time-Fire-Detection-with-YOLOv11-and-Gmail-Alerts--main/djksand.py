model = YOLO("best.pt")
names = model.model.names

cap = cv2.VideoCapture("vid.mp4")
while True:
    ret,frame= cap.read()
    if not ret:
        break

    frame = cv2.resize(frame,(1020,500))
    
    result = model.track(frame,persist=True)

    if result[0].boxes is not None:
        boxes = result[0].boxes.xyxy.int().cpu().tolist()
        class_id = result[0].boxes.cls.