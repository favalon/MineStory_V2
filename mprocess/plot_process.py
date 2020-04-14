import os
import numpy as np
import matplotlib.pyplot as plt
from general.save_load import SaveBasic, LoadBasic


def clusters_plot(char_roles, fp=None):
    for cr in char_roles:
        char_role = {0: "MainCharacter", 1: "Supporter", 2: "Opposites"}[cr]
        clusters = LoadBasic.load_basic(os.path.join('{}_clusters_data'.format(char_role)), path=fp)
        pass


def process(movie_data, p_id=None, fp=None, char_roles=None, down_sample=True, guide=False):
    if p_id and movie_data:
        movie_data[p_id].plot_status(down_sample=down_sample)
        if guide:
            movie_data[p_id].print_status_guide()
    elif char_roles is not None and p_id is None:
        clusters_plot(char_roles, fp=fp)
    else:
        pass