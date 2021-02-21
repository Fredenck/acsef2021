#Libraries
import RPi.GPIO as GPIO
import time
import cv2
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

GPIO_LEFT = 2
GPIO_FORWARD = 3
GPIO_RIGHT = 4
GPIO_UP = 17
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

GPIO.setup(GPIO_LEFT, GPIO.OUT)
GPIO.setup(GPIO_FORWARD, GPIO.OUT)
GPIO.setup(GPIO_RIGHT, GPIO.OUT)
GPIO.setup(GPIO_UP, GPIO.OUT)

# set up camera
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


GPIOS = [2, 3, 4, 17]
def tactile(detected): # [0.0.0.1] means something is above
    for i in range(4):
        if GPIO.input(GPIOS[detected[i]]) == detected[i]:
            continue
        else:
            GPIO.output(GPIOS[i], detected[i]==1)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    print ("Measured Distance = %.1f cm" % dist)
    
    if distance < 152.4: # 5ft
        return 1
    return 0

def detect():
    where = [0. 0. 0]
    ret, frame = cap.read()
    ClassIndex, confidece , bbox = model.detect(frame, confThreshold = 0.55)
    if (len(ClassIndex) != 0):
        for ClassInd, conf, boxes in zip(ClassIndex.flatten(), confidece.flatten(), bbox):
            if ClassInd <= 80:
                cv2.rectangle(frame, boxes, (255,0,0), 2)
                if boxes[0] < 300:
                    print("right")
                    where[2] = 1
                elif boxes[0] > 600:
                    print('left')
                    where[0] = 1
                else:
                    print('center')
                    where[1] = 1
                cv2.putText(frame, classLabels[ClassInd-1], (boxes[0]+10, boxes[1]+40), font, fontScale=font_scale, color=(0,255,0), thickness = 3)
    cv2.imshow('Object Detection', frame)
    return where
    if cv2.waitKey(2) & 0xff == ord('q'):
        break

if __name__ == '__main__':
    try:
        while True:
            above = distance()
            others = detect()
            others.append(above)
            tactile(others)
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
