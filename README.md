# raspifacecam
Two python scripts utilizing the vidgear library and the Pimorino Pan-Tilt raspi HAT to create a face-tracking robot, with all opencv processing done server-side.

Run PID_track.py on the rasperry pi, and Net_Client_Tracker_PID.py on a computer located on the same Wi-Fi network.
Make sure to change the network IP's in the 2 script files to the appropriate address your network devices are using.


Requirements:
opencv2,
vidgear,
the simple_pid library,
a raspberry pi (preferably edition 4) with Wi-Fi capability,
a raspberry pi camera (scripts tested with the official camera V2) and assorted libraries (picamera[array]),
the Pimorino Pan-Tilt hat and assorted library.



The scripts are made to be modifiable. Face detection is initially made using a Haar Cascade classifier, and the appropriate cascade classifier files must be present in the DATA directory for the script to work. They can be modified and substituted for other files,if need arises.
Face tracking is then applied to the detected face. This can be done with a variety of algorithms, but from my own tests, the most suitables ones are:

1) The KCF algorithm. A bit resource intensive, but provides fairly robust results.
2) The MOSSE algorithm. Very fast and quite robust, perhaps less so than other algorithms. This is the default implementation.
3) The CSRT algorithm. By far the most robust algorithm, it is very resource intensive and is not recommended, as it induces severe delays in the video stream.

You can choose between these algorithms by changing the track_create() function in the Net_Client_Tracker_PID.py file.

Additional options: You can change the resolution of the image received as well as the camera framerate. They must be changed in both scripts for appropriate results.
By default the resolution captured is 960x544 and the framerate is 10 FPS.
The DETECTORCONST constant in the Net_Client_Tracker_PID.py script file determines how many seconds elapse between every face detection. When using lighter tracking algorithms (MOSSE or KCF), higher values are important to maximize performance. By default, this is 5.
Finally, by changing the HCONST and VCONST constants in the PID_track.py script file, you can change the speed of camera tracking according to your needs.
