__author__ = "Pierluigi Gallo"
__copyright__ = "Copyright (c) 2017, CNIT"
__version__ = "0.1.0"
__email__ = "pierluigi.gallo@cnit.it"


# print(__doc__)

import itertools
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from matplotlib.pyplot import plot as plt, draw, show

from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
import time
from sklearn.externals import joblib
import os
import json
import bisect
from decimal import *
getcontext().prec = 2

def sequence_to_array(input_data):
    """
    This function converts (in a proper way) the DataFrame returned by pandas, into a matrix numpy.ndarray
    This is the right input format accepted by scikit-learn
    :param a: 
    :return: 
    """

    ##### input data (Pandas DataFrame)
    #    192.168.0.1                                192.168.0.3                                         192.168.0.5
    # [[1495465720.0857723, 15, 7, 116, 115]] [[1495465720.0218935, 12592, 16, 73, 73]]  [[1495465720.004212, 11750663, 4085872, 2047131, 2163431]]
    # [[1495465720.0857723, 15, 7, 116, 115]] [[1495465720.0218935, 12592, 16, 73, 73]]  [[1495465720.004212, 11750663, 4085872, 2047131, 2163431]]
    # [[1495465720.0857723, 15, 7, 116, 115]] [[1495465720.0218935, 12592, 16, 73, 73]]  [[1495465720.004212, 11750663, 4085872, 2047131, 2163431]]
    # ....

    # output data
    # output_data['node] = '192.168.0.1'
    # output_data ['measure'] = [[1495465720.0857723, 15, 7, 116, 115], [1495465720.0857723, 15, 7, 116, 115], ...]
    # # create a numpy array with the numeric values for input into scikit-learn
    data_dictionary = dict()
    node_addresses = list(df.columns.values)

    (num_readings, num_nodes) = list(input_data.shape)
    num_types_of_measurements = len(input_data[node_addresses[0]][0][0])
    print ("num readings %d" %num_readings)
    print ("num of nodes %d" %num_nodes)
    print ("num of types of measurements %d" %len(input_data[node_addresses[0]][0][0]))



    for nodeid in range(len(node_addresses)):
        # initialize with a line of zeros
        data_mat = [0] * num_types_of_measurements
        for ii in range(num_readings):
            row = input_data[node_addresses[nodeid]][ii][0]
            data_mat = np.vstack((data_mat, row))
        data_mat = data_mat[1:, :]
        data_dictionary[node_addresses[nodeid]] = data_mat
    return data_dictionary


