# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in
import json
import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.model_selection import cross_val_score
from sklearn import svm
from scipy import stats
from scipy.interpolate import interp1d
import itertools
import numpy as np
from sklearn import preprocessing
from sklearn.externals import joblib

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output

# print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.

def cross_val_svm(X, y, n):
    clf = svm.SVC()
    scores = cross_val_score(clf, X, y, cv = n)
    return scores


def vectors_labels(list1, list2):
    def label(l):
        return lambda x: l

    X = list1 + list2
    y = list(map(label(0), list1)) + list(map(label(1), list2))
    return X, y


def spectrum(vector):
    '''get the power spectrum of a vector of raw EEG data'''
    A = np.fft.fft(vector)
    ps = np.abs(A) ** 2
    ps = ps[:len(ps) // 2]
    return ps


def binned(pspectra, n):
    '''compress an array of power spectra into vectors of length n'''
    l = len(pspectra)
    array = np.zeros([l, n])
    for i, ps in enumerate(pspectra):
        x = np.arange(1, len(ps) + 1)
        f = interp1d(x, ps)  # /np.sum(ps))
        array[i] = f(np.arange(1, n + 1))
    index = np.argwhere(array[:, 0] == -1)
    array = np.delete(array, index, 0)
    return array


def feature_vector(readings, bins = 100):  # A function we apply to each group of power spectra
    '''
    Create 100, log10-spaced bins for each power spectrum.
    For more on how this particular implementation works, see:
    http://coolworld.me/pre-processing-EEG-consumer-devices/
    '''
    bins = binned(list(map(spectrum, readings)), bins)
    return np.log10(np.mean(bins, 0))


def grouper(n, iterable, fillvalue = None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue = fillvalue)


def vectors(df):
    return [feature_vector(group) for group in list(grouper(3, df.raw_values.tolist()))[:-1]]


def estimated_accuracy(subject):
    m = math[math['id'] == subject]
    r = relax[relax['id'] == subject]
    X, y = vectors_labels(vectors(m), vectors(r))
    X = preprocessing.scale(X)
    return cross_val_svm(X, y, 7).mean()


# relax = df[df.label == 'relax']
# math = df[(df.label == 'math1') |
#           (df.label == 'math2') |
#           (df.label == 'math3') |
#           (df.label == 'math4') |
#           (df.label == 'math5') |
#           (df.label == 'math6') |
#           (df.label == 'math7') |
#           (df.label == 'math8') |
#           (df.label == 'math9') |
#           (df.label == 'math10') |
#           (df.label == 'math11') |
#           (df.label == 'math12')]

def main():

    df = pd.read_csv("../mind-detech/input/input_file.csv")

    # convert to arrays from strings
    df.raw_values = df.raw_values.map(json.loads)
    df.eeg_power = df.eeg_power.map(json.loads)

    X = df.eeg_power.tolist()

    ex_readings = df.raw_values[:3]

    feature_vector(ex_readings)

    X = feature_vector(ex_readings)
    X = X.reshape(1,-1)

    clf2 = joblib.load("../mind-detech/Test.pkl")
    #print(clf2.predict(X))

    # !!!!! True means NOT Depress
    if(clf2.predict(X) == 1):
        print(True)
    else:
        print(False)

main()