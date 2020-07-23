import numpy as np
import shutil
import sys
import pickle

import os
from os import listdir, mkdir
from os.path import isfile, join, isdir

import cv2 as cv
from cv2 import *

# Konstanten
SOURCE_DIR_NAME = "Source"
TRAINING_DIR_NAME = "Training"
TESTING_DIR_NAME = "Testing"
TRAINING_RESOLUTION = 50


# Argumentenliste
argWithTesting = True
argModelFilename = "ToverlandSpellModel"

                   
# Globale Variabeln
knn = cv.ml.KNearest_create()


def PrepareClassification(withTesting):

    print()
    print("Die Klassifizierung wird vorbereitet ...")

    # Die Vezeichnispfade ermitterln
    workDir = os.path.realpath(__file__)
    sourceDir = join(os.path.dirname(workDir), SOURCE_DIR_NAME)
    trainingDir = join(os.path.dirname(workDir), TRAINING_DIR_NAME)
    testingDir = join(os.path.dirname(workDir), TESTING_DIR_NAME)

    # Überprüfen ob das Source-Verzeichnis existiert
    if isdir(sourceDir) is not True:
        print()
        print("ERROR: Es konnten keine Daten zum trainieren gefunden werden!")
        sys.exit(0)

    # Überprüfen ob es ein altes Training-Verzeichnis gibt
    if isdir(trainingDir):
    
        # Das alte Training-Verzeichnis mit dem Inhalt löschen
        shutil.rmtree(trainingDir)
        
    # Überprüfen ob es ein altes Testing-Verzeichnis gibt
    if isdir(testingDir):
        
        # Das alte Testing-Verzeichnis mit dem Inhalt löschen
        shutil.rmtree(testingDir)

    # Überprüfen ob nach dem Traing auch ein Testing durchgeführt werden soll
    if withTesting:
        
        # Ein neues Training-Verzeichnis erstellen
        mkdir(trainingDir)
        
        # Ein neues Testing-Verzeichnis erstellen
        mkdir(testingDir)

        # Die Quellbilder in Trainings- und Testings-Bilder aufteilen
        for d in listdir(sourceDir):
            directory = join(sourceDir, d)
            if isdir(directory):
                isTrainingFile = True
                for f in listdir(directory):
                    file = join(directory, f)
                    if isfile(file) and not f.startswith('.'):
                        if isTrainingFile:
                            destinationDir = join(trainingDir, d)
                            if not isdir(destinationDir):
                                mkdir(destinationDir)
                            shutil.copyfile(file, join(destinationDir, f))
                            isTrainingFile = False
                        else:
                            destinationDir = join(testingDir, d)
                            if not isdir(destinationDir):
                                mkdir(destinationDir)
                            shutil.copyfile(file, join(destinationDir, f))
                            isTrainingFile = True


def Training(withTesting):

    print()
    print("Das Training wird gestartet ...")
    
    # Die Vezeichnispfade ermitterln
    workDir = os.path.realpath(__file__)
    trainingDir = join(os.path.dirname(workDir), SOURCE_DIR_NAME)
    if withTesting:
        trainingDir = join(os.path.dirname(workDir), TRAINING_DIR_NAME)

    # Die Daten laden
    nameLookup = {}
    labelNames = []
    labelIndexes = []
    trainingSet = []
    numPics = 0
    dirCount = 0
    for d in listdir(trainingDir):
        nameLookup[dirCount] = d
        dirCount = dirCount + 1
        for f in listdir(join(trainingDir, d)):
            if isfile(join(trainingDir, d, f)):
                labelNames.append(d)
                labelIndexes.append(dirCount - 1)
                trainingSet.append(join(trainingDir, d, f))
                numPics = numPics + 1

    print()
    print("Folgende Daten wurden für das Training gefunden: ")
    for nl in nameLookup:
        print(nameLookup[nl])

    # Das Training starten
    samples = []
    for i in range(0, numPics):
        img = cv.imread(trainingSet[i])
        grayImg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        samples.append(grayImg)
        npArray = np.array(samples)
        shapedArray = npArray.reshape(-1, TRAINING_RESOLUTION * TRAINING_RESOLUTION).astype(np.float32)
    knn.train(shapedArray, cv.ml.ROW_SAMPLE, np.array(labelIndexes))
    print()
    print("Das Training wurde gestartet ...")

    # Das Ergebnis des Trainings speichern
    modelFile = join(os.path.dirname(os.path.dirname(workDir)), argModelFilename + ".yml")
    modelResultFile = join(os.path.dirname(os.path.dirname(workDir)), argModelFilename + ".res")
    knn.save(modelFile)
    nameLookupFile = open(modelResultFile, "wb")
    pickle.dump(nameLookup, nameLookupFile)
    nameLookupFile.close()
    
    print()
    print("Das Klassifizierungsmodell wurde erstellt und gespeichert: ", modelFile)


def Testing():

    print()
    print("Das Testing wurde gestartet ...")

    # Die Vezeichnispfade ermitterln
    workDir = os.path.realpath(__file__)
    testingDir = join(os.path.dirname(workDir), "/..", TESTING_DIR_NAME)

    # Die Daten laden
    nameLookup = {}
    labelNames = []
    labelIndexes = []
    testingSet = []
    numPics = 0
    dirCount = 0
    for d in listdir(testingDir):
        nameLookup[dirCount] = d
        dirCount = dirCount + 1
        for f in listdir(join(testingDir, d)):
            if isfile(join(testingDir, d, f)):
                labelNames.append(d)
                labelIndexes.append(dirCount - 1)
                testingSet.append(join(testingDir, d, f))
                numPics = numPics + 1

    # Das Testing starten
    samples = []
    for i in range(0, numPics):
        img = cv.imread(testingSet[i])
        grayImg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        samples.append(grayImg)
        npArray = np.array(samples)
        shapedArray = npArray.reshape(-1, TRAINING_RESOLUTION * TRAINING_RESOLUTION).astype(np.float32)
    ret, result, neighbours, dist = knn.find_nearest(shapedArray, k=5)
    print()
    print("Das Training wird gestartet ...")


# Main
PrepareClassification(argWithTesting)
Training(argWithTesting)
if argWithTesting:
    #Testing()
    pass
print()
print("Fertig!")

