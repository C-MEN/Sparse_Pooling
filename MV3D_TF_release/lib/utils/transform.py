import numpy as np

TOP_X_MAX = 60
TOP_X_MIN = 0
TOP_Y_MIN = -30
TOP_Y_MAX = 30
RES = 0.1
LIDAR_HEIGHT = 1.73
CAR_HEIGHT = 1.56
X0, Xn = 0, int((TOP_X_MAX - TOP_X_MIN) // RES) + 1
Y0, Yn = 0, int((TOP_Y_MAX - TOP_Y_MIN) // RES) + 1

def calib_to_P(calib,from_camera=False):
    #WZN: get the actual overall calibration matrix from Lidar coord to image
    #calib is 4*12 read by imdb
    #P is 3*4 s.t. uvw=P*XYZ1
    if from_camera:
        return np.reshape(calib[0,:],(3,4))
    else:
        C2V = np.vstack((np.reshape(calib[3,:],(3,4)),np.array([0,0,0,1])))
        R0 = np.hstack((np.reshape(calib[2,:],(4,3)),np.array([[0],[0],[0],[1]])))
        P2 = np.reshape(calib[0,:],(3,4))
        P = np.matmul(np.matmul(P2,R0),C2V)
        return P

def calib_to_L2C(calib):
    #WZN: return the calibration matrix from LIDAR coord to camera frame
    C2V = np.vstack((np.reshape(calib[3,:],(3,4)),np.array([0,0,0,1])))
    R0 = np.hstack((np.reshape(calib[2,:],(4,3)),np.array([[0],[0],[0],[1]])))
    return np.matmul(R0,C2V)

def _lidar_shift_to_bv_shift(x,y):
    xx = -y // RES
    yy = -x // RES

    return xx, yy

def _lidar_to_bv_coord(x, y):
    X0, Xn = 0, int((TOP_X_MAX - TOP_X_MIN) // RES) + 1
    Y0, Yn = 0, int((TOP_Y_MAX - TOP_Y_MIN) // RES) + 1

    xx = Yn - (y - TOP_Y_MIN) // RES
    yy = Xn - (x - TOP_X_MIN) // RES

    return xx, yy

def _lidar_to_bv_coord_float(x, y):
    X0, Xn = 0, int((TOP_X_MAX - TOP_X_MIN) // RES) + 1
    Y0, Yn = 0, int((TOP_Y_MAX - TOP_Y_MIN) // RES) + 1

    xx = float(Yn) - (y - TOP_Y_MIN) / RES
    yy = float(Xn) - (x - TOP_X_MIN) / RES

    return xx, yy

def _bv_to_lidar_coords(xx,yy):
    X0, Xn = 0, int((TOP_X_MAX-TOP_X_MIN)//RES)+1
    Y0, Yn = 0, int((TOP_Y_MAX-TOP_Y_MIN)//RES)+1
    y = Xn*RES-(xx+0.5)*RES + TOP_Y_MIN
    x = Yn*RES-(yy+0.5)*RES + TOP_X_MIN

    return x,y


def lidar_cnr_to_bv_cnr(corners):
    #WZN: transform 3D corners to bv corners, [x0,x1,x2,...,y0,y1,...,y7,z0,...,z7] to [x0,x1,x2,x3,y1,y2,y3,y4]
    if np.size(corners)==0:
        return np.zeros((0,8))
    elif np.size(corners)==24:
        bv_corners = np.zeros((1,8))
        xys = corners.reshape((3,8))[:2,:4]
        bv_corners[0,0:4],bv_corners[0,4:8] = _lidar_to_bv_coord_float(xys[0,:],xys[1,:])
        return bv_corners
    else:
        assert corners.shape[1]==24, 'wrong input size'
        bv_corners = np.zeros((corners.shape[0],8))
        xys = corners[:,[0,1,2,3,8,9,10,11]]
        bv_corners[:,0:4],bv_corners[:,4:8] = _lidar_to_bv_coord_float(xys[:,0:4],xys[:,4:8])
        return bv_corners


'''
def lidar_cnr_to_bv_single(corners):
    pts_2D = np.zeros(4)
    # min & max in lidar coords
    xmin = np.min(corners[:8])
    xmax = np.max(corners[:8])
    ymin = np.min(corners[8:16])
    ymax = np.max(corners[8:16])

    # top left bottom right at lidar bird view coords
    pts_2D = np.array([xmax, ymax, xmin, ymin])

    pts_2D[0], pts_2D[1] = _lidar_to_bv_coord(pts_2D[0], pts_2D[1])
    pts_2D[2], pts_2D[3] = _lidar_to_bv_coord(pts_2D[2], pts_2D[3])

    return pts_2D
'''
#  def lidar_cnr_to_bv_single(corners):
    #  """
    #  convert lidar corners (x0-x7,y0-y7,z0-z7) to lidar bv view (x1 ,y1, x2, y2)
    #  """
    #  if corners.shape == (3, 8):
        #  corners = corners.reshape(24)

    #  assert corners.shape[0] == 24
    #  pts_2D = np.zeros(4)
    #  xmin = np.min(corners[:8])
    #  xmax = np.max(corners[:8])
    #  ymin = np.min(corners[8:16])
    #  ymax = np.max(corners[8:16])

    #  pts_2D = np.array([xmin, ymin, xmax, ymax])

    #  pts_2D[0], pts_2D[1] = _lidar_to_bv_coord(pts_2D[0], pts_2D[1])
    #  pts_2D[2], pts_2D[3] = _lidar_to_bv_coord(pts_2D[2], pts_2D[3])

    #  return pts_2D

def lidar_to_bv_single(rois_3d):
    """
    cast lidar 3d points(x, y, z, l, w, h) to bird view (x1, y1, x2, y2)
    """
    assert(rois_3d.shape[0] == 6)
    rois = np.zeros((4))

    rois[0] = rois_3d[0] + rois_3d[3] * 0.5
    rois[1] = rois_3d[1] + rois_3d[4] * 0.5
    rois[2] = rois_3d[0] - rois_3d[3] * 0.5
    rois[3] = rois_3d[1] - rois_3d[4] * 0.5

    rois[0], rois[1] = _lidar_to_bv_coord(rois[0], rois[1])
    rois[2], rois[3] = _lidar_to_bv_coord(rois[2], rois[3])
    # print rois
    # assert rois[0] < 1000
    # assert rois[2] < 1000
    # assert rois[1] < 1000
    # assert rois[3] < 1000
    return rois

def from_2d_cnr_to_3d_cnr(corners_2d):
    corners_3d = np.zeros((corners_2d.shape[0],24))
    corners_3d[:,0:4] = corners_2d[:,0:4]
    corners_3d[:,4:8] = corners_2d[:,0:4]
    corners_3d[:,8:12] = corners_2d[:,4:8]
    corners_3d[:,12:16] = corners_2d[:,4:8]
    corners_3d[:,16:20] = -(LIDAR_HEIGHT)
    corners_3d[:,20:24] = -(LIDAR_HEIGHT-CAR_HEIGHT)

    return corners_3d


def bv_center_to_lidar(centers):
    ex_ctr_x = centers[:,0]
    ex_ctr_y = centers[:,1]
    ex_ctr_x, ex_ctr_y = _bv_to_lidar_coords(ex_ctr_x, ex_ctr_y)
    ex_ctr_z = np.ones((centers.shape[0]), dtype=np.float32) * -(LIDAR_HEIGHT-CAR_HEIGHT/2.) #
    centers_3d = np.vstack((ex_ctr_x,ex_ctr_y,ex_ctr_z)).T

    return centers_3d

def bv_anchor_to_lidar(anchors):
    """
    convert 2d anchors to 3d anchors
    """
    ex_lengths = anchors[:, 3] - anchors[:, 1]
    ex_widths = anchors[:, 2] - anchors[:, 0]

    ex_ctr_x = (anchors[:,0] + anchors[:,2]) / 2.
    ex_ctr_y = (anchors[:,1] + anchors[:,3]) / 2.

    ex_lengths = ex_lengths.reshape((anchors.shape[0], 1)) * RES
    ex_widths = ex_widths.reshape((anchors.shape[0], 1)) * RES
    ex_ctr_x = ex_ctr_x.reshape((anchors.shape[0], 1))
    ex_ctr_y = ex_ctr_y.reshape((anchors.shape[0], 1))

    ex_ctr_x, ex_ctr_y = _bv_to_lidar_coords(ex_ctr_x, ex_ctr_y)

    ex_heights = np.ones((anchors.shape[0], 1), dtype=np.float32) * CAR_HEIGHT
    ex_ctr_z = np.ones((anchors.shape[0], 1), dtype=np.float32) * -(LIDAR_HEIGHT-CAR_HEIGHT/2.) #

    anchors_3d = np.hstack((ex_ctr_x, ex_ctr_y, ex_ctr_z, ex_lengths, ex_widths, ex_heights))

    return anchors_3d

def reassign_z(zc):
    #reassign zc which is Nx1
    # this is for camera frame
    zc = (LIDAR_HEIGHT-CAR_HEIGHT/2)
    return zc


def lidar_3d_to_bv(rois_3d):
    """
    cast lidar 3d points(x, y, z, l, w, h) to bird view (x1, y1, x2, y2)
    """

    if len(rois_3d.shape) == 1:
    # if 0:
        rois = np.zeros(4)

        rois[0] = rois_3d[0] + rois_3d[3] * 0.5
        rois[1] = rois_3d[1] + rois_3d[4] * 0.5
        rois[2] = rois_3d[0] - rois_3d[3] * 0.5
        rois[3] = rois_3d[1] - rois_3d[4] * 0.5

        rois[0], rois[1] = _lidar_to_bv_coord_float(rois[0], rois[1])
        rois[2], rois[3] = _lidar_to_bv_coord_float(rois[2], rois[3])

    else:

        rois = np.zeros((rois_3d.shape[0], 4))

        rois[:, 0] = rois_3d[:, 0] + rois_3d[:, 3] * 0.5
        rois[:, 1] = rois_3d[:, 1] + rois_3d[:, 4] * 0.5
        rois[:, 2] = rois_3d[:, 0] - rois_3d[:, 3] * 0.5
        rois[:, 3] = rois_3d[:, 1] - rois_3d[:, 4] * 0.5

        rois[:, 0], rois[:, 1] = _lidar_to_bv_coord_float(rois[:, 0], rois[:, 1])
        rois[:, 2], rois[:, 3] = _lidar_to_bv_coord_float(rois[:, 2], rois[:, 3])

    return rois.astype(np.float32)


def lidar_to_bv(rois_3d):
    """
    cast lidar 3d points(0,x, y, z, l, w, h) to bird view (0,x1, y1, x2, y2)
    """

    rois = np.zeros((rois_3d.shape[0], 5))
    rois[:, 0] = rois_3d[:, 0]

    rois[:, 1] = rois_3d[:, 1] + rois_3d[:, 4] * 0.5
    rois[:, 2] = rois_3d[:, 2] + rois_3d[:, 5] * 0.5
    rois[:, 3] = rois_3d[:, 1] - rois_3d[:, 4] * 0.5
    rois[:, 4] = rois_3d[:, 2] - rois_3d[:, 5] * 0.5

    rois[:, 1], rois[:, 2] = _lidar_to_bv_coord_float(rois[:, 1], rois[:, 2])
    rois[:, 3], rois[:, 4] = _lidar_to_bv_coord_float(rois[:, 3], rois[:, 4])

    return rois.astype(np.float32)


def _bv_to_lidar_coord(x, y):
    Y0, Yn = 0, int((TOP_X_MAX - TOP_X_MIN) // RES) + 1
    X0, Xn = 0, int((TOP_Y_MAX - TOP_Y_MIN) // RES) + 1
    yy = (Yn - y) * RES + TOP_Y_MIN
    xx = (Xn - x) * RES + TOP_X_MIN
    return xx, yy

# WZN: compute the box that contains all corners
def lidar_cnr_to_3d(corners, lwh):
    """
    lidar_corners to Boxex3D

    """
    shape = corners.shape
    if shape[0] == 24:
        boxes_3d = np.zeros(6)
        corners = corners.reshape((3, 8))
        cnr_max = np.amax(corners,axis=1)
        cnr_min = np.amin(corners,axis=1)
        boxes_3d[:3] = (cnr_min+cnr_max)/2
        boxes_3d[3:] = (cnr_max-cnr_min)
    else:
        boxes_3d = np.zeros((shape[0],6))
        corners = corners.reshape((-1, 3, 8))
        cnr_max = np.amax(corners,axis=2)
        cnr_min = np.amin(corners,axis=2)
        boxes_3d[:,:3] = (cnr_min+cnr_max)/2
        boxes_3d[:,3:] = (cnr_max-cnr_min)
    return boxes_3d

''' WZN: origin
def lidar_cnr_to_3d(corners, lwh):
    """
    lidar_corners to Boxex3D
    """
    shape = corners.shape
    if shape[0] == 24:
        boxes_3d = np.zeros(6)
        corners = corners.reshape((3, 8))
        boxes_3d[:3] = corners.mean(1)
        boxes_3d[3:] = lwh
    else:
        boxes_3d = np.zeros((shape[0],6))
        corners = corners.reshape((-1, 3, 8))
        boxes_3d[:,:3] = corners.mean(2)
        boxes_3d[:,3:] = lwh
    return boxes_3d
'''

def cam_to_lidar_3d(pts_3D, Tr):
    """
    convert camera(x, y, z, l, w, h) to lidar (x, y, z, l, w, h)
    """

    points = pts_3D[:,:3].transpose()
    points = np.vstack((points, np.ones(pts_3D.shape[0])))

    R = np.linalg.inv(Tr[:, :3])
    T = np.zeros((3, 1))
    T[0] = -Tr[1,3]
    T[1] = -Tr[2,3]
    T[2] = Tr[0,3]
    RT = np.hstack((R, T))
    points_lidar = np.dot(RT, points)

    pts_3D_lidar = np.zeros((pts_3D.shape))
    pts_3D_lidar[:,:3] = points_lidar.transpose()
    pts_3D_lidar[:,3:6] = pts_3D[:,3:6]

    return pts_3D_lidar

def cam_to_lidar_3d_single(pts_3D,Tr):
    """
    convert camera(x, y, z, l, w, h) to lidar (x, y, z, l, w, h)
    """

    points = pts_3D[:3]
    points = np.vstack((points, 1)).reshape((4, 1))

    R = np.linalg.inv(Tr[:, :3])
    T = np.zeros((3, 1))
    T[0] = -Tr[1,3]
    T[1] = -Tr[2,3]
    T[2] = Tr[0,3]
    RT = np.hstack((R, T))

    points_lidar = np.dot(RT, points)

    pts_3D_lidar = np.zeros(6)
    pts_3D_lidar[:3] = points_lidar.flatten()
    pts_3D_lidar[3:6] = pts_3D[3:6]

    return pts_3D_lidar

def _bv_roi_to_3d(rpn_rois_bv):
    """ convert rpn rois (0, x1, y1, x2, y2) to lidar 3d anchor (0, x, y, z, l, w, h) """
     # convert bird view rpn_rois to lidar coordinates
    rpn_rois_bv[:,1], rpn_rois_bv[:,2] = _bv_to_lidar(rpn_rois_bv[:,1], rpn_rois_bv[:,2])
    rpn_rois_bv[:,3], rpn_rois_bv[:,4] = _bv_to_lidar(rpn_rois_bv[:,3], rpn_rois_bv[:,4])

    # convert rpn_rois(0, x1, y1, x2, y2) to rpn_rois_ctr (0, x, y, l, w)
    rpn_rois_ctr = np.zeros(shape=rpn_rois_bv.shape, dtype=rpn_rois_bv.dtype)

    rpn_rois_ctr[:,1] = (rpn_rois_bv[:,1] + rpn_rois_bv[:,3]) * 0.5 # x
    rpn_rois_ctr[:,2] = (rpn_rois_bv[:,2] + rpn_rois_bv[:,4]) * 0.5 # y
    rpn_rois_ctr[:,3] = np.abs(rpn_rois_bv[:,3] - rpn_rois_bv[:,1]) # l
    rpn_rois_ctr[:,4] = np.abs(rpn_rois_bv[:,2] - rpn_rois_bv[:,4]) # w

    # extend rpn_rois_ctr (0, x, y) to 3d rois (0, x, y, z, l, w, h)
    rshape = rpn_rois_ctr.shape
    ctr_height = np.ones((rshape[0]))*(- (LIDAR_HEIGHT - CAR_HEIGHT * 0.5))
    car_height = np.ones((rshape[0]))*CAR_HEIGHT
    ctr_height = ctr_height.reshape(-1, 1)
    car_height = car_height.reshape(-1, 1)

    if DEBUG:
        print (rpn_rois_ctr.shape)
        print ('car height shape', car_height.shape)
        print ('ctr shape', ctr_height.shape)

    all_rois_3d = np.hstack((rpn_rois_ctr[:,:3],
                ctr_height, rpn_rois_ctr[:,3:5], car_height))
    assert(all_rois_3d.shape[1] == 7)
    return all_rois_3d


def lidar_to_corners_single(pts_3D,ry=0):
    """
    convert pts_3D_lidar (x, y, z, l, w, h) to
    8 corners (x0, ... x7, y0, ...y7, z0, ... z7)

    (x0, y0, z0) at left,forward, up.
    clock-wise
    WZN: no rotation involved
    """
    R = np.array([[np.cos(ry), np.sin(ry), 0],
                [-np.sin(ry), np.cos(ry), 0],
                [0, 0, 1]]).reshape((3,3))

    l = pts_3D[3]
    w = pts_3D[4]
    h = pts_3D[5]

    x_corners = np.array([l/2., l/2., -l/2., -l/2., l/2., l/2., -l/2., -l/2.])
    y_corners = np.array([w/2., -w/2., -w/2., w/2., w/2., -w/2., -w/2., w/2.])
    z_corners = np.array([-h/2., -h/2., -h/2., -h/2., h/2., h/2., h/2., h/2.])

    corners = np.vstack((x_corners, y_corners, z_corners))

    corners[0,:] = corners[0,:] + pts_3D[0]
    corners[1,:] = corners[1,:] + pts_3D[1]
    corners[2,:] = corners[2,:] + pts_3D[2]

    corners = np.dot(R,corners)

    return corners.reshape(-1).astype(np.float32)

def lidar_3d_to_corners(pts_3D):
    """
    convert pts_3D_lidar (x, y, z, l, w, h) to
    8 corners (x0, ... x7, y0, ...y7, z0, ... z7)
    WZN: no rotation involved
    """

    l = pts_3D[:, 3]
    w = pts_3D[:, 4]
    h = pts_3D[:, 5]

    l = l.reshape(-1, 1)
    w = w.reshape(-1, 1)
    h = h.reshape(-1, 1)

    # clockwise, zero at bottom left
    x_corners = np.hstack((l/2., l/2., -l/2., -l/2., l/2., l/2., -l/2., -l/2.))
    y_corners = np.hstack((w/2., -w/2., -w/2., w/2., w/2., -w/2., -w/2., w/2.))
    z_corners = np.hstack((-h/2.,-h/2.,-h/2.,-h/2.,h/2.,h/2.,h/2.,h/2.))

    corners = np.hstack((x_corners, y_corners, z_corners))

    corners[:,0:8] = corners[:,0:8] + pts_3D[:,0].reshape((-1, 1)).repeat(8, axis=1)
    corners[:,8:16] = corners[:,8:16] + pts_3D[:,1].reshape((-1, 1)).repeat(8, axis=1)
    corners[:,16:24] = corners[:,16:24] + pts_3D[:,2].reshape((-1, 1)).repeat(8, axis=1)

    return corners

def projectToImage(pts_3D, P):
    """
    PROJECTTOIMAGE projects 3D points in given coordinate system in the image
    plane using the given projection matrix P.

    Usage: pts_2D = projectToImage(pts_3D, P)
    input: pts_3D: 3xn matrix
          P:      3x4 projection matrix
    output: pts_2D: 2xn matrix

    last edited on: 2012-02-27
    Philip Lenz - lenz@kit.edu
    """
    # project in image
    mat = np.vstack((pts_3D, np.ones((pts_3D.shape[1]))))

    pts_2D = np.dot(P, mat)

    # scale projected points
    pts_2D[0, :] = pts_2D[0, :] / pts_2D[2, :]
    pts_2D[1, :] = pts_2D[1, :] / pts_2D[2, :]
    pts_2D = np.delete(pts_2D, 2, 0)

    return pts_2D

def clip3DwithinImage(pts_3D,P,image_size):
    """
    WZN: first project 3D points to image than return index 
    that keep only the points visible to the image
    input see projectToImage(), image_size should be [side,height]
    return the indices of pts_3D
    """
    pts_2D = projectToImage(pts_3D,P)
    indices = np.logical_and(pts_2D[0,:]<image_size[0]-1,pts_2D[0,:]>=0)
    indices = np.logical_and(indices,pts_2D[1,:]>=0)
    indices = np.logical_and(indices,pts_2D[1,:]<image_size[1]-1)
    #print np.amax(pts_2D[:,indices],axis=1), 'image size: ', image_size
    return indices

def lidar_to_camera(pts_3D,calib):
    '''
    WZN: transform the points in LIDAR frame to camera frame
    '''
    L2C = calib_to_L2C(calib)
    mat = np.vstack((pts_3D, np.ones((pts_3D.shape[1]))))
    pts_3D_cam = np.dot(L2C,mat) 
    return pts_3D_cam[0:3,:].transpose()

def _corners_to_bv(corners):
    pts_2D = np.zeros((corners.shape[0], 4))

    # min & max in lidar coords
    xmin = np.min(corners[:, :8], axis=1).reshape(-1, 1)
    xmax = np.max(corners[:, :8], axis=1).reshape(-1, 1)
    ymin = np.min(corners[:, 8:16], axis=1).reshape(-1, 1)
    ymax = np.max(corners[:, 8:16], axis=1).reshape(-1, 1)

    # top left bottom right at lidar bird view coords
    pts_2D = np.hstack([xmax, ymax, xmin, ymin])

    pts_2D[:,0], pts_2D[:,1] = _lidar_to_bv_coord(pts_2D[:,0], pts_2D[:,1])
    pts_2D[:,2], pts_2D[:,3] = _lidar_to_bv_coord(pts_2D[:,2], pts_2D[:,3])

    return pts_2D

def corners_to_bv(corners):
    """
    WZN: 8 corners (x0, ... x7, y0, ...y7, z0, ... z7) *num_class
    """
    num_class = corners.shape[1] / 24
    bv = np.zeros((corners.shape[0], 4*num_class))
    for i in xrange(num_class):
        cnr = corners[:, i*24:(i+1)*24]
        bv[:, i*4:(i+1)*4] = _corners_to_bv(cnr)

    return bv


def lidar_cnr_to_img_single(corners, Tr, R0, P2):

    Tr = Tr.reshape((3, 4))
    R0 = R0.reshape((4, 3))
    P2 = P2.reshape((3, 4))
    assert Tr.shape == (3, 4)
    assert R0.shape == (4, 3)
    assert P2.shape == (3, 4)

    if 24 in corners.shape:
        corners = corners.reshape((3, 8))

    corners = np.vstack((corners, np.ones(8)))

    mat1 =  np.dot(P2, R0)
    mat2 = np.dot(mat1, Tr)
    img_cor = np.dot(mat2, corners)
    return img_cor

def lidar_cnr_to_img(corners, Tr, R0, P2):

    img_boxes = np.zeros((corners.shape[0], 4))

    R0 = R0.reshape((4, 3))
    Tr = Tr.reshape((3, 4))
    P2 = P2.reshape((3, 4))

    new_corners = corners.reshape((-1, 3, 8))

    mat = reduce(np.dot, [P2, R0, Tr])

    #  img_cor = np.array(map(lambda x:np.dot(mat, np.vstack((x,np.zeros(8)))), new_corners))
    new_corners = np.append(new_corners, np.ones((new_corners.shape[0], 1, 8)), 1)
    img_cor = np.dot(mat, new_corners).transpose(1, 0, 2)

    xs = img_cor[:,0,:] / np.abs(img_cor[:,2,:])
    ys = img_cor[:,1,:] / np.abs(img_cor[:,2,:])

    xmin = np.min(xs, axis=1).reshape(-1, 1)
    xmax = np.max(xs, axis=1).reshape(-1, 1)
    ymin = np.min(ys, axis=1).reshape(-1, 1)
    ymax = np.max(ys, axis=1).reshape(-1, 1)

    img_boxes = np.hstack((xmin, ymin, xmax, ymax))

    return img_boxes#.astype(np.int32)

def lidar_cnr_to_camera_bv(corners, Tr):
    #WZN
    #input corners in 3d, output bv boxes [x,z,l,w] in camera frame (For evaluation use)
    #corner definition see computeCorners3D
    new_corners = corners.reshape((3, 8))
    new_corners = np.vstack((new_corners, np.ones((1, 8))))
    cam_cor = np.dot(Tr, new_corners)
    ry = np.arctan2(np.sum(cam_cor[2,0:2])-np.sum(cam_cor[2,2:4]),np.sum(cam_cor[0,0:2])-np.sum(cam_cor[0,2:4]))
    #ry = np.arctan2(cam_cor[0,0]-cam_cor[0,1],cam_cor[2,0]-cam_cor[2,1])
    xyz = np.mean(cam_cor,axis=1)
    w = np.sqrt(np.sum((cam_cor[[0,2],0]-cam_cor[[0,2],1])**2))
    l = np.sqrt(np.sum((cam_cor[[0,2],0]-cam_cor[[0,2],3])**2))
    #print (cam_cor[2,0]-cam_cor[2,1],cam_cor[0,0]-cam_cor[0,1]) #Note in kitti facing left is 0 ry
    #h = np.abs(cam_cor[1,0]-cam_cor[1,4])
    return np.array([xyz[0],xyz[2],l,w]),ry
#  def lidar_cnr_to_img(corners, Tr, R0, P2):

    #  img_boxes = np.zeros((corners.shape[0], 4))

    #  Tr = Tr.reshape((3, 4))
    #  R0 = R0.reshape((4, 3))
    #  P2 = P2.reshape((3, 4))

    #  for i in range(corners.shape[0]):

        #  img_cor = lidar_cnr_to_img_single(corners[i], Tr, R0, P2)

        #  img_cor = img_cor / np.abs(img_cor[2])

        #  #  xmin = np.max((0, np.min(img_cor[0])))
        #  xmin = np.min(img_cor[0])
        #  xmax = np.max(img_cor[0])
        #  #  ymin = np.max((0, np.min(img_cor[1])))
        #  ymin = np.min(img_cor[1])
        #  ymax = np.max(img_cor[1])

        #  img_boxes[i, :] = np.array([xmin, ymin, xmax, ymax])

    #  return img_boxes.astype(np.int32)

def computeCorners3D(Boxex3D, ry):

    # compute rotational matrix around yaw axis
    R = np.array([[np.cos(ry), 0, np.sin(ry)],
                    [0,    1,       0],
         [-np.sin(ry), 0, np.cos(ry)]]).reshape((3,3))

    # 3D bounding box dimensions
    l, w, h = Boxex3D[3:6]
    x, y, z = Boxex3D[0:3]

    # 3D bounding box corners
    x_corners = np.array([l/2, l/2, -l/2, -l/2, l/2, l/2, -l/2, -l/2])
    y_corners = np.array([0,0,0,0,-h,-h,-h,-h])
    z_corners = np.array([w/2, -w/2, -w/2, w/2, w/2, -w/2, -w/2, w/2])

    corners = np.vstack((x_corners, y_corners, z_corners))

    # rotate and translate 3D bounding box
    corners_3D = np.dot(R, corners)
    corners_3D[0,:] = corners_3D[0,:] + x
    corners_3D[1,:] = corners_3D[1,:] + y
    corners_3D[2,:] = corners_3D[2,:] + z

    return corners_3D


def corners_to_bv_single(corners):
    pts_2D = np.zeros(4)
    # min & max in lidar coords
    xmin = np.min(corners[:8])
    xmax = np.max(corners[:8])
    ymin = np.min(corners[8:16])
    ymax = np.max(corners[8:16])

    # top left bottom right at lidar bird view coords
    pts_2D = np.array([xmax, ymax, xmin, ymin])

    pts_2D[0], pts_2D[1] = _lidar_to_bv_coord(pts_2D[0], pts_2D[1])
    pts_2D[2], pts_2D[3] = _lidar_to_bv_coord(pts_2D[2], pts_2D[3])

    return pts_2D

def lidar_cnr_to_img(corners, Tr, R0, P2):

    img_boxes = np.zeros((corners.shape[0], 4))

    for i in range(corners.shape[0]):

        img_cor = lidar_cnr_to_img_single(corners[i], Tr, R0, P2)

        img_cor = img_cor / img_cor[2]

        xmin = np.min(img_cor[0])
        xmax = np.max(img_cor[0])
        ymin = np.min(img_cor[1])
        ymax = np.max(img_cor[1])

        img_boxes[i, :] = np.array([xmin, ymin, xmax, ymax])

    return img_boxes.astype(np.int32)

def camera_to_lidar_cnr(pts_3D, P):
    """
    convert camera corners to lidar corners
    WZN: the original implementation seems to be totally wrong!!
    """
    
    if pts_3D.shape[1] == 24:
        pts_3D = pts_3D.reshape((3, 8))
    pts_3D = np.vstack((pts_3D, np.ones(8)))
    #if assume P is rigid transform, it can be much faster, without inverse
    if P.shape[0] == 3:
        P = np.vstack((P,np.array([0,0,0,1])))
    lidar_corners = np.linalg.solve(P,pts_3D)[:3,:]
    
    #pts_3D = np.vstack((pts_3D, np.zeros(8)))

    #assert pts_3D.shape == (4, 8)

    #R = np.linalg.inv(P[:, :3])
    ## T = -P[:, 3].reshape((3, 1))
    #T = np.zeros((3, 1))
    #T[0] = -P[1,3]
    #T[1] = -P[2,3]
    #T[2] = P[0,3]
    #RT = np.hstack((R, T))

    #lidar_corners = np.dot(RT, pts_3D)
    #lidar_corners = lidar_corners[:3,:]
    return lidar_corners.reshape(-1, 24)
    


def corners_to_img(corners, Tr, R0, P2):
    
    Tr = Tr.reshape((3, 4))
    R0 = R0.reshape((4, 3))
    P2 = P2.reshape((3, 4))
    
    if 24 in corners.shape:
        corners = corners.reshape((3, 8))

    # R0 = np.vstack((R0, np.zeros(3)))
    # print corners.shape
    corners = np.vstack((corners, np.ones(8)))

    # print(corners.shape)
    img_cor = reduce(np.dot, [P2, R0, Tr, corners])

    return img_cor

if __name__ == '__main__':
    P = np.array([6.927964000000e-03, -9.999722000000e-01, -2.757829000000e-03,
                  -2.457729000000e-02, -1.162982000000e-03, 2.749836000000e-03,
                  -9.999955000000e-01, -6.127237000000e-02, 9.999753000000e-01,
                  6.931141000000e-03, -1.143899000000e-03, -3.321029000000e-01]).astype(np.float32).reshape((3, 4))
    camera = [1.84, 1., 8.41, 5.78, 1.90, 2.72]
    # lidar = camera_to_lidar(camera, P)
    # print lidar
    # corners = lidar_to_corners_single(lidar)
    # corners = corners.reshape((3, 8))
    # # print(lidar)
    # print(corners)
