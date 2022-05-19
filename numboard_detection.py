from cv2 import drawContours
import imutils
import cv2
import numpy as np
from PIL import Image
import math


# 최초 모든 컨투어 찾기 작업
def pre_img_plate(src):
  gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
  gray = cv2.bilateralFilter(gray, -1, 10, 5)
  canny = cv2.Canny(gray, 30, 300)
  mode = cv2.RETR_LIST
  method = cv2.CHAIN_APPROX_SIMPLE
  contours, hierarchy = cv2.findContours(canny, mode, method)
  big_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
  return big_contours

def rect_detect(contour_list):
  contour_boxes = []
  cnt = 0
  for cont in contour_list:
    p = cv2.arcLength(cont, True)#외곽선 길이 반환
    ap = cv2.approxPolyDP(cont, 0.02 * p, True)#외곽선 근사화
    rect = 0
    flag = 0
    print(len(ap))
    if len(ap) == 4:
      rect = ap
      x, y, w, h = cv2.boundingRect(cont)

      x_min = x
      y_min = y
      x_max = x + w
      y_max = y + h

      contour_box = [x_min, y_min, x_max, y_max]
      contour_boxes.append(contour_box)
      break
    # elif (len(ap) == 6):
    #   exclude_num = 1
    #   flag = 1
    # elif (len(ap) == 5):
    #   exclude_num = 2
    #   flag = 2
    else:
      cnt += 1
  return rect, contour_boxes, cnt

def angle_cal(x1, x4, y1, y4):
  angle = math.degrees(math.atan2(y4 - y1, x4 - x1))
  return angle

def img_rotate(img, angle):
  height, width, channel = img.shape
  matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1)
  dst = cv2.warpAffine(img, matrix, (width, height))
  return dst

def pre_img_number(img):
  img = cv2.resize(img, (640, 480))
  gray1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  ret, gray2 = cv2.threshold(gray1, 150, 255, cv2.THRESH_BINARY)

  mode = cv2.RETR_LIST
  method = cv2.CHAIN_APPROX_SIMPLE
  contours1, hierarchy = cv2.findContours(gray2, mode, method)
  contour_boxes1 = []
  for contour1 in contours1:
      x, y, w, h = cv2.boundingRect(contour1)
      x_min1 = x
      y_min1 = y
      x_max1 = x + w
      y_max1 = y + h
      contour_box1 = [x_min1, y_min1, x_max1, y_max1]
      contour_boxes1.append(contour_box1)
  return contour_boxes1, img

def area_calculate(x_min, y_min, x_max, y_max):
  area = (x_max - x_min) * (y_max - y_min)
  return area

def optimal_rect(sorted_list):
  max_area = 0
  inner = []
  for idx, area_cont in enumerate(sorted_list):
    area = area_calculate(area_cont[0], area_cont[1], area_cont[2], area_cont[3])
    if area > max_area:
      max_area = area
      optimal_idx = idx
  optimal_area_contour = sorted_list[optimal_idx]
  for i in range(len(sorted_list)):
    if((optimal_area_contour[0] < sorted_list[i][0]) and (optimal_area_contour[2] > sorted_list[i][2])
            and (optimal_area_contour[1] < sorted_list[i][1]) and (optimal_area_contour[3] > sorted_list[i][3])):

      inner.append(sorted_list[i])
  return inner

def inner_draw(inner, img):
  contour_boxes1 = []
  for i in inner:
    x_min1 = i[0]
    y_min1 = i[1]
    x_max1 = i[2]
    y_max1 = i[3]
    contour_box1 = [x_min1, y_min1, x_max1, y_max1]
    contour_boxes1.append(contour_box1)
    cv2.rectangle(img, (x_min1, y_min1), (x_max1, y_max1), (0, 0, 255), 3)
  return contour_boxes1, img


def x_compare(contour_list):
  contour_lists = []
  for i in range(len(contour_list)):
    if(contour_list[i][0] == contour_list[i-1][0]):
      contour_list[i - 1].append('8')
    if(contour_list[i][0] != contour_list[i-1][0]):
      contour_lists.append(contour_list[i])
  return contour_lists


def percent_cal(num1, num2):
  percent = (num1 / num2) * 100
  return percent


def detect1(lists):
    cal_x = lists[2]-lists[0]
    percent_x = (cal_x / max_x)*100
    return percent_x


