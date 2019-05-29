import numpy as np
import cv2
import skvideo.io

path = "/home/neel/IITB/misc/video.mp4"

videogen = skvideo.io.vreader(path)

for frame in videogen:
	frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
	cv2.imshow("frame", frame)

	if cv2.waitKey(50) & 0xFF == ord('q'):
		break