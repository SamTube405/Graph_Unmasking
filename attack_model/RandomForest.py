import matplotlib as mpl
mpl.use('Agg')

from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold

import matplotlib.pyplot as plt


from imblearn import over_sampling as ovsample
from imblearn import pipeline as pl
import csv_io
import sys
import os
import numpy as np
import itertools
import logging
import pandas as pd
import errno

from multiprocessing import Pool, Lock

def chkDir(path):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def writeFile(text,fileName):
    chkDir(fileName)
    lock.acquire()
    try:
        f = open(fileName, "a")
        f.write(text)
    finally:
        lock.release()
    

def getPairsDir(fileName):
    path=""
    tags = fileName.split("/")
    for i in range(0,len(tags)-1):
        path+=tags[i]+"/"
    return path

def getTag(fileName):
    tags = fileName.split("/")
    return tags[len(tags) - 1].split(".")[0]


class LBLRFImbalanced:
    def __init__(self,fn,X,y):
        plotPath=getPairsDir(fn)+"/plots"
        tag=getTag(fn)
        rf = RandomForestClassifier(n_estimators=100)

        pipeline = pl.make_pipeline(
            # ovsample.SMOTE(ratio="auto"),
            # LinearSVC(random_state=42),
            rf)

        # Split the data, note that random state is for consistent split, not define the position
        # stratify will adhere to the same class ratio in the traning set
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.4, test_size=0.6, random_state=42,
                                                            stratify=y)

        # print "Training: %d, Testing: %d" % (len(X_test), len(y_test))
        # print y_test
        # Train the classifier with balancing
        pipeline.fit(X_train, y_train)

        # Test the classifier and get the prediction
        y_pred_bal = pipeline.predict(X_test)

        feature_importance_text = ",".join(map(lambda x: str(round(x, 8)), rf.feature_importances_))
        feature_importance_text += "\n"
        writeFile(feature_importance_text, plotPath + "/" + "_features.csv")

        # 5 * 2 cv
        rkf = RepeatedStratifiedKFold(n_splits=2, n_repeats=5, random_state=42)
        cv_scores = cross_val_score(pipeline, X, y, cv=rkf, scoring='f1_macro')
        #print cv_scores
        # The mean score and the 95% confidence interval of the score estimate
        # print cv_scores['test_f1_macro']
        #print("Accuracy: %0.2f (+/- %0.2f)" % (cv_scores.mean(), cv_scores.std() * 2))

        cv_scores_text = str(cv_scores.mean())
        cv_scores_text += "\n"
        writeFile(cv_scores_text, plotPath + "/" + "_cv_scores.csv")

        precision, recall, f1_score, support = precision_recall_fscore_support(y_test, y_pred_bal)
        scores = ""
        for j in [0, 1]:
            scores += "%s,%s,%s,%s,%s\n" % (
            str(j), str(precision[j]), str(recall[j]), str(f1_score[j]), str(support[j]))
        writeFile(scores, plotPath + "/" +"_"+tag + "_RF.csv")
        #print scores

def mp_worker(fn):
    
    data=csv_io.read_data(fn,0,l=85)


    np.random.shuffle(np.array(data))
    #print len(data[0])
    y = [x[len(x)-1] for x in data]
    X = [x[0:len(x)-1] for x in data]
    #print len(X), len(X[0])
    lrf=LBLRFImbalanced(fn,X,y)

    return;


if __name__ == '__main__':
    lock = Lock()
    pool = Pool(processes=4)

    pairDir=os.path.abspath(sys.argv[1])
    

    # make dir for plots
    plotPath=pairDir+"/plots"

    try:
        os.makedirs(plotPath)
    except OSError:
        if not os.path.isdir(plotPath):
            raise


    fns=[]
    abspairDir = os.path.abspath(pairDir)
    for fn in os.listdir(abspairDir):
        if (fn.endswith("pairs.txt")):
            absfn=os.path.abspath(pairDir+"/"+fn)
            fns.append(absfn)
            #print absfn
    #print len(fns)

    pool.map(mp_worker, fns)