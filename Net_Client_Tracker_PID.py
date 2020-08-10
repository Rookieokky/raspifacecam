from vidgear.gears import NetGear
import cv2
from simple_pid import PID

def has_big_rect(face_rectangle):
    if len(face_rectangle)==0:
        return False,-1

    found_big=False
    max_size=face_rectangle[0].shape
    ind=0
    for i,rect in enumerate(face_rectangle):
        if rect[2]>50:
            found_big=True
            if rect.shape>max_size:
                max_size=rect.shape
                ind=i
    if found_big:
        return True,ind
    else:
        return False,-1

def track_create():
    tracker=cv2.TrackerMOSSE_create()
    return tracker

FRAMERATE = 10
DETECTORCONST=5

im_size = (960, 544)

# activate Bidirectional mode
options = {'bidirectional_mode': True,'compression_param':cv2.IMREAD_COLOR}

#define NetGear Client with `receive_mode = True` and defined parameter
client = NetGear(address = '192.168.0.113', port = '5454', protocol = 'tcp',  pattern = 1, receive_mode = True, logging = True, **options)

target_data="PROTOCOL_1"
data = client.recv(return_data=target_data)
_,frame=data

# We will first detect the face and set that as our starting box.
face_cascade = cv2.CascadeClassifier('HAAR/haarcascade_frontalface_default.xml')
tracker = track_create()
tracker_name = str(tracker).split()[0][1:]

frame = cv2.flip(frame, 0)
face_rects = face_cascade.detectMultiScale(frame)

while len(face_rects) == 0:
    target_data = "PROTOCOL_1"
    data = client.recv(return_data=target_data)
    _, frame = data
    frame = cv2.flip(frame, 0)
    face_rects = face_cascade.detectMultiScale(frame)

# Convert this list of a single array to a tuple of (x,y,w,h)
roi = tuple(face_rects[0])


# Initialize tracker with first frame and bounding box
ret = tracker.init(frame, roi)
print(frame.shape)
index = 0
target_data="PROTOCOL_2"
track_fail=False
# loop over
try:
    while True:
        # receive data from server and also send our data
        data = client.recv(return_data = target_data)
        #time.sleep(0.05)
        # check for data if None
        if data is None:
            print ("No data received.")
            break
        # extract server_data & frame from data
        _, frame = data
        # again check for frame if None
        if frame is None:
            break

        frame = cv2.flip(frame, 0)

        if frame is not None:
            ret = True
        else:
            ret = False
        index += 1
        if index > DETECTORCONST*(FRAMERATE)-1:
            index = 0
        print(index)
        if index == DETECTORCONST*(FRAMERATE)-1 or track_fail:  # every 16 frames
            face_rects = face_cascade.detectMultiScale(frame)  # attempt to find new face
            boolret, ind = has_big_rect(face_rects)
            cv2.putText(frame, "Detecting..", (230, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255),3)
            if len(face_rects) and boolret != 0:
                for i, fce in enumerate(face_rects):
                    print(i, fce)
                    del tracker  # if you find it, reinitialize tracker
                    tracker = track_create()
                    ret = tracker.init(frame, tuple(face_rects[ind]))
                    index = 0
            else:
                print("Detector Fail")
                index -= 1  # else try again next frame


            # Update tracker
        success, roi = tracker.update(frame)

        # roi variable is a tuple of 4 floats
        # We need each value and we need them as integers
        (x, y, w, h) = tuple(map(int, roi))
        # Draw Rectangle as Tracker moves
        rectangle_cntr = "fail"  # direction
        track_fail=False
        if success:
            # Tracking success
            p1 = (x, y)
            p2 = (x + w, y + h)
            cv2.rectangle(frame, p1, p2, (0, 255, 0), 3)
            rectangle_cntr = (x + w // 2, y + h // 2)
            cv2.circle(frame, rectangle_cntr, 5, (0, 255, 0), 2)
        else:
            # Tracking failure
            track_fail=True
            cv2.putText(frame, "Tracking Failure!!", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 3)

            # Display tracker type on frame
        cv2.putText(frame, tracker_name, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)


        # Display result
        cv2.imshow(tracker_name, frame)

        # send servo data
        target_data=rectangle_cntr

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
finally:
    cv2.destroyAllWindows()
    client.close()
