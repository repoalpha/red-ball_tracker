# red-ball_tracker
This application is designed for the raspberry pi using python 3.4.2 on jessie. A webcam is mounted on a pan tilt mount in this case a logitech 920. The application draws an on screen bounding box and screen centre target mostly for calibration purposes. Once a redball is brought into the field of view Open CV will detect the ball, a yellow circle is drawn indicating the target has been acquried with a centroid dot in the middle. Servo motor position numbers are displayed on screen for x,y and the motors will centre on the red ball target. As the ball is moved around the motors will track the ball motion. Once the target is lost the servo motors will stop. The bounding box is an area where the motors typically will cease operation since the object is fairly well centred and should not require continious hunting. Once the ball leaves the bounding box area the motors will track the object to keep it within the centre of the web cams field of view and on screen display.

![alt text](https://raw.githubusercontent.com/repoalpha/red-ball_tracker/tracker_screenshot.png

# Dependencies
- open cv version 3.2
- imutils
- pigpiod

# A note about pigpiod
The pigpiod Daemon needs to be run first for a few seconds before starting the calibrate tool. This Daemon is used in place of the Rpi.gpio module normally used as the servo jitter is herendous due to timing variations of the debian OS kernel. You can leave the pipiod Daemon running the same can't be said for the native pwm used by the pi. Pigpoid could be run from boot if required by modifying the init.d file, I do not since I may need resources for other projects at times so I keep it flexible. The camera I used is a USB logitech 920 not the raspberry pi type hence the bigger servos and mount. 

To start the pigpiod Daemon use:
> sudo pigpiod

To stop the Daemon:
> pkill pigpiod

# The hardware
I used the Hitech HS-645 servos and a SPT-100 pan & tilt mount with the matching HS-645 motor brackets to hold the pan motor to a base board.
