import numpy as np
import time
import math
import pickle

import os
from os.path import join

import cv2 as cv
from cv2 import *

import threading
from threading import Thread

from statistics import mean


# Kanstanten
DESIRED_FPS = 42
DEFAULT_FPS = 42
TRAINING_RESOLUTION = 50
NUM_DISTANCES_TO_AVERAGE = int(round(20 * (DESIRED_FPS / DEFAULT_FPS)))
SPELL_END_MOVEMENT = 10 * (DEFAULT_FPS / DESIRED_FPS) #0.5 * (DEFAULT_FPS / DESIRED_FPS)
MIN_SPELL_LENGTH = 15 * (DESIRED_FPS / DEFAULT_FPS)
MIN_SPELL_DISTANCE = 100
MODEL_FILE_NAME = "ToverlandSpellModel"


# Argumentenliste
argVideoSource = 0


# Globale Variabeln
Frame = None
IsNewFrame = False
RemovedBackgroundFrame = None
IsNewRemovedBackgroundFrame = False
ThresholdFrame = None
IsNewThresholdFrame = False
WandPathFrame = None
SpellFrame = None
FindNewWand = True
TrackedPoints = None
WandTracks = []
lk_params = dict(winSize = (25, 25),
                 maxLevel = 7,
                 criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))
RemoveBackgroundThread = None
ThresholdThread = None
WandDetectionThread = None
videoCapture = None
backgroundSubtractor = None
nameLookup = None
knn = cv.ml.KNearest_create()


# Fenster
showOriginalFrame = False
showRemovedBackgroundFrame = False
showThresholdFrame = False
showOutputFrame = True
showSpellFrame = True


# Initialisieren
def initialize():

    global videoCapture, backgroundSubtractor, RemoveBackgroundThread, ThresholdThread, WandDetectionThread, nameLookup, knn

    # Fenster initialisieren
    if (showOriginalFrame):
        cv.namedWindow("Original")
        cv.moveWindow("Original", 0, 0)
    if (showRemovedBackgroundFrame):
        cv.namedWindow("Removed Background")
        cv.moveWindow("Removed Backgroun", 0, 480)
    if (showThresholdFrame):
        cv.namedWindow("Threshold")
        cv.moveWindow("Threshold", 640, 480)
    if (showOutputFrame):
        cv.namedWindow("Output")
        cv.moveWindow("Output", 0, 0)
    if (showSpellFrame):
        cv.namedWindow("Spell")
        cv.moveWindow("Spell", 640, 0)

    # VideoCapture initialisieren
    videoCapture = cv.VideoCapture(argVideoSource)
    backgroundSubtractor = cv.createBackgroundSubtractorMOG2()

    # Den Thread zum entfernen des Hintergrundes starten
    RemoveBackgroundThread = Thread(target = RemoveBackground)
    RemoveBackgroundThread.do_run = True
    RemoveBackgroundThread.daemon = True
    RemoveBackgroundThread.start()

    # Den Thread für das Anwenden von Threshold starten
    ThresholdThread = Thread(target = Threshold)
    ThresholdThread.do_run = True
    ThresholdThread.daemon = True
    ThresholdThread.start()

    # 
    WandDetectionThread = Thread(target = WandDetection)
    WandDetectionThread.do_run = True
    WandDetectionThread.daemon = True
    WandDetectionThread.start()

    #
    workDir = os.path.realpath(__file__)
    nameLookupFile = open(join(os.path.dirname(workDir), MODEL_FILE_NAME + ".res"), "rb")
    nameLookup = pickle.load(nameLookupFile)
    nameLookupFile.close()
    print(nameLookup)

    #
    fs = cv.FileStorage(join(os.path.dirname(workDir), MODEL_FILE_NAME + ".yml"), cv.FILE_STORAGE_READ)
    knn_yml = fs.getNode("opencv_kenn")
    knn_format = knn_yml.getNode("format").real()
    is_classifier = knn_yml.getNode("is_classifier").real()
    default_k = knn_yml.getNode("default_k").real()
    samples = knn_yml.getNode("samples").mat()
    responses = knn_yml.getNode("responses").mat()
    fs.release
    knn.train(samples, cv.ml.ROW_SAMPLE, responses)


def destroy():

    # Threads stoppen
    RemoveBackgroundThread.do_run = False
    RemoveBackgroundThread.join()
    ThresholdThread.do_run = False
    ThresholdThread.join()
    WandDetectionThread.do_run = False
    WandDetectionThread.join()

    # Resourcen freigeben
    videoCapture.release()

    # Alle Fenser schließen
    cv.destroyAllWindows()

    
def updateWindows():

    # Die entsprechenden Frames anzeigenl
    if Frame is not None and showOriginalFrame:
        cv.imshow("Original", Frame)
    if RemovedBackgroundFrame is not None and showRemovedBackgroundFrame:
        cv.imshow("Removed Background", RemovedBackgroundFrame)
    if ThresholdFrame is not None and showThresholdFrame:
        cv.imshow("Threshold", ThresholdFrame)
    if WandPathFrame is not None and showOutputFrame:
        cv.imshow("Output", WandPathFrame)
    if SpellFrame is not None and showSpellFrame:
        cv.imshow("Spell", SpellFrame)