def cal_0(lists):
    cnt = 0
    for i in lists:
        if(i == 0):
          cnt += 1
    return cnt

src = cv2.imread('car/d7217.jpg')
src_err = src.copy()
src = imutils.resize(src, width=650)

src_copy = src.copy()
big_contours = pre_img_plate(src) #find all contour
rect, contour_list, cnt = rect_detect(big_contours)

if cnt == 2:
  src = imutils.resize(src_err, width=1050)
  src_copy = src.copy()
  big_contours = pre_img_plate(src) #find all contour
  rect, contour_list, cnt = rect_detect(big_contours)

if cnt >= 10:
  if cnt == 30:
    src = imutils.resize(src_err, width = 750)
  else:
    src = imutils.resize(src_err, width=640)
  src_copy = src.copy()
  big_contours = pre_img_plate(src) #find all contour
  rect, contour_list, cnt = rect_detect(big_contours)

xmin = contour_list[0][0]
xmax = contour_list[0][2]
ymin = contour_list[0][1]
ymax = contour_list[0][3]
print(xmin)
cv2.drawContours(src_copy, [rect], -1, (0, 255, 0), 3)

rect = np.reshape(rect, (4, -1))
rec_x = []
rec_y = []
for rec in rect:
  rec_x.append(rec[0])
  rec_y.append(rec[1])
rec_x = sorted(rec_x)
rec_y = sorted(rec_y)

x1, x2, x3, x4 = rec_x[1], rec_x[0], rec_x[2], rec_x[3]
y1, y2, y3, y4 = rec_y[0], rec_y[2], rec_y[3], rec_y[1]

#회전 처리
src_rotat = src.copy()
rotat = src_rotat[ymin:ymax, xmin:xmax]

angle = angle_cal(x1, x4, y1, y4)
flag = 0
if angle > 5.0:
  flag = 1
  rotation_img = img_rotate(rotat, angle + 1)  # 경사가 있다면 회전
else:
  flag = 2
  rotation_img = rotat  # 경사가 없다면 회전x


roi_copy = rotation_img.copy()
contour_boxes, number_plate = pre_img_number(roi_copy)
print(number_plate)
sorted_contourboxes = sorted(contour_boxes, key=lambda x: x[0])
src1 = number_plate.copy()
src2 = src1.copy()
src3 = src2.copy()
ex1_img = src1.copy()
inner = optimal_rect(sorted_contourboxes)  # 가장 큰 contour외부는 빼줌
contour_boxes1, src1 = inner_draw(inner, src1)

all_area = src1.shape[1] * src1.shape[0]
contour_boxes2 = []
for cnt in contour_boxes1:
  sub = cnt[2] - cnt[0]  # 전체에서 가로 비율
  area = area_calculate(cnt[0], cnt[1], cnt[2], cnt[3])  # 전체에서 넓이 비율
  sub_per = (sub/all_area)*1000
  area_per = (area/all_area)*100
  if area_per > 0.3 and sub_per < 0.5:  # 6
    contour_boxes2.append(cnt)



# car2에서 처럼 맨 앞이랑 맨 뒤 나사 노이즈 제거
last_idx = len(contour_boxes2)-1
print(contour_boxes2)

first_area = area_calculate(
    contour_boxes2[0][0], contour_boxes2[0][1], contour_boxes2[0][2], contour_boxes2[0][3])
last_area = area_calculate(contour_boxes2[last_idx][0], contour_boxes2[last_idx]
                     [1], contour_boxes2[last_idx][2], contour_boxes2[last_idx][3])
last_area2 = area_calculate(contour_boxes2[last_idx-1][0], contour_boxes2[last_idx-1]
                      [1], contour_boxes2[last_idx-1][2], contour_boxes2[last_idx-1][3])
if last_area < 5000:
  del contour_boxes2[last_idx]
if first_area < 5000:
  del contour_boxes2[0]
for contour_box in contour_boxes2:
  cv2.rectangle(src2, (contour_box[0], contour_box[1]),
                (contour_box[2], contour_box[3]), (0, 0, 255), 3)

src_number = src2.copy()
src_number = src_number[contour_boxes2[0][1] - 30:contour_boxes2[0][3] +
                        30, contour_boxes2[0][0] - 5:contour_boxes2[len(contour_boxes2)-1][2] + 30]

