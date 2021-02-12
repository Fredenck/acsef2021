import cv2
config_file = 'ssd_mobilenet_coco/ssd_mobilenet_config.pbtxt'
frozen_model = 'ssd_mobilenet_coco/frozen_inference_graph.pb'
model = cv2.dnn_DetectionModel(frozen_model, config_file)
model.setInputSize(320,320)
model.setInputScale(1.0/127.5)
model.setInputMean((127.5, 127.5, 127.5))
model.setInputSwapRB(True)
classLabels = []
label_path = 'ssd_mobilenet_coco/coconames.txt'
with open(label_path, 'rt') as labels:
    classLabels = labels.read().rstrip('\n').split('\n')
cap = cv2.VideoCapture(0)
    
font_scale = 3
font = cv2.FONT_HERSHEY_PLAIN
while True:
    ret, frame = cap.read()
    ClassIndex, confidece , bbox = model.detect(frame, confThreshold = 0.55)
    if (len(ClassIndex) != 0):
        for ClassInd, conf, boxes in zip(ClassIndex.flatten(), confidece.flatten(), bbox):
            if ClassInd <= 80:
                cv2.rectangle(frame, boxes, (255,0,0), 2)
                if boxes[0] < 300:
                    print("right")
                elif boxes[0] > 600:
                    print('left')
                else:
                    print('center')
                cv2.putText(frame, classLabels[ClassInd-1], (boxes[0]+10, boxes[1]+40), font, fontScale=font_scale, color=(0,255,0), thickness = 3)
    cv2.imshow('Object Detection', frame)
    if cv2.waitKey(2) & 0xff == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