# Eine Zauberstarbbewegung erkennen
def CheckForPattern(wandTracks, frame):

    global WandPathFrame, FindNewWand, SpellFrame

    if (wandTracks is None or len(wandTracks) == 0):
        return

    thickness = 10
    croppedMax = TRAINING_RESOLUTION - thickness

    distances = []
    WandPathFrame = np.zeros_like(frame)
    prevTrack = wandTracks[0]

    for track in wandTracks:
        x1 = prevTrack[0]
        x2 = track[0]
        y1 = prevTrack[1]
        y2 = track[1]

        distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        distances.append(distance)

        cv.line(WandPathFrame, (x1, y1), (x2, y2), (255, 255, 255), thickness)
        prevTrack = track

    mostRecentDistances = distances[-NUM_DISTANCES_TO_AVERAGE:]
    avgMostRecentDistances = mean(mostRecentDistances)
    sumDistances = sum(distances)

    contours, hierarchy = cv.findContours(WandPathFrame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if (avgMostRecentDistances < SPELL_END_MOVEMENT and len(distances) > MIN_SPELL_LENGTH):
        if (len(contours) > 0) and sumDistances > MIN_SPELL_DISTANCE:

            cnt = contours[0]
            x, y, w, h = cv.boundingRect(cnt)
            crop = WandPathFrame[y-10:y+h+10, x-30:x+w+30]
            result = ClassifyImage(crop)

            wandPathFrameCopy = WandPathFrame.copy()
            cv.putText(wandPathFrameCopy, result, (0, 50), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
            SpellFrame = wandPathFrameCopy.copy()
            #print("Result: ", result)
            #print("Most Recent avg: ", avgMostRecentDistances)
            #print("Length Distances: ", len(distances))
            #print("Sum Distances: ", sumDistances)
            #print("")
            
            PerformSpell(result)

        FindNewWand = True
        wandTracks.clear()

    return wandTracks


#
def ClassifyImage(image):

    return "Test-Spell"


#
def PerformSpell(spell):
    pass
    

# Thread: Zum entfernen des Hintergrundes
def RemoveBackground():

    # 
    global Frame, RemovedBackgroundFrame, IsNewFrame, IsNewRemovedBackgroundFrame

    #
    t = threading.currentThread()
    while getattr(t, "do_run", True):

        # Überprüfen ob es einen neuen Frame gibt
        if IsNewFrame:
            IsNewFrame = False

            # Eine Arbeitskopie des Frames erstelle
            frameCopy = Frame.copy()

            # Den Hintergrund im Frame entfernen
            #frameMask = backgroundSubtractor.apply(frameCopy)
            frameMask = backgroundSubtractor.apply(frameCopy, learningRate = 0.001)
            RemovedBackgroundFrame = cv.bitwise_and(frameCopy, frameCopy, mask = frameMask)
            IsNewRemovedBackgroundFrame = True
            
        else:
            time.sleep(0.001)


# Thread: Für das Anwenden von Threshold
def Threshold():

    # 
    global Frame, RemovedBackgroundFrame, ThresholdFrame, IsNewFrame, IsNewRemovedBackgroundFrame, IsNewThresholdFrame

    #
    t = threading.currentThread()
    while getattr(t, "do_run", True):

        # Überprüfen ob es einen neuen Frame gibt
        if IsNewRemovedBackgroundFrame:
            IsNewRemovedBackgroundFrame = False

            # Eine Arbeitskopie des Frames erstelle
            frameCopy = RemovedBackgroundFrame.copy()

            # Den Threshold anfenden
            grayFrame = cv.cvtColor(frameCopy, cv.COLOR_BGR2GRAY)
            ret, localFrame = cv.threshold(grayFrame, 240, 255, cv.THRESH_BINARY)
            if ret:
                ThresholdFrame = localFrame.copy()
                IsNewThresholdFrame = True
            else:
                time.sleep(0.001)

        else:
            time.sleep(0.001)


# Thread: 
def WandDetection():

    # 
    global ThresholdFrame, IsNewThresholdFrame, FindNewWand, WandTracks

    #
    oldThresholdFrame = None
    trackedPoints = None
    t = threading.currentThread()
    while getattr(t, "do_run", True):

        # Überprüfen ob es einen neuen Frame gibt
        if IsNewThresholdFrame:
            IsNewThresholdFrame = False

            # Eine Arbeitskopie des Frames erstelle
            frameCopy = ThresholdFrame.copy()

            if FindNewWand:

                # Potenzielle Zauberstabspitzen identifizieren
                TrackedPoints = cv.goodFeaturesToTrack(frameCopy, 5, .01, 30)

                # Überprüfen ob Zauberstabspitzen gefunden wurden
                if TrackedPoints is not None:
                    FindNewWand = False

            else:

                # Die Zeuberstabspitzenbewegung erfassen
                nextPoints, statusArray, error = cv.calcOpticalFlowPyrLK(oldThresholdFrame, frameCopy, TrackedPoints, None, **lk_params)
                newGoodPoints = nextPoints[statusArray==1]
                oldGoodPoints = TrackedPoints[statusArray==1]
                if len(newGoodPoints) > 0:
                    for i, (new, old) in enumerate(zip(newGoodPoints, oldGoodPoints)):
                        a, b = new.ravel()
                        c, d = old.ravel()
                        WandTracks.append([a, b])

                    TrackedPoints = newGoodPoints.copy().reshape(-1, 1, 2)
                    WandTracks = CheckForPattern(WandTracks, frameCopy)

                else:
                    WandTracks = []
                    FindNewWand = True

            oldThresholdFrame = frameCopy
            
        else:
            time.sleep(0.001)


# Initialisierung
initialize()


# Main Loop
while True:

    # Das aktuelle Frame abrufen
    ret, localFrame = videoCapture.read()
    if (ret):

        # Eine Arbeitskopie des Frames erstellen
        Frame = localFrame.copy()

        # Das Frame spiegeln
        cv.flip(Frame, 1, Frame)

        # Flag für eine neues Frame setzen
        IsNewFrame = True

        # Die Fenster aktualisieren
        updateWindows()

    # Überprüfen ob der ESC-Key betätigt wurde
    if (cv.waitKey(1) is 27):

        # Beenden
        destroy()
        break


        
        
    
    