img_ex1 = ex1_img[contour_boxes2[0][1] - 35:contour_boxes2[0][3] + 30,
                  contour_boxes2[0][0] - 5:contour_boxes2[len(contour_boxes2)-1][2] + 30]

img_ex1 = cv2.resize(img_ex1, (640, 480))
gray3 = cv2.cvtColor(img_ex1, cv2.COLOR_BGR2GRAY)
ret, gray3 = cv2.threshold(gray3, 150, 255, cv2.THRESH_BINARY)

mode = cv2.RETR_LIST
method = cv2.CHAIN_APPROX_SIMPLE
contours1, hierarchy = cv2.findContours(gray3, mode, method)

contour_boxes3 = []
for contour1 in contours1:
    x, y, w, h = cv2.boundingRect(contour1)
    x_min1 = x
    y_min1 = y
    x_max1 = x + w
    y_max1 = y + h
    contour_box3 = [x_min1, y_min1, x_max1, y_max1]
    contour_boxes3.append(contour_box3)
    cv2.rectangle(img_ex1, (x_min1, y_min1), (x_max1, y_max1), (0, 0, 255), 3)

contour_boxes3 = sorted(contour_boxes3, key=lambda x: x[0])
del contour_boxes3[0]
# 너무 작은 컨투어 노이즈 제거
contour_boxes4 = []
for i in contour_boxes3:
  area_c = area_calculate(i[0], i[1], i[2], i[3])
  if area_c > 1000:
    contour_boxes4.append(i)

#print(contour_boxes4)
cv2.imshow('asd', img_ex1)

src3 = img_ex1.copy()
sorted_contourboxes = contour_boxes4
contour_out_in = []  # 4,6,8,9,0과 같이 외부와 내부가 같은 list에
contour_out = []  # 4,6,8,9,0에서 외부 내부가 다른 list에
# print(sorted_contourboxes)
for i in range(len(sorted_contourboxes)):
  cnt = 0
  for j in range(len(sorted_contourboxes)):
    # 4,6,8,9,0처럼 내부에 또 컨투어가 있는 숫자들을 판단
    # 즉, 외부 컨투어보다 작은 내부 컨투어가 잇으면 그 외부랑 내부컨투어만 contour_out_in에 추가
    if((sorted_contourboxes[i][0] < sorted_contourboxes[j][0]) and (sorted_contourboxes[i][2] > sorted_contourboxes[j][2])
       and (sorted_contourboxes[i][1] < sorted_contourboxes[j][1]) and (sorted_contourboxes[i][3] > sorted_contourboxes[j][3])):
      cnt += 1
      # 4,6,8,9,0 내부 외부 좌표를 한 번에 넣기
      contour_out_in.append(sorted_contourboxes[i] + sorted_contourboxes[j])

      #contour_out에 4,6,8,9,0의 외부 컨투어좌표와 내부 컨투어 좌표를 나누어서 넣음 -->>즉 이 리스트는 내부컨투어를 가지는 숫자들에 대한 컨투어 좌표 집합
      if sorted_contourboxes[i] not in contour_out:
        contour_out.append(sorted_contourboxes[i])

      contour_out.append(sorted_contourboxes[j])
  #sorted_contourboxes[i].append(cnt)

#print('sorted_contourboxes',sorted_contourboxes)
#print('contour_out_in', contour_out_in)
#print('contour out', contour_out)

contour_in_x = []  # 내부contour가 없는 1,2,3,5,7
for i in range(len(sorted_contourboxes)):
  if (sorted_contourboxes[i] not in contour_in_x) and (sorted_contourboxes[i] not in contour_out):
      #print(sorted_contourboxes[i])
      contour_in_x.append(sorted_contourboxes[i])

contour_out_all = []  # 정리된 전체 contour
contour_in_out_all = sorted(contour_out_in + contour_in_x, key=lambda x: x[0])
print('전체 숫자 contour 좌표 : ', contour_in_out_all)
print("-----------------------------------------------------------------------")

######################### 외부. 내부 contour 좌표 나누기 #########################

# 번호판 내부에 들어온 나사 노이즈 제거
cont = []
first_y = contour_in_out_all[0][1]
for i in contour_in_out_all:
  if i[1] < first_y + 36:
    cont.append(i)
#print(cont)
for con in cont:
    cv2.rectangle(src3, (con[0], con[1]), (con[2], con[3]), (0, 0, 255), 3)


