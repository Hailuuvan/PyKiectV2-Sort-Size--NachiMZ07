import cv2
import numpy as np
import time
import XYZ_realworld

class image_recognition:
    XYZ = XYZ_realworld.XYZ_realworld()
    
    def __init__(self,print_status=True, write_images=False,
                image_Path="D:\DATN\FinalProject\Calib\Captures/",
                testing_Path="D:\DATN\FinalProject\Calib\Captures/",
                preview_images=False,preview_autoclose=True,print_img_labels=True):
        
        self.IMGDIR=image_Path
        self.TESTDIR=testing_Path
        self.PREVIEW_IMAGES=preview_images
        self.PREVIEW_AUTOCLOSE=preview_autoclose
        self.PRINT_STATUS=print_status
        self.PRINT_IMG_LABELS=print_img_labels
        self.WRITE_IMAGES=write_images

        #valid contour parameters limits (in pixels)
        #self.MIN_AREA=900 #30x30
        #self.MAX_AREA=90000 #300x300
        # Diện tích tối thiểu
        self.MIN_AREA = int(900 * (1920/640) * (1080/480))  # 30x30

        # Diện tích tối đa
        self.MAX_AREA = int(90000 * (1920/640) * (1080/480))  # 300x300

            #aspect ratio width/height
        self.MIN_ASPECTRATIO=1/5
        self.MAX_ASPECTRATIO=5

        #OstuSensitivity
        self.OtsuSensitivity=22
        
        self.XYZ_real = [[0],[0],[0]]
        self.rect_theta = [[0],[0],[0]]
        self.area = []

        # Các biến khác
        self.x_real = []
        self.y_real = []
        self.z_real = []
        
        self.area = 0
    def test_objectDetect(self,bgFile,targetFile):

        img=cv2.imread(self.TESTDIR+bgFile+".jpg")
        bg=cv2.imread(self.TESTDIR+targetFile+".jpg") 
        self.run_detection(img,bg,True)

    def run_detection(self,img,bg,testRun=False):
           
        obj_count, contours_detected, contours_validindex=self.detectObjects(img,bg)

        obj_count, detected_points, img_output=self.detectionOutput(img,obj_count,contours_validindex,contours_detected)

        return obj_count, detected_points, img_output
    
    def detectObjects(self, image, bg_img,externalContours=True):

        img=image.copy()           
        background_img=bg_img.copy()


        # Process Image Difference
        self.diff=self.calculateDifference_Otsu(img,background_img)
        
        # ///////////// Find the Contours
        # use RETR_EXTERNAL for only outer contours... use RETR_TREE for all the hierarchy
        if externalContours==True:
            contours_detected, hierarchy = cv2.findContours(self.diff, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours_detected, hierarchy = cv2.findContours(self.diff, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            
        #calculate key variables
        height, width, channels = img.shape

        # /////// identify the VALID Contours
        contours_validindex= self.identify_validcontours(contours_detected,height,width)
        
        

        obj_count=len(contours_validindex)
        self.printStatus("valid contours "+ str(obj_count))

        return obj_count, contours_detected, contours_validindex

    def detectionOutput(self, image, obj_count, validcontours, diff_contours):

        img_output=image.copy()

        detected_points=[]
        
        if (len(validcontours)>0):
            for i in range(0,len(validcontours)):
                
                
                cnt=diff_contours[validcontours[i]]
    
                #get rectangle detected_points
                x,y,w,h=cv2.boundingRect(cnt)
                # Vẽ hộp giới hạn xung quanh đối tượng
                # cv2.rectangle(img_output, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Vẽ khoanh vùng đối tượng
                #cv2.drawContours(img_output, [cnt], -1, (255, 0, 0), 2)
                
                # Tìm góc xoay va dien tich của vật
                if len(cnt) >0:
                    self.rect_theta = cv2.minAreaRect(cnt)
                    #box = cv2.boxPoints(self.rect_theta)
                    #box = np.int0(box)
                    #print("box",box)
                    self.area = cv2.contourArea(cnt)
                    if self.area > 45000:
                        self.area = 200
                    if (self.area) > 25000 and self.area < 40000:
                        self.area = 110
                    elif (self.area) < 25000:
                        self.area = 75

                #get centroid
                M=cv2.moments(cnt)
                cx=int(M['m10']/M['m00'])
                cy=int(M['m01']/M['m00'])
                
                # cộng thêm cx sau khi ROI
                cx = cx + 1000
                
                self.printStatus("point number "+str(i))
                self.printStatus("cx: "+ str(cx)+",cy: "+str(cy))
                self.printStatus("x: "+str(x)+" y: "+str(y)+" w: "+str(w)+" h: "+str(h))
                
                # Tính toán vị trí thực tham chiếu từ hàm XYZ_realworld
                self.XYZ_real = self.XYZ.calculate_XYZ(cx,cy)
   
                #draw retangle
                cv2.rectangle(img_output,(x,y),(x+w,y+h),(0,255,0),2)
                #draw center
                cv2.circle(img_output,(cx-1000,cy),3,(0,255,0),2)
                
                #------------ predicted--------------
                
                #cv2.circle(img_output,(predicted[0]-1000+50,predicted [1]+50),3,(0,0,255),2)
                #print(predicted)
                #------------------------------------
                if self.PRINT_IMG_LABELS ==True:
                    # Các thông số cố định
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    font_thickness = 2
                    color = (255, 0, 0) # Màu chữ
                    bg_color = (0, 200, 0) # Màu nền mỏng (xanh lá cây)
                    alpha = 0.6  # Độ trong suốt

                    # Tọa độ gốc của văn bản
                    origin_x = cx - 990
                    origin_y = cy

                    # Số lượng dòng văn bản
                    num_lines = 6
                    line_height = 15

                    # Kích thước hình chữ nhật background
                    rect_width = 160 # Chiều rộng đủ để chứa text
                    rect_height = num_lines * line_height - 25  # Chiều cao đủ cho các dòng text và padding

                    # Tạo một lớp nền mỏng
                    overlay = img_output.copy()
                    cv2.rectangle(overlay, (origin_x, origin_y - 10), (origin_x + rect_width, origin_y + rect_height), bg_color, thickness=cv2.FILLED)

                    # Áp dụng lớp nền mỏng lên ảnh gốc
                    cv2.addWeighted(overlay, alpha, img_output, 1 - alpha, 0, img_output)

                    #image,text,font,bottomleftconrner,fontscale,fontcolor,linetype
                    cv2.putText(img_output,"Point "+str(i),(cx-990,cy),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
                    cv2.putText(img_output,"cx,cy: "+str(self.truncate(cx,2))+","+str(self.truncate(cy,2)),(cx-990,cy+15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
                    cv2.putText(img_output,"Area: "+str(self.truncate(self.area,2)),(cx-990,cy+30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
                    cv2.putText(img_output,"(x,y): "+str(self.truncate(self.XYZ_real[0],2))+","+str(self.truncate(self.XYZ_real[1],2)),(cx-990,cy+45),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
                    cv2.putText(img_output,"Angle: "+str(self.truncate(self.rect_theta[2],2)),(cx-990,cy+60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
                    
                points=[x,y,w,h,cx,cy]
                detected_points.append(points)

        if (obj_count>1 or len(validcontours)==0):               
            self.previewImage("Multiple Objects Detected",img_output)
            cv2.imshow("detect",img_output)
            #ban_img_output = cv2.resize(img_output,(0,0),fx=0.5,fy=0.5 )
            #cv2.imshow("detect",ban_img_output)
            #print(ban_img_output.shape)
            one_object=False
        else:
            self.previewImage("One Objects Detected",img_output)
            cv2.imshow("detect",img_output)
            #ban_img_output = cv2.resize(img_output,(0,0),fx=0.5,fy=0.5 )
            #cv2.imshow("detect",ban_img_output)
            one_object=True

        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        return obj_count, detected_points, img_output
    

    #tạo hàm lấy giá trị XYZ_real
    def get_XYZ_real(self):
        
        return self.XYZ_real, self.rect_theta, self.area 
      
    def truncate(self, n, decimals=0):
        n=float(n)
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier

    def writeImage(self,filename,image,testdir=False):
        if self.WRITE_IMAGES==True:
            if testdir==False:
                cv2.imwrite(self.TESTDIR+filename,image)
            else:
                cv2.imwrite(self.IMGDIR+filename,image)

    def readImage(self,imgfile):

        img=cv2.imread(imgfile)

        return img
        
    def printStatus(self,text):

        if self.PRINT_STATUS==True:
            print(text)
            
    
    def previewImage(self, text, img):
        if self.PREVIEW_IMAGES==True:
            #show full screen
            cv2.namedWindow(text, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(text,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

            cv2.imshow(text,img)
            if self.PREVIEW_AUTOCLOSE==True:
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
    
            else:
                cv2.waitKey(0)
                cv2.destroyAllWindows()

    def calculateDifference_Otsu(self,img,background_img):
        
        # Object Recognition Tresholds
        diff_low_t=45
        diff_high_t=255


        self.previewImage("Original Image [Diff Otsu]",img)

        # Background - Gray
        background_img_gray=cv2.cvtColor(background_img, cv2.COLOR_BGR2GRAY)
        self.previewImage("1 Background Gray",background_img_gray)

        # Image - Gray
        img_gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.previewImage("2 Image Gray",img_gray)
        
        #cv2.imshow("gray",img_gray)
        ban_gray = cv2.resize(img_gray,(0,0),fx=0.5,fy=0.5 )
        cv2.imshow("gray",ban_gray)
        # Calculate Difference
        diff_gray=cv2.absdiff(background_img_gray,img_gray)
        self.previewImage("3 Pre-Diff",diff_gray)

        #cv2.imshow("gray",diff_gray)
        ban__diff_gray = cv2.resize(diff_gray,(0,0),fx=0.5,fy=0.5 )
        cv2.imshow("gray",ban__diff_gray)
        
        # Diff Blur
        diff_gray_blur = cv2.GaussianBlur(diff_gray,(5,5),0)
        self.previewImage("4 Pre-Diff Blur",diff_gray_blur)

            #========= Otsu automatically finds the right threhosld, calibration not needed.

        # find otsu's threshold value with OpenCV function
        ret, otsu_tresh = cv2.threshold(diff_gray_blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        self.previewImage("5 Otsu Treshold",otsu_tresh)

        self.printStatus("Otsu defined treshold value is %d" % ret)

        if (ret < self.OtsuSensitivity):
            #discard image
            #make the difference zero by subtracting backdroungs
            diff=cv2.absdiff(background_img_gray,background_img_gray)
        else:       
            #Treshold Blur
            diff = cv2.GaussianBlur(otsu_tresh,(5,5),0)
            self.previewImage("6 Image Treshold",diff)
        return diff


    def identify_validcontours(self,cnt,height,width):

        #helps discard noise on contour detection.
        #this is calibrated for Legos in this example

        contours_validindex=[]
        contour_index=-1

        for i in cnt:

            contour_index=contour_index+1
            ca=cv2.contourArea(i)

            # Calculate W/H Ratio
            x,y,w,h = cv2.boundingRect(i)

            aspect_ratio = float(w)/h

            # Flag as edge_noise if the object is at a Corner

            #height, width, channels = img.shape
            edge_noise=False
            if x==0:
                edge_noise=True
            if y==0:
                edge_noise=True
            if (x+w)==width:
                edge_noise=True
            if (y+h)==height:
                edge_noise=True
                       
            # DISCARD noise with measure if area not within parameters
            if ca>self.MIN_AREA and ca<self.MAX_AREA:

                # DISCARD as noise on ratio
                if aspect_ratio>=self.MIN_ASPECTRATIO and aspect_ratio<=self.MAX_ASPECTRATIO:
  
                    # DISCARD if at the Edge
                    if edge_noise==False:
                        contours_validindex.append(contour_index)
                       
        return contours_validindex

    def square_rotatedCrop(self,cnt,crop_img,contour_img,height,width):

        #You need squares to use InceptionV3 :)

        #This rectangle will reflect the rotation of the image.
        rect = cv2.minAreaRect(cnt)
        
        img=crop_img.copy()

        r_cx=rect[0][0] #center x
        r_cy=rect[0][1] #centery y
        r_width=rect[1][0]
        r_height=rect[1][1]
    
        #EXPAND THE RECTANGLE ==> CHECK TO SEE IF NOT OUT OF BOUNDS
        adjust=0.15+0.05
        while True:
            #assume True in each iteration
            fits_inbounds=True
            #reduce adjustment each iteration
            adjust=adjust-0.05
            if adjust==0: break

            newW=int(r_width*(1+adjust))
            newH=int(r_height*(1+adjust))
            new_rect=(rect[0],[newW,newH],rect[2])
            nbox=cv2.boxPoints(new_rect)

            for i in range(nbox.shape[0]):
                #x or y smaller than zero
                for j in range (nbox[i].shape[0]):
                    if nbox[i][j]<0:
                        fits_inbounds=False
                #x greater than picture with
                if nbox[i][0]>width:
                    fits_inbounds=False
                #y greater than picture with
                    
                if nbox[i][1]>height:
                    fits_inbounds=False
                    
            if fits_inbounds==True:
                rect=new_rect
                break
            else:
                newW=int(r_width)
                newH=int(r_height)

        #Enable same Orientation when pieces are asymetrical (e.g. long side if image is horizontal)
        if r_height>r_width:
            #flip w, h
            rect=(rect[0],[r_height,r_width],rect[2]+90)

        #Make it a square
        if newW>newH:
            rect=(rect[0],[newW,newW],rect[2])
        if newH>newW:
            rect=(rect[0],[newH,newH],rect[2])

        #Draw the Box       
        boxdraw = cv2.boxPoints(rect)
        boxdraw = np.int0(boxdraw)
        cv2.drawContours(contour_img,[boxdraw],0,(0,0,255),3)

        # rotate img
        angle = rect[2]
        rows, cols = img.shape[0], img.shape[1]
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
        img_rot = cv2.warpAffine(img, M, (cols, rows))

        # rotate bounding box
        box = cv2.boxPoints(rect)      
        pts = np.int0(cv2.transform(np.array([box]), M))[0]
        pts[pts < 0] = 0

        #re-establish width and height on rotated image
        width, height, channel=img_rot.shape

        x=pts[1][1]
        xw=pts[0][1]
        w=xw-x
        y=pts[1][0]
        yh=pts[2][0]
        h=yh-y

        # CHECK TO SEE IF EXPANDED CONTOUR IS IN BOUNDS
        if y<0: y=0
        if x<0: x=0
        if (xw)>width: w=width-x
        if (yh)>height: h=height-y        

        # SQUARE THE CONTOUR
        if w>h:
            #make a square
            h=w
            if (y+h)>height: y=height-h
        if h>w:
            w=h
            if (x+w)>width: x=width-w

        # Crop the Image
        crop_img = img_rot[x:x+w,
                           y:y+h]
        
        return crop_img,contour_img,r_width,r_height



