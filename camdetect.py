
import cv2
import time
import json
from detectstatus import detectstatus, detectsingle, detecthandle

# def load_cam_config():
#     width = 0
#     height = 0
#     expo = 0.0
#     auto = 1
#     with open("./config/cam.json") as load_f:
#         load_dict = json.load(load_f)
#         width = load_dict["width"]
#         height = load_dict["height"]
#         expo = load_dict["exposure"]
#         auto = load_dict["auto"]
#     return width, height, expo, auto

def set_camera(num):
    cam = cv2.VideoCapture(num)
    # read camera default internal config
    width = cam.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    height = cam.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    expo = cam.get(cv2.cv.CV_CAP_PROP_EXPOSURE)
    print ("camera width is %d, height is %d, exposure is %f" % (width,height,expo))
    # read camera config file
    width,height,expo,auto = load_cam_config()

    cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,height)
    if auto == 0:
        #cam.set(cv2.cv.CV_CAP_PROP_AUTO_EXPOSURE,0.25)  # set as manual exposure(0.75 auto, 0.25 manual)
        cam.set(cv2.cv.CV_CAP_PROP_EXPOSURE,expo)   # 0.1, 0.05, 0.02
    else:
        cam.set(cv2.cv.CV_CAP_PROP_EXPOSURE,0.0)  # manual exposure
    #cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

    width = cam.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    height = cam.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    expo = cam.get(cv2.cv.CV_CAP_PROP_EXPOSURE)
    print ("test camera width is %d, height is %d, exposure is %f" % (width,height,expo))
    
    return cam

def region_detect(i,j,frame,target_matrix):
    m0 = target_matrix[j*2]
    m1 = target_matrix[j*2+1]
    m11 = m1[0]
    m12 = m1[1]
    #print j,counter,m0,m1,m11,m12
    y0 = m11[1]
    y1 = m12[1]
    x0 = m11[0]
    x1 = m12[0]
    #print y0,y1,x0,x1
    cropped = frame[y0:y1,x0:x1]   #[y0:y1, x0:x1]
    r_data = 0;
    ###############################################################
    # style--> "name"(such as AA1.1141): value(such as 1,2,3)
    # B Y G R, 0x00(B)00(Y)00(G)00(R), 0(1:OK,0:Err)0(1:On,0:Off)
    ###############################################################
    # check handle status
    hand1 = m0.find("HANDLE")
    if hand1 >= 0:
        m0 = m0[0:hand1-1]
        x_data = detecthandle(cropped)
        if x_data[0] == 1:
            if x_data[1] == 'W':
                r_data = 0xC0
            else:
                r_data = 0x80
        else:
            r_data = 0x00
    else:
        # check lamp status
        pos1 = m0.find("GREEN")
        pos2 = m0.find("RED")
        pos3 = m0.find("YELLOW")
        if pos1 >=0:  # GREEN
            m0 = m0[0:pos1-1]
            tmp = send_data.get(m0)
            if tmp == None:
                tmp = 0
            r_data = tmp + 8
            x_data = detectsingle(cropped)
            if len(x_data) > 0:
                if x_data[0][1] == 'N' or x_data[0][1] == 'E':
                    r_data = r_data
                else:
                    r_data = r_data + 4
        elif pos2 >= 0: # RED
            m0 = m0[0:pos2-1]
            tmp = send_data.get(m0)
            if tmp == None:
                tmp = 0
            r_data = tmp + 2
            x_data = detectsingle(cropped)
            if len(x_data) > 0:
                if x_data[0][1] == 'N' or x_data[0][1] == 'E':
                    r_data = r_data
                else:
                    r_data = r_data + 1
        elif pos3 >= 0: # YELLOW
            m0 = m0[0:pos3-1]
            tmp = send_data.get(m0)
            if tmp == None:
                tmp = 0
            r_data = tmp + 32
            x_data = detectsingle(cropped)
            if len(x_data) > 0:
                if x_data[0][1] == 'N' or x_data[0][1] == 'E':
                    r_data = r_data
                else:
                    r_data = r_data + 16
        else:
            r_data = 10
            x_data = detectstatus(cropped)
            if x_data is None:
                r_data = 0  # default R:off, G:off
            elif len(x_data):
                #parse status of lamp
                x = len(x_data)
                y = 0
                while x:
                    tmp0 = x_data[y]
                    tmp1 = tmp0[1]
                    if tmp1 == 'R':
                        r_data = r_data + 1
                    elif tmp1 == 'G':
                        r_data = r_data + 4
                    elif tmp1 == 'E':
                        r_data = 0
                    else:
                        r_data = r_data
                    x = x - 1
                    y = y + 1
                    #print ("lamp status data is %d", (r_data))
            else:
                r_data = 0
    return m0, r_data


#requrl = "/mqtt/send/offlinecache"
#connection = "127.0.0.1:7788"

#reload(sys)
#sys.setdefaultencoding("utf-8")

#img_counter = 0


# read annotation configuration
# input: num--index of annotation file(annoX.json, X is num)
# output: counter--number of target, matrix--coordinate of target
def read_anno_config(fileurl):
    counter = 0
    matrix = []
    # fileurl = "./config/anno"+str(num)+".json"
    with open(fileurl) as load_f:
        load_dict = json.load(load_f)
        load_dict1 = load_dict["shapes"]
        for val in load_dict1:
            counter = counter + 1
            print (val)
            print (counter)
            matrix.append(val["label"])
            matrix.append(val["points"])
        print (matrix)
    return counter,matrix

# Detection entry
# input: img data with jpg encode, annotation matrix and target_number
# output: send_data
def entry_detect(jpgframe, target_num, target_matrix):
    # frame = cv2.imdecode(jpgframe, cv2.IMREAD_COLOR)
    frame = jpgframe
    # cv2.imshow("xyz",frame)
    # cv2.waitKey(2)
    # frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
    #crop image and detect status
    i = target_num
    j = 0
    send_data = {}
    while i:
        m0,r_data = region_detect(i,j,frame,target_matrix)
        send_data.update({m0: r_data})
        i = i - 1
        j = j + 1
    return send_data
    #send detection result to network
    #print send_data
    #post_data(send_data,requrl,connection)
    #img_counter += 1
    #print("frame counter is: %d" %(img_counter))
    #time.sleep(2)

# release opencv window, at the end of program
# input: none
# output: none
def release_detect():
    cv2.destroyAllWindows()
    time.sleep(2)   #delay 2s