# x길이 최대값 구하기
max_x = 0
for p in contour_in_out_all:
    max_pre_x = p[2]-p[0]
    if max_x < max_pre_x:
      max_x = max_pre_x

######################### 0,4,8,9,6 숫자 판단 #########################

# 8은 내부에 컨투어가 2개니깐 하나는 무시해주려고 x_compare함수로 판단
contour_in_out_all = x_compare(cont)


number_list = []
for idx, out in enumerate(contour_in_out_all):
  # 길이가 4이면 내부 컨투어니깐 나중에 하려고 number_list에 그냥 좌표 그래로 추가
  if(len(out) == 4):
    number_list.append(out)
  # 8은 '8'이 추가되면서 길이가 9
  elif(len(out) == 9):
    number_list.append(8)
  # 길이가 8인 남은 숫자들은 0,4,9,6
  elif(len(out) == 8):
    y_center_out = (out[3]+out[1]) / 2
    y_center_in = (out[7]+out[5]) / 2
    #0은 내부와 외부 컨투어의 크기의 비율을 비교
    if(percent_cal(area_calculate(out[4], out[5], out[6], out[7]), area_calculate(out[0], out[1], out[2], out[3])) >= 23):
      number_list.append(0)
    #elif(y_center_out > y_center_in):
    #elif(abs(y_center_out - y_center_in) < 100):
    elif((y_center_out > y_center_in) or (abs(y_center_out - y_center_in)) < 20):
      #내부랑 외부 컨투어의 중심 좌표가 매우 가까움
      if(90 <= percent_cal(y_center_in, y_center_out) <= 110):
        number_list.append(4)
      else:
        number_list.append(9)
      #외부 컨투어의 중심이 내부 컨투어보다 작음
    elif(y_center_out < y_center_in):
      number_list.append(6)


######################### 1,2,3,5,7 숫자 판단 #########################

gray0 = cv2.cvtColor(src3, cv2.COLOR_BGR2GRAY)
ret, gray = cv2.threshold(gray0, 150, 255, cv2.THRESH_BINARY)

# 1확인 크기의 비율이 다른 숫자들에 비해 작음
x_idx = -1
for idx, number in enumerate(number_list):
  if (number == 4 or number == 6 or number == 8 or number == 9 or number == 0):
    continue
  else:
    if (detect1(number) < 70):
      x_idx = idx
    if(x_idx != -1):
      number_list[x_idx] = 1

# 2,7 확인
# 2의 밑부분은 검정색이 더 많음
idx_2 = -1
idx_7 = -1
for idx, number in enumerate(number_list):
  if(number == 4 or number == 6 or number == 8 or number == 9 or number == 0 or number == 1):
    continue
  else:
    length_bottom = len(gray[number[3]-10, number[0]:number[2]])

    list_gray = gray[number[3]-10, number[0]:number[2]]
    cnt_0 = cal_0(list_gray)
    #print(percent_cal(cnt_0, length_bottom))
    if(percent_cal(cnt_0, length_bottom) > 85.0):
      idx_2 = idx
    if(percent_cal(cnt_0, length_bottom) < 30.0):
      idx_7 = idx

    if(idx_2 != -1):
      number_list[idx_2] = 2
    if(idx_7 != -1):
      number_list[idx_7] = 7

# 3, 5 확인

idx_3 = -1
idx_5 = -1
for idx, number in enumerate(number_list):

  if (number == 4 or number == 6 or number == 8 or number == 9 or number == 0 or number == 1 or number == 2 or number == 7):
    continue
  else:
    center_xmin = number[0]
    center_xmax = number[2]
    center_y = int((number[1]+number[3])/2)
    center_x_20 = int(0.2*center_xmax + 0.8*center_xmin)

    line_img = cv2.line(src, (center_xmin, center_y),
                        (center_x_20, center_y), (255, 255, 0), 2)

    check_0 = gray[center_y, center_x_20]
    list_gray2 = gray[center_y, center_xmin:center_x_20]
    cnt_black = cal_0(list_gray2)
    #print(cnt_black)
    if(cnt_black) > 5:
      idx_5 = idx
    else:
      idx_3 = idx

    if(idx_3 != -1):
      number_list[idx_3] = 3
    if(idx_5 != -1):
      number_list[idx_5] = 5
print(number_list)
#"""


#cv2.imshow('s', src_copy)

cv2.waitKey()
cv2.destroyAllWindows()