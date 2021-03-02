#Libraries
import RPi.GPIO as GPIO
import time
import cv2
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

GPIO_LEFT = 17
GPIO_FORWARD = 27
GPIO_RIGHT = 22
GPIO_UP = 25
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


GPIO.setup(GPIO_LEFT, GPIO.OUT, initial=False)
GPIO.setup(GPIO_FORWARD, GPIO.OUT, initial=False)
GPIO.setup(GPIO_RIGHT, GPIO.OUT, initial=False)
GPIO.setup(GPIO_UP, GPIO.OUT, initial=False)


# set up camera
config_file = '/home/pi/Desktop/whiteCane/ssd_mobilenet_coco/ssd_mobilenet_config.pbtxt'
frozen_model = '/home/pi/Desktop/whiteCane/ssd_mobilenet_coco/frozen_inference_graph.pb'
label_path = '/home/pi/Desktop/whiteCane/ssd_mobilenet_coco/coconames.txt'
model = cv2.dnn_DetectionModel(frozen_model, config_file)
model.setInputSize(320,320)
model.setInputScale(1.0/127.5)
model.setInputMean((127.5, 127.5, 127.5))
model.setInputSwapRB(True)
classLabels = []
with open(label_path, 'rt') as labels:
    classLabels = labels.read().rstrip('\n').split('\n')
cap = cv2.VideoCapture(0)
    
font_scale = 3
font = cv2.FONT_HERSHEY_PLAIN


GPIOS = [17, 27, 22, 25]

GPIO.output(GPIOS, False)
# GPIOS = [GPIO_LEFT, GPIO_FORWARD, GPIO_RIGHT, GPIO_UP]
def tactile(detected): # [0.0.0.1] means something is above

    for i in range(4):
       # print(detected[i])
        print("BEFORE " + str(GPIO.input(GPIOS[i])))
        if GPIO.input(GPIOS[i]) == detected[i]:
            pass
            # print("SAME")
        else:
           # print("CHANGE")
            GPIO.output(GPIOS[i], detected[i]==1)
        print("AFTER " + str(GPIO.input(GPIOS[i])))
    print(GPIO.input(GPIOS[3]))
    return 1
    
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
    print ("Measured Distance = %.1f cm" % distance)
    
    if distance < 152.4: # 5ft
        return 1
    return 0

def detect():
    where = [0, 0, 0]
    ret, frame = cap.read()
    ClassIndex, confidece , bbox = model.detect(frame, confThreshold = 0.55)
    if (len(ClassIndex) != 0):
        for ClassInd, conf, boxes in zip(ClassIndex.flatten(), confidece.flatten(), bbox):
            if ClassInd <= 80:
                cv2.rectangle(frame, boxes, (255,0,0), 2)
                if boxes[0] < 213:
                    print("right")
                    where[2] = 1
                elif boxes[0] > 326:
                    print('left')
                    where[0] = 1
                else:
                    print('center')
                    where[1] = 1
                cv2.putText(frame, classLabels[ClassInd-1], (boxes[0]+10, boxes[1]+40), font, fontScale=font_scale, color=(0,255,0), thickness = 3)
    # cv2.imshow('Object Detection', frame)
    return where

if __name__ == '__main__':
    try:
        while True:
            above = distance()
            others = detect()
            others.append(above) # left forward right up
            
            others = [1,0,1,0]
            #others = [0,1,0,1]
            
            
            tactile(others)
            time.sleep(0.05)
            GPIO.output(GPIOS, False)
            time.sleep(0.2)
            # GPIO.output(GPIOS, False)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.output(GPIOS, False)
        #GPIO.output(GPIO_LEFT, False)
        #GPIO.output(GPIO_FORWARD, False)
        #GPIO.output(GPIO_RIGHT, False)
        #GPIO.output(GPIO_UP, False)
        GPIO.cleanup()
        print("Cleanup and output reset to false")
