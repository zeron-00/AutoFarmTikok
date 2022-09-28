import cv2
import numpy as np
import requests as rq

def link_to_img(link:str):
    return cv2.imdecode(np.frombuffer(rq.get(link).content, np.uint8), -1)[:,:,:3][:,:,::-1]

def bypass_object(image, return_ = 'image'):
        img = image.copy()
        def detect_yelow(img):
            img_new = cv2.inRange(img,(200,200,100),(255,230,150))&(img[:,:,1]-img[:,:,2]>50)&(img[:,:,0]-img[:,:,2]>75)
            return cv2.medianBlur(img_new*1,5)
        def detect_red(img):
            img_new = cv2.inRange(img,(220,150,130),(255,200,160))&(img[:,:,0]-img[:,:,1]>30)&(img[:,:,1]>img[:,:,2])
            return cv2.medianBlur(img_new*1,5)
        def detect_gray(img):
            img_new = cv2.inRange(img,(170,150,140),(201,181,180))&((img[:,:,0]-(img[:,:,0]*0.5+img[:,:,2]*0.5))<30)
            return cv2.medianBlur(img_new*1,5)
        def detect_violet(img):
            img_new = cv2.inRange(img,(160,90,170),(220,160,225))&(img[:,:,0]-img[:,:,1]>30)&(img[:,:,2]-img[:,:,1]>30)
            return cv2.medianBlur(img_new*1,5)
        def detect_green(img):
            img_new = cv2.inRange(img,(140,160,120),(180,230,180))&(img[:,:,1]-img[:,:,0]>30)&(img[:,:,1]-img[:,:,2]>30)
            return cv2.medianBlur(img_new*1,5)
        def detect_blue(img):
            img_new = cv2.inRange(img,(120,180,220),(160,210,255))&(img[:,:,1]>img[:,:,0])&(img[:,:,2]>img[:,:,1])
            return cv2.medianBlur(img_new*1,5)
        def contour_box(contour):
            con = contour[:,0]
            x1, x2, y1, y2 = con[:,0].min(), con[:,0].max(), con[:,1].min() ,con[:,1].max()
            return x1,y1,x2,y2
        yelow = detect_yelow(img)
        red = detect_red(img)
        gray = detect_gray(img)
        violet = detect_violet(img)
        green = detect_green(img)
        blue = detect_blue(img)
        z = np.zeros(img.shape[:2])
        list_image_mini = []
        list_rectangle = []
        for img_threshold in [yelow, red, gray, violet, green, blue]:
            # for con in cv2.findContours(img_threshold,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]:
            for con in cv2.findContours(img_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
                if cv2.contourArea(con)>100:
                    x1,y1,x2,y2 = contour_box(con)
                    cv2.rectangle(z,(x1,y1),(x2,y2),(255,0,0),2)
                    list_image_mini.append(np.uint8(cv2.threshold(cv2.cvtColor(img[y1-5:y2+5,x1-5:x2+5],cv2.COLOR_BGR2GRAY),0,255,cv2.THRESH_OTSU)[1]==0))
                    list_rectangle.append([x1,y1,x2,y2])
        p_min = {'%': 0,'box1':'','box2':''}
        
        for i in range(len(list_image_mini)):
            h,w = list_image_mini[i].shape[:2]
            im1 = cv2.resize(list_image_mini[i],(w,h))
            x1,y1,x2,y2 = list_rectangle[i]
            cv2.putText(img,str(i),(x1,y1),1,2,(255,0,255),2)
            cv2.rectangle(img,(x1,y1),(x2,y2),(128,128,128))
            for j in range(i+1,len(list_image_mini)):
                im2 = cv2.resize(list_image_mini[j],(w,h))
                x1,y1,x2,y2 = list_rectangle[i]
                v1 = (x2-x1)/(y2-y1)
                x1,y1,x2,y2 = list_rectangle[j]
                v2 = (x2-x1)/(y2-y1)
                pre2 = v1/v2 if v1<v2 else v2/v1
                pse_sub = (im1==im2).sum()/(im1.shape[0]*im1.shape[1])
                pse = np.max(cv2.matchTemplate(im1,im2,cv2.TM_CCOEFF_NORMED))
                pre_result = (pse**2)*(pre2**2)*(pse_sub**2)
                # print([i,j],np.round(pse,3),'%', np.round(pre2,3),'%', np.round(pse_sub,3), '%')
                if pre_result>p_min['%']:
                    p_min['%'] = pre_result
                    x1,y1,x2,y2 = list_rectangle[i]
                    p_min['box1'] = (x1,y1,x2,y2)
                    x1,y1,x2,y2 = list_rectangle[j]
                    p_min['box2'] = (x1,y1,x2,y2)
        # Trả về img
        if (return_ == 'image'):
            color = (255,0,0)
            x1,y1,x2,y2 = p_min['box1']
            cv2.rectangle(img,(x1-3,y1-3),(x2+3,y2+3),color,3) 
            x1,y1,x2,y2 = p_min['box2']
            cv2.rectangle(img,(x1-3,y1-3),(x2+3,y2+3),color,3)
            cv2.putText(img,str(np.round(p_min['%']*100,2))+'%',(30,50),1,2,(255,0,0),2)
           
            return img
        # Trả về 2 điểm
        else:
            x1,y1,x2,y2 = p_min['box1']
            point_1 = (x1+x2)//2, (y1+y2)//2
            x1,y1,x2,y2 = p_min['box2']
            point_2 = (x1+x2)//2, (y1+y2)//2
            return point_1, point_2
        
img = cv2.imread('{image}')[:,:,::-1]

# img_result = bypass_object(img, return_ = 'image')
# plt.imshow(img_result)
# plt.show()

p1, p2 = bypass_object(img,'234')
print(p1,'|',p2)