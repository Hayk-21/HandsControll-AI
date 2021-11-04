import cv2
import math
import mediapipe as mp
import time
import sys
import numpy as np
import HTModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def main(settime=30):
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    pTime = 0
    detector = htm.handDetector(detectionCon=0.7)
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    # volume.GetMute()
    # volume.GetMasterVolumeLevel()
    volRange = volume.GetVolumeRange()
    minVol = volRange[0]
    maxVol = volRange[1]
    volBar = 300
    volPer = 0
    vol = 0
    cTime = time.time()
    bTime = cTime
    while True:
        if cTime - bTime > settime:
            cv2.destroyAllWindows()
            break

        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(img, (x1, y1), 6, (0, 255, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 6, (0, 255, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 6, (0, 255, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 2)

            length = math.hypot(x2 - x1, y2 - y1)
            if length < 30:
                cv2.circle(img, (x2, y2), 6, (255, 255, 0), cv2.FILLED)

            ##MAX = 120 MIN = 10
            ##Volume Range -65 -> 0
            vol = np.interp(length, [10, 120], [minVol, maxVol])
            volBar = np.interp(length, [10, 120], [300, 100])
            volPer = np.interp(length, [10, 120], [0, 100])
            volume.SetMasterVolumeLevel(vol, None)

        ########################## VOL
        cv2.rectangle(img, (10, 100), (60, 300), (0, 255, 0), 3)
        cv2.rectangle(img, (10, int(volBar)), (60, 300), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (20, 350), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        ########################## FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
        ##############################
        cv2.imshow("Img", img)
        cv2.waitKey(1)

main()