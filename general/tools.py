import os
import glob
import pickle
import urllib.request
import json


def get_data_url(url):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    # data = json.loads(response.read(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    return data


def get_index_positions(listOfElements, element):
    ''' Returns the indexes of all occurrences of give element in
    the list- listOfElements '''
    indexPosList = []
    indexPos = 0
    while True:
        try:
            # Search for item in list from indexPos to the end of list
            indexPos = listOfElements.index(element, indexPos)
            # Add the index position in list
            indexPosList.append(indexPos)
            indexPos += 1
        except ValueError as e:
            break

    return indexPosList


def clear_folders(path):
    files = glob.glob(path)
    for f in files:
        os.remove(f)