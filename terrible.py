# import the necessary packages
from __future__ import print_function
from imutils.video import VideoStream
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import FileVideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import sys


def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])
 
	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])
 
	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)
 
	# return the eye aspect ratio
	return ear

def blackscreen(): #Create function that will turn off screen
    input()
    if sys.platform.startswith('win'): #If system is Windows
        #imports from windows
        import win32gui
        import win32con
        from os import getpid, system
        from threading import Timer
	
        def force_exit():
            pid = getpid()
            system('taskkill /pid %s /f' % pid)
	
        t = Timer(1, force_exit)
        t.start()
        SC_MONITORPOWER = 0xF170 #variable that will change the power in the screen to zero
        win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, SC_MONITORPOWER, 2)
        t.cancel()


 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
	help="path to output video file")
ap.add_argument("-p", "--shape-predictor", required=True,
	help="path to facial landmark predictor")
args = vars(ap.parse_args())

# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold
EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 3
 
# initialize the frame counters and the total number of blinks
COUNTER = 0
TOTAL = 0

# initialize the video stream and allow the camera
# sensor to warmup
print("[INFO] warming up camera...")
vs = VideoStream(usePiCamera=False).start()
time.sleep(2.0)
 
# initialize the FourCC, video writer, dimensions of the frame, and
# zeros array
fourcc = cv2.VideoWriter_fourcc(*'XVID')
writer = None
(h, w) = (None, None)
zeros = None

# loop over frames from the video stream
#for n in range(90):
while (True):
	# grab the frame from the video stream and resize it to have a
	# maximum width of 300 pixels
    frame = vs.read()
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])
    frame = imutils.resize(frame, width=450)
    # grab the indexes of the facial landmarks for the left and
    # right eye, respectively
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    # start the video stream thread
    print("[INFO] starting video stream thread...")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # detect faces in the grayscale frame
    rects = detector(gray, 0)

    # loop over the face detections
    for rect in rects:
		# determine the facial landmarks for the face region, then
		# convert the facial landmark (x, y)-coordinates to a NumPy
		# array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
 
		# extract the left and right eye coordinates, then use the
		# coordinates to compute the eye aspect ratio for both eyes
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
 
		# average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        		# compute the convex hull for the left and right eye, then
		# visualize each of the eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        		# check to see if the eye aspect ratio is below the blink
		# threshold, and if so, increment the blink frame counter
        if ear < EYE_AR_THRESH:
            COUNTER += 1
            print('blink')
            blackscreen()
 
		# otherwise, the eye aspect ratio is not below the blink
		# threshold
        else:
            print('no blibk')
			# if the eyes were closed for a sufficient number of
			# then increment the total number of blinks
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1
 
			# reset the eye frame counter
            COUNTER = 0

    # check if the writer is None
    if writer is None:
		# store the image dimensions, initialzie the video writer,
		# and construct the zeros array
        (h, w) = frame.shape[:2]
        writer = cv2.VideoWriter(args["output"], fourcc, 30.0,
        (w * 2, h * 2), True)
        zeros = np.zeros((h, w), dtype="uint8")

        	# break the image into its RGB components, then construct the
    # RGB representation of each frame individually
    (B, G, R) = cv2.split(frame)
    R = cv2.merge([zeros, zeros, R])
    G = cv2.merge([zeros, G, zeros])
    B = cv2.merge([B, zeros, zeros])
 
	# construct the final output frame, storing the original frame
	# at the top-left, the red channel in the top-right, the green
	# channel in the bottom-right, and the blue channel in the
	# bottom-left
    output = np.zeros((h * 2, w * 2, 3), dtype="uint8")
    output[0:h, 0:w] = frame
    output[0:h, w:w * 2] = R
    output[h:h * 2, w:w * 2] = G
    output[h:h * 2, 0:w] = B
	# write the output frame to file
    writer.write(output)
# do a bit of cleanup
print("[INFO] cleaning up...")
vs.stop()
writer.release()