def nodedata_to_array(input_data):
    # number of elements containing 'None'
    toberemoved = np.sum(input_data.isnull())

    dims = input_data.values.shape
    print("input data has %d rows" %(dims[0]))
    # num_types_of_measurements = len(input_data[0][0][0])
    num_types_of_measurements = len(input_data.values[0][0])
    matrix = [0] * num_types_of_measurements
    for ii in range(dims[0]-toberemoved):
        row = input_data.values[ii][0]
        if row!= None:
            matrix = np.vstack((matrix, row))
    matrix = matrix[1:, :]
    return matrix

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        np.set_printoptions(precision=2)

        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    # print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        tmp = format(cm[i,j], '.2f')
        plt.text(j, i, tmp,
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

# set data source in
# - "iris"   (example dataset for flower classification on petals and sepals)
# - "matlab" (matlab mesh simulator written by P. Gallo)
# - "wilab"  (wilab experiment )
data_source = "wilab"

############################### data from example

# import some data to play with
if(data_source == "iris"):
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    print ("X = %s" %X)
    print ("y = %s" %y)
    class_names = iris.target_names
    # put the original column names in a python list
    original_headers = list(df.columns.values)
    # remove the non-numeric columns
    df = df._get_numeric_data()
    # put the numeric column names in a python list
    numeric_headers = list(df.columns.values)
    # create a numpy array with the numeric values for input into scikit-learn
    numpy_array = df.as_matrix()
    # set printing options to print all data rather than a selection
    np.set_printoptions(threshold=sys.maxint)
    # Split the data into a training set and a test set
    X_train, X_test, y_train, y_test = train_test_split(X, y.astype(int), random_state=0)

############################### data from matlab simulations
# header description
# 0 node_ident,             - not to be used
# 1 radius,                 - not to be used
# 2 max_busy,
# 3 busy_50,
# 4 busy_90,
# 5 max_idle,
# 6 idle_50,
# 7 idle_90,
# 8 tx_neigh_G,
# 9 tx_neigh_G2,
# 10 rx_neigh_G,
# 11 rx_neigh_G2,
# 12 num_of_cliques_tx,
# 13 nodes_in_cliques_tx,
# 14 num_of_cliques_rx,
# 15 nodes_in_cliques_rx,
# 16 succ_norm_all,         - not to be used
# 17 tx_norm_all,           - not to be used
# 18 output
elif data_source == "matlab":
    df = pd.read_csv('./matlab_simulation_data2.csv')
    # put the original column names in a python list
    original_headers = list(df.columns.values)
    # remove the non-numeric columns
    df = df._get_numeric_data()
    # put the numeric column names in a python list
    numeric_headers = list(df.columns.values)
    # create a numpy array with the numeric values for input into scikit-learn
    numpy_array = df.as_matrix()
    # set printing options to print all data rather than a selection
    np.set_printoptions(threshold=sys.maxint)

    # print ("numpy_array [:,0] = %s" %(numpy_array[:, 0]))
    X = numpy_array[:, 2:16:1]
    y = numpy_array[:, 18]
    class_names = ['flow in the middle', 'hidden nodes', 'no-interf']

    # Split the data into a training set and a test set
    X_train, X_test, y_train, y_test = train_test_split(X, y.astype(int), random_state=0)

    # print ("X = %s" %numpy_array[0:3:1,2:16:1])
    # print ("y = %s" %numpy_array[0:3:1,17])



############################### data from wilab experiment
# header description
# 0 TIME
# 1 BUSY_TIME
# 2 tx_activity
# 3 num_tx
# 4 num_tx_success
elif data_source == "wilab":
    # read dataframe
    # df = pd.read_json('measure-all-cases.json')
    # sanitized_data = sequence_to_array(df)
    # # # put the numeric column names in a python list
    # node_addresses = list(df.columns.values)
    # print(node_addresses)
    #
    # X = sanitized_data['B'][:, 1:]

    # os.chdir('/Users/nicolas/Downloads')
    # Reading the json as a dict
    # with open('measure-flow-in-the-middle.json') as json_file:
    with open('measure_5_features_final.json') as json_file:
        data = json.load(json_file)
    # pd.DataFrame.from_dict(data, orient='index').T.set_index('index')
    tmp = pd.DataFrame.from_dict(data, orient='index').T

    sanitized_data = dict()
    sanitized_data['A'] = nodedata_to_array(tmp['A'])
    sanitized_data['B'] = nodedata_to_array(tmp['B'])
    sanitized_data['C'] = nodedata_to_array(tmp['C'])
    sanitized_data['D'] = nodedata_to_array(tmp['D'])
    sanitized_data['E'] = nodedata_to_array(tmp['E'])
    np.set_printoptions(precision=2)
    # np.set_printoptions() # reset
    print(sanitized_data['B'])

    plt.close("all")
    fig = plt.figure(1)


    start = 2
    ax = fig.add_subplot(1, 1, 1)
    time_reference = sanitized_data['B'][start, 0]

    # the second term is 'A' for all in order to have synchronized traces
    xa = sanitized_data['A'][start:, 0] - time_reference
    xb = sanitized_data['B'][start:, 0] - time_reference
    xc = sanitized_data['C'][start:, 0] - time_reference
    xd = sanitized_data['D'][start:, 0] - time_reference
    xe = sanitized_data['E'][start:, 0] - time_reference

    # ax.plot(x, sanitized_data[start:, 1])
    # ax.plot(x, sanitized_data[start:, 2])
    # Plot transmissions for all nodes
    ax.plot(xa, sanitized_data['A'][start:, 3])
    ax.plot(xb, sanitized_data['B'][start:, 3])
    ax.plot(xc, sanitized_data['C'][start:, 3])
    ax.plot(xd, sanitized_data['D'][start:, 3])
    ax.plot(xe, sanitized_data['E'][start:, 3])
    # ax.plot(x, sanitized_data[start:, 4])
    plt.draw()


    # # these values are taken from the figure named "training-traces.png"
    # start_time1 = 97 + time_reference
    # end_time1 = 136  + time_reference
    # start_time2 = 145 + time_reference
    # end_time2 = 194  + time_reference
    # start_time3 = 210 + time_reference
    # end_time3 = 278  + time_reference
    # start_time4 = 331 + time_reference
    # end_time4 = 438  + time_reference
    # start_time5 = 486 + time_reference
    # end_time5 = 576  + time_reference
    # start_time6 = 754 + time_reference
    # end_time6 = 896 + time_reference
    #

    # these values are taken from measure_5_features_final.json"
    start_time1 = 140 + time_reference
    end_time1 = 172  + time_reference
    start_time2 = 180 + time_reference
    end_time2 = 211  + time_reference
    start_time3 = 225 + time_reference
    end_time3 = 283  + time_reference
    start_time4 = 315 + time_reference
    end_time4 = 381 + time_reference
    start_time5 = 493 + time_reference
    end_time5 = 619  + time_reference
    start_time6 = 656 + time_reference
    end_time6 = 780 + time_reference



    # # start_time6 = 820 + time_reference
    # # end_time6 = 896 + time_reference
    # start_time6 = 754 + time_reference
    # end_time6 = 800 + time_reference

    # finds the
    startpos1=dict()
    startpos1['A'] = bisect.bisect(sanitized_data['A'][:, 0], start_time1)
    startpos1['B'] = bisect.bisect(sanitized_data['B'][:, 0], start_time1)
    startpos1['C'] = bisect.bisect(sanitized_data['C'][:, 0], start_time1)
    startpos1['D'] = bisect.bisect(sanitized_data['D'][:, 0], start_time1)
    startpos1['E'] = bisect.bisect(sanitized_data['E'][:, 0], start_time1)

    startpos2 = dict()
    startpos2['A'] = bisect.bisect(sanitized_data['A'][:, 0], start_time2)
    startpos2['B'] = bisect.bisect(sanitized_data['B'][:, 0], start_time2)
    startpos2['C'] = bisect.bisect(sanitized_data['C'][:, 0], start_time2)
    startpos2['D'] = bisect.bisect(sanitized_data['D'][:, 0], start_time2)
    startpos2['E'] = bisect.bisect(sanitized_data['E'][:, 0], start_time2)

    startpos3 = dict()
    startpos3['A'] = bisect.bisect(sanitized_data['A'][:, 0], start_time3)
    startpos3['B'] = bisect.bisect(sanitized_data['B'][:, 0], start_time3)
    startpos3['C'] = bisect.bisect(sanitized_data['C'][:, 0], start_time3)
    startpos3['D'] = bisect.bisect(sanitized_data['D'][:, 0], start_time3)
    startpos3['E'] = bisect.bisect(sanitized_data['E'][:, 0], start_time3)

    startpos4 = dict()
    startpos4['A'] = bisect.bisect(sanitized_data['A'][:, 0], start_time4)
    startpos4['B'] = bisect.bisect(sanitized_data['B'][:, 0], start_time4)
    startpos4['C'] = bisect.bisect(sanitized_data['C'][:, 0], start_time4)
    startpos4['D'] = bisect.bisect(sanitized_data['D'][:, 0], start_time4)
    startpos4['E'] = bisect.bisect(sanitized_data['E'][:, 0], start_time4)

    startpos5 = dict()
    startpos5['A'] = bisect.bisect(sanitized_data['A'][:, 0], start_time5)
    startpos5['B'] = bisect.bisect(sanitized_data['B'][:, 0], start_time5)
    startpos5['C'] = bisect.bisect(sanitized_data['C'][:, 0], start_time5)
    startpos5['D'] = bisect.bisect(sanitized_data['D'][:, 0], start_time5)
    startpos5['E'] = bisect.bisect(sanitized_data['E'][:, 0], start_time5)

    startpos6 = dict()
    startpos6['A'] = bisect.bisect(sanitized_data['A'][:, 0], start_time6)
    startpos6['B'] = bisect.bisect(sanitized_data['B'][:, 0], start_time6)
    startpos6['C'] = bisect.bisect(sanitized_data['C'][:, 0], start_time6)
    startpos6['D'] = bisect.bisect(sanitized_data['D'][:, 0], start_time6)
    startpos6['E'] = bisect.bisect(sanitized_data['E'][:, 0], start_time6)

    endpos1 = dict()
    endpos1['A'] = bisect.bisect(sanitized_data['A'][:, 0], end_time1)
    endpos1['B'] = bisect.bisect(sanitized_data['B'][:, 0], end_time1)
    endpos1['C'] = bisect.bisect(sanitized_data['C'][:, 0], end_time1)
    endpos1['D'] = bisect.bisect(sanitized_data['D'][:, 0], end_time1)
    endpos1['E'] = bisect.bisect(sanitized_data['E'][:, 0], end_time1)

    endpos2 = dict()
    endpos2['A'] = bisect.bisect(sanitized_data['A'][:, 0], end_time2)
    endpos2['B'] = bisect.bisect(sanitized_data['B'][:, 0], end_time2)
    endpos2['C'] = bisect.bisect(sanitized_data['C'][:, 0], end_time2)
    endpos2['D'] = bisect.bisect(sanitized_data['D'][:, 0], end_time2)
    endpos2['E'] = bisect.bisect(sanitized_data['E'][:, 0], end_time2)

    endpos3 = dict()
    endpos3['A'] = bisect.bisect(sanitized_data['A'][:, 0], end_time3)
    endpos3['B'] = bisect.bisect(sanitized_data['B'][:, 0], end_time3)
    endpos3['C'] = bisect.bisect(sanitized_data['C'][:, 0], end_time3)
    endpos3['D'] = bisect.bisect(sanitized_data['D'][:, 0], end_time3)
    endpos3['E'] = bisect.bisect(sanitized_data['E'][:, 0], end_time3)

    endpos4 = dict()
    endpos4['A'] = bisect.bisect(sanitized_data['A'][:, 0], end_time4)
    endpos4['B'] = bisect.bisect(sanitized_data['B'][:, 0], end_time4)
    endpos4['C'] = bisect.bisect(sanitized_data['C'][:, 0], end_time4)
    endpos4['D'] = bisect.bisect(sanitized_data['D'][:, 0], end_time4)
    endpos4['E'] = bisect.bisect(sanitized_data['E'][:, 0], end_time4)

    endpos5 = dict()
    endpos5['A'] = bisect.bisect(sanitized_data['A'][:, 0], end_time5)
    endpos5['B'] = bisect.bisect(sanitized_data['B'][:, 0], end_time5)
    endpos5['C'] = bisect.bisect(sanitized_data['C'][:, 0], end_time5)
    endpos5['D'] = bisect.bisect(sanitized_data['D'][:, 0], end_time5)
    endpos5['E'] = bisect.bisect(sanitized_data['E'][:, 0], end_time5)

    endpos6 = dict()
    endpos6['A'] = bisect.bisect(sanitized_data['A'][:, 0], end_time6)
    endpos6['B'] = bisect.bisect(sanitized_data['B'][:, 0], end_time6)
    endpos6['C'] = bisect.bisect(sanitized_data['C'][:, 0], end_time6)
    endpos6['D'] = bisect.bisect(sanitized_data['D'][:, 0], end_time6)
    endpos6['E'] = bisect.bisect(sanitized_data['E'][:, 0], end_time6)

    print(startpos1)
    print(startpos2)
    print(startpos3)
    print(startpos4)
    print(startpos5)
    print(startpos6)


    ############### measure_long_4_training

    # ####### NO INTERFERENCE
    # # first time slot
    # low_interference_data = sanitized_data['B'][startpos1['B']:endpos1['B'], :]
    # low_interference_class = [1] * len(low_interference_data)
    #
    # # tmp = sanitized_data['B'][startpos1['B']:endpos1['B'], :]
    # # low_interference_data = np.vstack((low_interference_data, tmp))
    # # low_interference_class = np.concatenate((low_interference_class, [1] * len(tmp)))
    # #
    # # tmp = sanitized_data['E'][startpos1['E']:endpos1['E'], :]
    # # low_interference_data = np.vstack((low_interference_data, tmp))
    # # low_interference_class = np.concatenate((low_interference_class, [1] * len(tmp)))
    #
    # # second time slot
    # tmp = sanitized_data['E'][startpos2['E']:endpos2['E'], :]
    # low_interference_data = np.vstack((low_interference_data, tmp))
    # low_interference_class = np.concatenate((low_interference_class, [1] * len(tmp)))
    #
    # # third time slot
    # tmp = sanitized_data['D'][startpos3['D']:endpos3['D'], :]
    # low_interference_data = np.vstack((low_interference_data, tmp))
    # low_interference_class = np.concatenate((low_interference_class, [1] * len(tmp)))
    #
    # tmp = sanitized_data['E'][startpos3['E']:endpos3['E'], :]
    # low_interference_data = np.vstack((low_interference_data, tmp))
    # low_interference_class = np.concatenate((low_interference_class, [1] * len(tmp)))

    ####### NO INTERFERENCE
    # first time slot
    low_interference_data = sanitized_data['B'][startpos1['B']:endpos3['B'], :]
    low_interference_class = [1] * len(low_interference_data)

    # second time slot
    tmp = sanitized_data['E'][startpos1['E']:endpos3['E'], :]
    low_interference_data = np.vstack((low_interference_data, tmp))
    low_interference_class = np.concatenate((low_interference_class, [1] * len(tmp)))

    # third time slot
    tmp = sanitized_data['D'][startpos1['D']:endpos3['D'], :]
    low_interference_data = np.vstack((low_interference_data, tmp))
    low_interference_class = np.concatenate((low_interference_class, [1] * len(tmp)))


    ######### HIDDEN NODES
    # forth time slot
    hidden_nodes_data = sanitized_data['D'][startpos4['D']:endpos4['D'], :]
    hidden_nodes_class = [2] * len(hidden_nodes_data)

    tmp = sanitized_data['B'][startpos4['B']:endpos4['B'], :]
    hidden_nodes_data = np.vstack((hidden_nodes_data, tmp))
    hidden_nodes_class = np.concatenate((hidden_nodes_class, [2] * len(tmp)))

    # fifth time slot
    tmp = sanitized_data['A'][startpos5['A']:endpos5['A'], :]
    hidden_nodes_data = np.vstack((hidden_nodes_data, tmp))
    hidden_nodes_class = np.concatenate((hidden_nodes_class, [2] * len(tmp)))

    tmp = sanitized_data['E'][startpos5['E']:endpos5['E'], :]
    hidden_nodes_data = np.vstack((hidden_nodes_data, tmp))
    hidden_nodes_class = np.concatenate((hidden_nodes_class, [2] * len(tmp)))

    ######## FLOW IN THE MIDDLE
    flow_in_the_middle_data = sanitized_data['B'][startpos6['B']:endpos6['B'], :]
    flow_in_the_middle_class = [3] * len(flow_in_the_middle_data)



    # plt.show()



    ############ old
    # low_interference_data = sanitized_data[2:300, :]
    # low_interference_class = [1] *len(low_interference_data)
    #
    # hidden_nodes_data = sanitized_data[310:610, :]
    # hidden_nodes_class = [2] * len(hidden_nodes_data)
    #
    # flow_in_the_middle_data = sanitized_data[620:890, :]
    # flow_in_the_middle_class = [3] * len(flow_in_the_middle_data)

    ############### measure_long_ok
    # low_interference_data = sanitized_data[70:90, :]
    # low_interference_class = [1] * len(low_interference_data)
    #
    # hidden_nodes_data = sanitized_data[93:116, :]
    # hidden_nodes_class = [2] * len(hidden_nodes_data)
    #
    # flow_in_the_middle_data = sanitized_data[118:178, :]
    # flow_in_the_middle_class = [3] * len(flow_in_the_middle_data)





    X = np.vstack((low_interference_data, hidden_nodes_data))
    X = np.vstack((X, flow_in_the_middle_data))

    y = np.concatenate((np.array(low_interference_class),np.array(hidden_nodes_class)))
    y = np.concatenate((y,flow_in_the_middle_class))

    print (X)
    print (y)
    plt.draw()
    #
    # sys.exit(0)
    #
    # y = [1] * 60

    class_names = ['no-interf', 'hidden nodes', 'flow in the middle']
    # Split data into a training set and a test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

else:
    print("please, choose in the code a valid data_source ")



classifier = BaggingClassifier(KNeighborsClassifier(), max_samples=0.5, max_features=0.5)
trained_classifier = classifier.fit(X_train, y_train)

# trained_classifier = classifier.fit(X_train, y_train)
print ("score obtained %f " %trained_classifier.score(X_train, y_train))

y_pred = trained_classifier.predict(X_test)

# print ("size X_train %s, size y_train %s size X_test %s" % (X_train.shape, y_train.shape, X_test.shape))


# Compute confusion matrix
cnf_matrix = confusion_matrix(y_test, y_pred)
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names, title='Confusion matrix, without normalization')
plt.savefig('confusion-matrix.pdf', format='pdf')
plt.draw()

# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True, title='Normalized confusion matrix')
plt.savefig('normalized-confusion-matrix.pdf', format='pdf')
plt.draw()

# train the classifier with all available training data
trained_classifier = classifier.fit(X[:,1:], y)
# save the trained model to a file for later use
joblib.dump(trained_classifier, 'trained-interference-classifier.pkl')


plt.show()