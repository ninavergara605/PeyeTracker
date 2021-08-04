import re
from pathlib import Path, PureWindowsPath
from collections import namedtuple, defaultdict
import os
import numpy as np


def get_paths_from_directory(directory, metadata_keys_raw=None, valid_metadata_keys=None, target_path_type=None, filename_contains=None):
    target_paths=[]
    if os.path.isdir(directory):
        for root, _, files in os.walk(directory):
            for file in files:
                
                if filename_contains:
                    if filename_contains in file:
                        full_path = os.path.join(root, file)
                        normalized = normalize_path(full_path)
                        target_paths.append(normalized)
                elif target_path_type:
                    if file.endswith(target_path_type):
                        
                        full_path = os.path.join(root, file)
                        normalized = normalize_path(full_path)
                        target_paths.append(normalized)
    else:
        if os.path.isfile(directory):
            if directory.endswith(target_path_type):
                normalized = normalize_path(directory)
                target_paths.append(normalized)
            
    if metadata_keys_raw:
        metadata = extract_metadata(target_paths)
        
        labeled_paths = make_subjects(target_paths, metadata, metadata_keys_raw, valid_metadata_keys)
        filtered = filter_duplicates(labeled_paths)
        return filtered
    return target_paths

def extract_metadata(paths):
    file_metadata = []
    for path in paths:
        name = path.stem.strip()
        split_name_raw = re.split('[\-_]|(\d+)', name)
        split_name = list(filter(None,split_name_raw)) #filters out the empty strings
        file_metadata.append(convert_dtypes(split_name))
    return file_metadata


def make_subjects(paths, file_metadata, metadata_keys_raw, valid_metadata_keys):
    valid_keys = valid_metadata_keys
    path_keys = [*valid_keys[:,1], 'path']
    num_fields_in_filename = len(metadata_keys_raw)
    Subject = namedtuple('Subject', path_keys)
    invalid_metadata = defaultdict(list)
    labeled_paths = []
    
    for path, metadata in zip(paths, file_metadata):
        if (_len := len(metadata) == num_fields_in_filename):
            filtered_data = [metadata[int(i)] for i in valid_keys[:,0]]
            if not isinstance(filtered_data[1], int):
                print('invalid path: ', filtered_data, path)
            else:
                labeled_paths.append(Subject._make([*filtered_data, path]))
        else:
            invalid_metadata[_len].append([metadata, path])
    '''
    if invalid_metadata:
        assigned = manual_assignment(invalid_metadata, Subject)
    '''
    return labeled_paths


def manual_assignment(invalid_metadata, Subject):
    labeled_paths = []
    for _len, data in invalid_metadata.items():
        indexes = input('Too many fields for pairing {} to metadata keys: {}. /n Please specify correct indexes. choices are: {}'.format(data, Subject._fields, list(range(_len))))
        
def convert_dtypes(arr):
    converted = []
    for x in arr:
        if x.isdigit():
            converted.append(int(x))
        else:
            try:
                converted.append(x.lower())
            except AttributeError:
                converted.append(x)
    return converted

def normalize_path(path):
    if path:
        if '\\' in path:
            windows_path = PureWindowsPath(path)
            normalized = Path(windows_path.as_posix())
        else:
            normalized = Path(path)
        return normalized
    else:
        return None

'''
Creates a path from directory and file name inputs.
Any folder that does not exist is made into a directory.
'''

def create_path(directory, file_name, extension='.csv', folder='processed_data', nested_folder = None):        
    if nested_folder:
        folder_path = directory / folder / nested_folder
    else:
        folder_path = directory / folder
    if not folder_path.is_dir():
        folder_path.mkdir(parents=True)
    
    file_path = folder_path / file_name 
    path_with_extension = file_path.with_suffix(extension)
    return path_with_extension

def filter_duplicates(paths):
    metadata = [x[:-1] for x in paths]
    index_container = defaultdict(list)
    for i, key in enumerate(metadata):
        index_container[key].append(i)
    filtered = [paths[indexes[0]] for _, indexes in index_container.items()]
    return filtered
