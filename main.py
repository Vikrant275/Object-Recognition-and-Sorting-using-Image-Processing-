import cv2
from object_detector import *
import numpy as np
import time
import os
import serial

# User area specification
Input_area = input("Enter")
ser = serial.Serial(port='COM1', baudrate=9600)
ser.close()
ser.open()
# Load Aruco detector
parameters = cv2.aruco.DetectorParameters_create()
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)


# Load Object Detector
detector = HomogeneousBgDetector()

# Load Cap
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 730)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1260)

while True:
    _, img = cap.read()
    canny = cv2.Canny(img, 150, 170)
    # Get Aruco marker
    corners, _, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
    if corners:

        # Draw polygon around the marker
        int_corners = np.int0(corners)
        cv2.polylines(img, int_corners, True, (0, 0, 255), 5)

        # Aruco Perimeter
        aruco_perimeter = cv2.arcLength(corners[0], True)

        # Pixel to cm ratio
        pixel_cm_ratio = aruco_perimeter / 20

        contours = detector.detect_objects(img)

        # Draw objects boundaries
        for cnt in contours:
            # Get rect
            rect = cv2.minAreaRect(cnt)
            (x, y), (w, h), angle = rect
            # Get Width and Height of the Objects by applying the Ratio pixel to cm
            object_width = w / pixel_cm_ratio
            object_height = h / pixel_cm_ratio

            # Display rectangle
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
            cv2.polylines(img, [box], True, (255, 0, 0), 2)
            cv2.putText(img, "Width {} cm".format(round(object_width, 1)), (int(x - 100), int(y - 20)), cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
            cv2.putText(img, "Height {} cm".format(round(object_height, 1)), (int(x - 100), int(y + 15)), cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
            #print(object_height)
            #print(object_width)
            area = object_height*object_width
            print("area is: ", area)
            for contour in contours:
                approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, closed=True), True)
                cv2.drawContours(img, [approx], 0, (0, 255, 0), 3)
                a = approx.ravel()[0]
                b = approx.ravel()[1]

                if len(approx) == 3:
                    cv2.putText(img, "Triangle", (a, b), cv2.FONT_HERSHEY_PLAIN, 1, (46, 156, 225), 3)
                elif len(approx) == 4:
                    cv2.putText(img, "Square", (a, b), cv2.FONT_HERSHEY_COMPLEX, 1, (200, 0, 225), 3)

                elif len(approx) == 6:
                    if area == Input_area:
                        cv2.putText(img, "PASS", (a, b), cv2.FONT_HERSHEY_COMPLEX, 1, (200, 0, 225), 3)
                        ser.write(b'0')

                elif (len(approx) != 6):
                    cv2.putText(img, "Manufacturer defect", (a, b), cv2.FONT_HERSHEY_COMPLEX, 1, (200, 0, 225), 3)
                    ser.write(b'1')
                    #else:
                     #   cv2.putText(img, "Size", (a, b), cv2.FONT_HERSHEY_COMPLEX, 1, (200, 0, 225), 3)
                       # ser.write(b'2')

                else:
                    cv2.putText(img, ".........", (a, b), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 225), 3)
                    #ser.write(b'0')





    cv2.imshow("Size", img)
    cv2.imshow("canny",canny)
    key = cv2.waitKey(1)
    if key == 2:
        break

cap.release()
cv2.destroyAllWindows()

