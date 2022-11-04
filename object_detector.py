import cv2
import numpy as np


class HomogeneousBgDetector():
    def __init__(self):
        pass

    def detect_objects(self, frame):
        # Convert Image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # blur img
        blurimg = cv2.cv2.GaussianBlur(gray, (5, 5), 1)
        #circle

        #circles = cv2.HoughCircles(gray,cv2.CV_HOUGH_GRADIENT,1,parm1=100,param2=30,maxRaduis=0,minRaduis=0)
        #circles = np.uint16(np.around(circles))
        #for i in circles[0, :]:
         #   cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
          #  cv2.circle(img, (i[0], i[1], 2, (0, 255, 0), 3))

        # Create a Mask with adaptive threshold
        mask = cv2.adaptiveThreshold(blurimg, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.imshow("blur", blurimg)
        cv2.imshow("mask", mask)
        objects_contours = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 2000:
                #cnt = cv2.approxPolyDP(cnt, 0.03*cv2.arcLength(cnt, True), True)
                objects_contours.append(cnt)

        return objects_contours

    # def get_objects_rect(self):
    #     box = cv2.boxPoints(rect)  # cv2.boxPoints(rect) for OpenCV 3.x
    #     box = np.int0(box)