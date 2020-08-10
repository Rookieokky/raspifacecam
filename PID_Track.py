import cv2
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import pantilthat #pantilthat.pan, pantilhat.tilt
from vidgear.gears import PiGear
from vidgear.gears import NetGear
from simple_pid import PID

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def has_big_rect(face_rectangle):
    if len(face_rectangle)==0:
        return False,-1
    for i,rect in enumerate(face_rectangle):
        if rect[2]>80:
            return True,i
    return False,-1





FRAMERATE=10
im_size = (960, 544)

VCONST=6/(im_size[1]/2) #6 degrees per half camera vertical rotation
HCONST=14/(im_size[0]/2) #14 degrees per half camera horizontal rotation


pan_PID=PID(0.5,0,0.1,sample_time=1/FRAMERATE,setpoint=0,proportional_on_measurement=True,output_limits=(-im_size[1]/2,im_size[1]/2))
tilt_PID=PID(0.5,0,0.1,sample_time=1/FRAMERATE,setpoint=0,proportional_on_measurement=True,output_limits=(-im_size[0]/2,im_size[0]/2))


stream = PiGear(resolution=im_size, framerate=FRAMERATE, logging=True).start()

options = {'bidirectional_mode': True,'compression_format': '.jpg','compression_param':[cv2.IMWRITE_JPEG_QUALITY, 70]} #activates jpeg encoding to reduce bandwith

server = NetGear(address = '192.168.0.113', port = '5454', protocol = 'tcp',  pattern = 1, logging = True, **options)

try:
    pantilthat.idle_timeout(0.5)

    # Read video

    time.sleep(0.1)
    pantilthat.pan(-30)
    pantilthat.tilt(85)

    while True:
        rec_center=None
        frame=stream.read()
        recv_data = server.send(frame)
        if recv_data is None:
            break
        dir=0
        if isinstance(recv_data,str):
            continue

        rec_center=recv_data
        pan_deg=pantilthat.get_pan()
        tilt_deg=pantilthat.get_tilt()

        if rec_center is not None:
            horiz=im_size[0]//2-rec_center[0]
            vert=im_size[1]//2-rec_center[1]

            horiz_desired=tilt_PID(horiz)
            vert_desired=pan_PID(vert)

            next_pan_deg=pan_deg+VCONST*vert_desired
            next_tilt_deg=tilt_deg+HCONST*horiz_desired

            next_pan_deg=clamp(next_pan_deg,-65,65)
            next_tilt_deg=clamp(next_tilt_deg,-90,90)
            print(VCONST*vert_desired,HCONST*horiz_desired)
            pantilthat.pan(next_pan_deg)
            pantilthat.tilt(next_tilt_deg)


finally:
    cv2.destroyAllWindows()
    stream.stop()
    server.close()