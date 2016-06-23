import numpy as np
from numpy.lib.recfunctions import stack_arrays
from root_numpy import root2array
import pandas as pd
import glob
import argparse


def root2pandas(files_path, tree_name, **kwargs):
	'''converts files from .root to pandas DataFrame
	Args:
		files_path: a string like './data/*.root', for example
		tree_name: a string like 'Collection_Tree' corresponding to the name of the folder inside the root file that we want to open
		kwargs: arguments taken by root2array, such as branches to consider, start, stop, step, etc
	Returns:
		output_panda: a pandas dataframe like allbkg_df in which all the info from the root file will be stored
	Note:
		if you are working with .root files that contain different branches, you might have to mask your data
		in that case, return pd.DataFrame(ss.data)
	'''
	files = files_path
	ss = stack_arrays([root2array(fpath, tree_name, **kwargs).view(np.recarray) for fpath in files])
	try:
        	return pd.DataFrame(ss)
    	except Exception:
        	return pd.DataFrame(ss.data)


def build_X(events, phrase):
        '''slices related branches into a numpy array
	Args:
		events: a pandas DataFrame containing the complete data by event
		phrase: a string like 'Jet' corresponding to the related branches wanted
	Returns:
		output_array: a numpy array containing data only pertaining to the related branches
	'''
	sliced_events = events[[key for key in events.keys() if key.startswith(phrase)]].as_matrix()
	return sliced_events

def read_in(class_files_dict):
	'''takes paths of root files slices them into ML format
	Args:
		*_path:  a string like './data/*.root', for example
	Returns:
		X_jets: ndarray containing jet related branches
		X_photons: ndarray containing photon related branches
		X_muons: ndarray containing muon related branches
		y: ndarray containing the truth labels
		w: ndarray containing EventWeights
	'''
	
	#convert files to pd data frames, assign key to y, concat all files
	all_events=False	
	for key in class_files_dict.keys():
		df = root2pandas(class_files_dict[key], 'events')
		df['y'] = key
		if all_events is False:
			all_events=df
		else:
			all_events = pd.concat([all_events, df], ignore_index=True)
	
		
	#slice related branches
	X_jets = build_X(all_events, 'Jet')
	print all_events.keys()
	X_photons = build_X(all_events, 'Photon')
	X_muons = build_X(all_events, 'Muon')
	y = all_events['y'].values
	w = all_events['EventWeight'].values
	
	
	return X_jets, X_photons, X_muons, y, w