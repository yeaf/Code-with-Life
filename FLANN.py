import numpy as np
import cv2
from skimage import transform


def calc_length(point1, point2):
    x = (point1[0] - point2[0]) ** 2
    y = (point1[1] - point2[1]) ** 2
    return (x + y) ** 0.5

MIN_MATCH_COUNT = 10
#读入模板
dst_img = cv2.imread('C:/Users/Administrator/Desktop/12.png', 0)
#读取检测
ori_img = cv2.imread('C:/Users/Administrator/Desktop/10.jpg', 1)

sift = cv2.xfeatures2d.SIFT_create()
kp1, des1 = sift.detectAndCompute(dst_img, None)
kp2, des2 = sift.detectAndCompute(ori_img, None)

index_params = dict(algorithm = 1, trees = 5)
search_params = dict(checks = 50)
flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des1,des2,k=2)

good = []
for m,n in matches:
    if m.distance < 0.7*n.distance:
        good.append(m)

if len(good) > MIN_MATCH_COUNT:
   
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
    matchesMask = mask.ravel().tolist()
    h,w = dst_img.shape
    pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
    ori = cv2.perspectiveTransform(pts, M)

    dst = [(ele[0][0], ele[0][1]) for ele in ori]
    length_width = int(max(calc_length(dst[3], dst[0]), calc_length(dst[1], dst[2])))
    length_hight = int(max(calc_length(dst[0], dst[1]), calc_length(dst[2], dst[3])))
    tar = np.float32([[0,0],[length_hight,0],[length_hight,length_width], [0,length_width]])
    warp_matrix = cv2.getPerspectiveTransform(ori, tar)
    res = cv2.warpPerspective(ori_img, warp_matrix, (length_hight, length_width))
    rot_img = transform.rotate(res[::-1,:], -90, resize=True)

    img_new = cv2.resize(rot_img, (720, 960), interpolation=cv2.INTER_CUBIC)
    cv2.imshow("original", img_new)
    roi_list = list()

    rois = np.array([
		[[45, 15], [260, 15], [260, 50], [45, 50]],
	  
		[[160, 275], [690, 275], [690, 365], [160, 365]],

        [[220, 365], [690, 365], [690, 600], [220, 600]],
        
		[[45, 885], [200, 885], [200, 920], [45, 920]],
		])
    
    for roi in rois:
        xmin = np.min([coordinates[0] for coordinates in roi])
        xmax = np.max([coordinates[0] for coordinates in roi])
        ymin = np.min([coordinates[1] for coordinates in roi])
        ymax = np.max([coordinates[1] for coordinates in roi])
        roi_list.append((xmin, xmax, ymin, ymax))

    result = np.zeros_like(img_new)
    for roi in roi_list:
        result[roi[2]:roi[3], roi[0]:roi[1]] = img_new[roi[2]:roi[3], roi[0]:roi[1]]

    cv2.imshow("result", result)
    imm = cv2.normalize(result, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
    cv2.imwrite("C:/Users/Administrator/Desktop/1010.jpg", imm)
    cv2.waitKey(0)
else:
    print("Not enough matches are found - %d/%d") % (len(good),MIN_MATCH_COUNT)
    matchesMask = None




