import cv2, time, pandas 
from datetime import datetime 
from time import sleep,time
import time
import math
from datetime import datetime

dist_from_camera =  float(input("Enter Calibration Length(in meters): "))
theta = float(input("Enter angle of view of Camera: "))
object_count = 0; speed = 0.0; speed_kmph = 0.0
road_length = dist_from_camera*math.tan(theta)*2
static_back = None; motion_list = [ None, None ]; time = []
df = pandas.DataFrame(columns = ["Start", "End"])
video = cv2.VideoCapture(0)
check, frame = video.read()
sleep(2)
frame_count = 0; last_frame_motion = 0; delta_t = 0
motion = 0; stk = []; x_cor = []; t = datetime.now()

#continuous video stream
while True:
    check, frame = video.read()
    if motion==0:
        last_frame_motion = 0
    else:
        last_frame_motion = 1
    motion = 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    if static_back is None: 
        static_back = gray 
        continue
    #elif(frame_count%10!=0):
        #static_back = gray
    
    diff_frame = cv2.absdiff(static_back, gray)
    thresh_frame = cv2.threshold(diff_frame, 25, 255, cv2.THRESH_BINARY)[1] 
    thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)

    #moving regions
    
    (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    for contour in cnts: 
        if cv2.contourArea(contour) < 10000: 
            continue
        motion = 1
        
        (x, y, w, h) = cv2.boundingRect(contour)
        centroid_x = int((x+x+w)/2)
        centroid_y = int((y+y+h)/2)
        t = datetime.now()
        if motion==1 and last_frame_motion==0:
            object_count += 1
            stk.append(t)
            x_cor.append(centroid_x)

        #region marked in green
        img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        #centroid
        cv2.circle(frame, (centroid_x,centroid_y), 5,(0, 0, 255),-1)
        cv2.putText(img, "Object No: "+str(object_count), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
        #saving the image of tracked object
        if(centroid_x>300)and(centroid_x<340):
            obj_img = img[y:y+h, x:x+w]
            cv2.imwrite("Object "+str(object_count)+".png", obj_img)

    if motion==0 and last_frame_motion==1:
            delta_t = t - stk[0]
            dx = abs(centroid_x - x_cor[0])
            stk.pop()
            x_cor.pop()
            str_time = str(delta_t)
            str_time = str_time.split(':')
            sec =  int(str_time[0])*3600 + int(str_time[1])*60 + float(str_time[2])
            try :
                speed = road_length/sec
            except:
                print("Error: Object Moved Too Fast")
            speed_kmph = 18/5*speed
            print("Velocity of Object %d: %.2f m/s; %.2f km/h" %(object_count, speed, speed_kmph))
    
    #cv2.imshow("Gray Frame", gray)
    #cv2.imshow("Difference Frame", diff_frame)
    #cv2.imshow("Background Frame",static_back)
    #cv2.imshow("Threshold Frame", thresh_frame)
    
    cv2.putText(frame, "Velocity of Object %d: %.2f m/s; %.2f km/h" %(object_count, speed, speed_kmph),
                (20,400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (252,68,69), 2)
    cv2.namedWindow("Color Frame", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Color Frame",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Color Frame", frame)
    
    
    frame_count += 1
    key = cv2.waitKey(1)
    #reset the threshold frame
    if key == ord('r'):
        static_back = gray
    #exit
    if key == ord('q'):
        break
video.release()
cv2.destroyAllWindows() 
