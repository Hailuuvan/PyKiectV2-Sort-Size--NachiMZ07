import numpy as np

# camera variables
cam_mtx = None
dist = None
newcam_mtx = None
roi = None
rvec1 = None
tvec1 = None
R_mtx = None
Rt = None
P_mtx = None


class XYZ_realworld:

    def __init__(self):
        # imgdir="/home/pi/Desktop/Captures/"
        savedir = "camera_data/"
        # self.imageRec=image_recognition_singlecam.image_recognition(False,False,imgdir,imgdir,False,True,False)

        self.cam_mtx = np.load(savedir + 'cam_mtx.npy')
        self.dist = np.load(savedir + 'dist.npy')
        self.newcam_mtx = np.load(savedir + 'newcam_mtx.npy')
        self.roi = np.load(savedir + 'roi.npy')
        self.rvec1 = np.load(savedir + 'rvec1.npy')
        self.tvec1 = np.load(savedir + 'tvec1.npy')
        self.R_mtx = np.load(savedir + 'R_mtx.npy')
        self.Rt = np.load(savedir + 'Rt.npy')
        self.P_mtx = np.load(savedir + 'P_mtx.npy')

        s_arr = np.load(savedir + 's_arr.npy')
        self.scalingfactor = s_arr[0]

        self.inverse_newcam_mtx = np.linalg.inv(self.newcam_mtx)
        self.inverse_R_mtx = np.linalg.inv(self.R_mtx)

    def calculate_XYZ(self, u, v):
        # Solve: From Image Pixels, find World Points

        uv_1 = np.array([[u, v, 1]], dtype=np.float32)
        uv_1 = uv_1.T
        suv_1 = self.scalingfactor * uv_1
        xyz_c = self.inverse_newcam_mtx.dot(suv_1)
        xyz_c = xyz_c - self.tvec1
        XYZ_checkboard = self.inverse_R_mtx.dot(xyz_c)
        #Ma trận xoay từ checkboard sang robot
        Rotate = np.array([[-1, 0, 0],[0, -1, 0],[0,0, 1]])
        #Ma trận Translation
        Trans = np.array([[59],[-24.441],[350]])
        XYZ_robot = np.dot(Rotate, XYZ_checkboard) + Trans

        return XYZ_robot


object1 = XYZ_realworld()

#print("[x;y;z]")
#X = object1.calculate_XYZ(1171,227)
#Y = object1.calculate_XYZ(1163,748)
#print(X)
#print(Y)

