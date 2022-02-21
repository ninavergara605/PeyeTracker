import sys
import pathlib


class UserInputErrors:

    def __init__(self, user_input):
        self._user_input = user_input
        self.metadata_keys_exist()
        self.available_aspect_ratio()
        self.paths_exist()

    def catch_missing_dependencies(self, dependency_list):
        for option, dependency in dependency_list:
            if self._user_input[option] and (not self._user_input[dependency]):
                raise Exception(f'Please define "{dependency}" for the "{option}" data.')

    def metadata_keys_exist(self):
        path_metadata_pairings = [
            ('asc_directory_path', 'asc_metadata_keys')
            , ('roi_event_map_path', 'roi_event_map_metadata_keys')
        ]
        self.catch_missing_dependencies(path_metadata_pairings)

    def available_aspect_ratio(self):
        if self._user_input['calc_roi_raster_coords']:
            if (not self._user_input['aspect_ratio']) & (not self._user_input['asc_directory_path']):
                raise Exception(
                    'To calculate raster coordinates, please define the "aspect_ratio" or an "asc_directory_path".')

    def paths_exist(self):
        path_keys = [key for key in self._user_input.keys()
                     if ('path' in key) & (isinstance(self._user_input[key], pathlib.PosixPath))
                     ]
        for key in path_keys:
            path = self._user_input[key]
            if (not path.is_file()) & (not path.is_dir()):
                raise Exception(f'The defined path for "{key}" ({path}) does not exist.')


def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    debug_mode = True
    if debug_mode:
        debug_hook(exception_type, exception, traceback)
    else:
        print(f"{exception_type.__name__}: {exception}")


sys.excepthook = exception_handler


def fixations_in_roi(fixations, trial_roi, fix_roi):
    if not (fixations.empty and trial_roi.empty):
        if fix_roi.empty:
            raise Exception("Could not find fixations within any ROI boundaries")
