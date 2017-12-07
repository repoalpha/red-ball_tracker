# USAGE
# python track.py
# python track.py --video BallTracking_01.mp4

# import the necessary packages
import argparse
import imutils
import cv2
from subprocess import call
import pigpio

try:
    call(["sudo","pigpiod"]) #start pigpio daemon if not running
except Exception:
    print("Pigpio Daemon running")


pi = pigpio.pi()

pi.set_mode(18, pigpio.OUTPUT)
pi.set_PWM_frequency(17, 100) #set pin 11 GPIO 17 on Pi-3 set Freq to 100hz
pi.set_PWM_frequency(18, 100) #set pin 12 GPIO 18 on Pi-3 set Freq to 100hz
pi.set_servo_pulsewidth(17, 1616) # set pan motor to front position based on how whole mount is positioned to base i.e. part number to front
pi.set_servo_pulsewidth(18, 1306) # set tilt motor to level position


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the (optional) video file")
args = vars(ap.parse_args())

# define the color ranges
colorRanges = [
	((160, 100, 100), (180, 255, 255), "red")] # green and blue removed i.e (57, 68, 0), (151, 255, 255), "blue"

# if a video path was not supplied, grab the reference to the webcam
if not args.get("video", False):
	camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
	camera = cv2.VideoCapture(args["video"])

panServoPosition = int(1616)           # pan servo position facing front relative to base
tiltServoPosition = int(1306)          # tilt servo position dead level
# keep looping
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()

    # if we are viewing a video and we did not grab a frame, then we have
    # reached the end of the video
    if args.get("video") and not grabbed:
            break

    # resize the frame, blur it, and convert it to the HSV color space
    frame = imutils.resize(frame, width=640)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    XFrameCenter = int(float(camera.get(cv2.CAP_PROP_FRAME_WIDTH)) / 2.0)
    YFrameCenter = int(float(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)) / 2.0)
    cv2.circle(frame, (int(XFrameCenter),int(YFrameCenter)), 3, (0, 255, 255), -1) # put a dot in the centre of the screen
    cv2.rectangle(frame, (int(XFrameCenter+100), int(YFrameCenter-75)), (int(XFrameCenter-100),int(YFrameCenter+75)), (255, 0, 0), 2)
    rightside = int(XFrameCenter+100)
    below =  int(YFrameCenter-75) 
    leftside = int(XFrameCenter-100)
    above =  int(YFrameCenter+75)
    #print("XFrameCenter", XFrameCenter, "YFrameCenter", YFrameCenter)
    

    # loop over the color ranges
    for (lower, upper, colorName) in colorRanges:
        # construct a mask for all colors in the current HSV range, then
        # perform a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask
        (_,cnts,_) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use it to compute
            # the minimum enclosing circle and centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            (cX, cY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only draw the enclosing circle and text if the radious meets
            # a minimum size
            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2) #circle
                cv2.circle(frame, (int(x),int(y)), 3, (0, 255, 0), -1) #draws green dot in middle of circle
                cv2.putText(frame, colorName, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2) #color word

                tilt = int(x)
                pan = int(y)
                #print("pan",int(x),"tilt",int(y))
                #print("x",int(x), "y", int(y))
                if  rightside >= x >= leftside and above >= y >= below:
                    panServoPosition, tiltServoPosition = (1616, 1306)
                    cv2.putText(frame, "Stop inside Box", (XFrameCenter, YFrameCenter-240), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                if x <= 320 and panServoPosition >= 500:
                    panServoPosition = panServoPosition - 20
                    X = str(panServoPosition)
                    cv2.putText(frame, X, (XFrameCenter, YFrameCenter -50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2) #color word
                if x > 320 and panServoPosition <= 2500:
                    panServoPosition = panServoPosition + 20
                    X = str(panServoPosition)
                    cv2.putText(frame, X, (XFrameCenter, YFrameCenter -50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2) #color word
                if y > 240 and tiltServoPosition >=900:# At value 1306 tilt is dead level
                    tiltServoPosition = tiltServoPosition - 20
                    Y = str(tiltServoPosition)
                    cv2.putText(frame, Y, (XFrameCenter, YFrameCenter+50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2) #color word
                if y < 240 and panServoPosition <=2300:
                    tiltServoPosition = tiltServoPosition + 20
                    Y = str(tiltServoPosition)
                    cv2.putText(frame, Y, (XFrameCenter, YFrameCenter+50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            panDutyCycle = (float(panServoPosition))# * 0.01) + 0.5) * 1000
            tiltDutyCycle = (float(tiltServoPosition))# * 0.01) + 0.5) * 1000
            #print (float(tiltServoPosition))
            #print(float(panServoPosition))
            pi.set_servo_pulsewidth(18, tiltDutyCycle) #vary duty cycle x direction here
            
            pi.set_servo_pulsewidth(17, panDutyCycle) #vary duty cycle x direction here

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
            break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
