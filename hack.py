

import numpy as np
import cv2

cap = cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (5120,480))

for n in range(5):
    # Capture frame-by-frame
    ret, frame = cap.read()

    out.write(frame)

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# When everything done, release the capture
cap.release()
