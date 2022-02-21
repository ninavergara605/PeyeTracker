from scripts.PathUtilities import normalize_path
import sys
import inspect
import pkgutil
import numpy as np
from scripts.catch_errors import UserInputErrors
from functools import reduce
from .lower_strings import lower_strings_dispatch
from ..PathUtilities.general_path_functions import create_output_directory


def validate_user_input(user_input):
    funcs = [add_user_scripts
        , normalize_user_paths
        , create_output_directory
        , lower_strings_dispatch
        , get_valid_metadata_keys
        , check_event_map_trial_id]

    validated = reduce(lambda res, f: f(res), funcs, user_input)
    UserInputErrors(validated)
    return validated


def check_event_map_trial_id(user_input):
    if user_input['roi_event_map_path'] and not user_input['roi_event_map_trial_column']:
        user_input['roi_event_map_trial_column'] = 'trial_id'
        user_input['add_roi_event_map_trial_id'] = True
        print('Event map trial column will be created since roi_event_map_trial_column is blank')
    return user_input


def get_valid_metadata_keys(user_input):
    metadata_keys = [key for key in user_input.keys()
                     if ('metadata_key' in key) & (user_input[key] is not None)]
    for key in metadata_keys:
        valid_key = ''.join(['valid_', key])
        user_input[valid_key] = filter_metadata_keys(user_input[key])
    return user_input


def filter_metadata_keys(raw_keys):
    if raw_keys:
        metadata_keys = np.array(list(enumerate(raw_keys)))
        valid_keys = metadata_keys[metadata_keys[:, 1] != 'drop']
        return valid_keys
    else:
        return []


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
    test_tag_path = './EyeTrackApp/UserScripts/TestResponseTag/'
    test_import_path = './EyeTrackApp/UserScripts/BehaviorTestImport/'
    for script_path, tag in zip([test_import_path, test_tag_path], ['test_import_module', 'test_tag_module']):
        user_input[tag] = load_user_module(script_path)
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
