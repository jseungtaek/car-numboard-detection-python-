import imutils
import cv2
import numpy as np
from PIL import Image


# 최초 모든 컨투어 찾기 작업
def pre_img_plate(img):
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  gray = cv2.bilateralFilter(gray, -1, 10, 5)
  canny = cv2.Canny(gray, 30, 300)
  mode = cv2.RETR_LIST
  method = cv2.CHAIN_APPROX_SIMPLE
  contours, hierarchy = cv2.findContours(canny, mode, method)
  big_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
  #print(big_contours)
  return big_contours

def rect_detect(contour_list):
  contour_boxes = []
  for cont in contour_list:
    p = cv2.arcLength(cont, True)
    ap = cv2.approxPolyDP(cont, 0.018 * p, True)
    #print(len(ap))
    flag = 0
    rect = 0
    if len(ap) == 4:
      rect = ap
      x, y, w, h = cv2.boundingRect(cont)

      x_min = x
      y_min = y
      x_max = x + w
      y_max = y + h

      contour_box = [x_min, y_min, x_max, y_max]
      #print(contour_box)
      contour_boxes.append(contour_box)
      break
    else:
      flag = 2
  return rect, contour_boxes, flag

src = cv2.imread('car/d4507.jpg')
src = cv2.resize(src, (0, 0), fx=0.3, fy=0.3,interpolation = cv2.INTER_AREA)


src_copy = src.copy()
big_contours = pre_img_plate(src)
rect, contour_list, flag = rect_detect(big_contours)

xmin = contour_list[0][0]
xmax = contour_list[0][2]
ymin = contour_list[0][1]
ymax = contour_list[0][3]

cv2.drawContours(src_copy, [rect], -1, (0, 255, 0), 3)

cv2.imshow('s', src_copy)

cv2.waitKey()
cv2.destroyAllWindows()