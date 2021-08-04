from Import.get_paths import normalize_path
import sys
import inspect
import pkgutil
import numpy as np

def validate_user_input(user_input):
    user_input = add_user_scripts(user_input)
    user_input = normalize_user_paths(user_input)
    user_input = strings_to_lower(user_input)
    user_input = get_valid_metadata_keys(user_input)
    return user_input

def get_valid_metadata_keys(user_input):
    user_input_keys = [key for key in user_input.keys() if 'metadata_key' in key]
    for key in user_input_keys:
        valid_key = valid_key = ''.join(['valid_', key])
        user_input[valid_key] = filter_metadata_keys(user_input[key])
    return user_input

def filter_metadata_keys(raw_keys):
    metadata_keys = np.array(list(enumerate(raw_keys)))
    valid_keys = metadata_keys[metadata_keys[:,1] != 'drop']
    return valid_keys


def strings_to_lower(user_input):
    for key, value in user_input.items():
        if isinstance(value, str):
            lowered_value = value.lower()
        elif isinstance(value, dict):
            lowered_value = lower_strings_dict(value)
        elif isinstance(value, tuple):
            lowered_value = lower_strings_tuple(value)
            print(lowered_value)
        elif isinstance(value, list):
            lowered_value = lower_strings_list(value)
        else:
            lowered_value = []
        
        if lowered_value:
            user_input[key] = lowered_value
    return user_input


def lower_strings_dict(_dict):
    lowered_dict = {}
    for key, value in _dict.items():
        lowered_key = key.lower()
        if isinstance(value, str):
            lowered_dict[lowered_key] = value.lower()
        elif isinstance(value, list):
            lowered_key = lower_strings_list(value)
        else:
            lowered_dict[lowered_key] = value
    return lowered_dict

def lower_strings_tuple(_tuple):
    lowered = []
    for value in _tuple:
        if isinstance(value, tuple):
            lowered_value = tuple([x.lower() if isinstance(x, str) else x for x in value])
        else:
            try:
                lowered_value = value.lower()
            except:
                lowered_value = value
        lowered.append(lowered_value)
    return tuple(lowered)

def lower_strings_list(_list):
    if isinstance(_list[0], tuple):
        lowered_list = [lower_strings_tuple(x) for x in _list]
    else:
        lowered_list = [x.lower() if isinstance(x, str) else x for x in _list]
    return lowered_list

def normalize_user_paths(user_input):
    '''
    Grab keys in user input that contain 'path' and normalize their string values with pathlib.
    Update user_input with normalized values.
    
    Returns user_input dictionary
    '''
    path_keys = [key for key, value in user_input.items()
                 if value and 'path' in key]
    for path_key in path_keys:
        user_input[path_key] = normalize_path(user_input[path_key])
    return user_input

def add_user_scripts(user_input):
    '''
    check folders for user defined test response tag and behavior test importing scripts. If present load module and add it to user input.
    Return Updated user_input dictionary
    '''
    test_tag_path= './EyeTrackApp/UserScripts/TestResponseTag/'
    test_import_path= './EyeTrackApp/UserScripts/BehaviorTestImport/' 
    for script_path, tag in zip([test_import_path, test_tag_path], ['test_import_module','test_tag_module']):
        user_input[tag]=load_user_module(script_path)
    return user_input

def load_user_module(script_path):
    for importer, package_name, _ in pkgutil.iter_modules([script_path]):
        if package_name not in sys.modules:
            
            user_module = importer.find_module(package_name).load_module(package_name)
            for __, obj in inspect.getmembers(user_module):
                if inspect.isclass(obj) or inspect.isfunction(obj):
                    source_file = inspect.getsourcefile(obj)
                    
                    if package_name in source_file:
                        try:
                            top_level_class = obj.mro()[0]
                            return top_level_class
                        except AttributeError:
                            return obj
    return
