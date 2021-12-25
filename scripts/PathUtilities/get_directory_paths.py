import re
from collections import namedtuple, defaultdict
import os
from .general_path_functions import normalize_path


class GetPathsFromDirectory:

    def __init__(self
                 , path
                 , metadata_keys_raw=None
                 , valid_metadata_keys=None
                 , target_path_type=None
                 , filename_contains=None
                 ):
        self._path = path
        self._metadata_keys_raw = metadata_keys_raw
        self._valid_metadata_keys = valid_metadata_keys
        self._target_path_type = target_path_type
        self._filename_contains = filename_contains
        self.result = self.dispatch()

    def dispatch(self):
        target_paths = []
        if os.path.isdir(self._path):
            directory_files = [os.path.join(root, file)
                               for root, _, files in os.walk(self._path)
                               for file in files
                               ]
            target_paths = self.filter_files(directory_files)
        else:
            target_paths.append(self._path)
        if not target_paths:
            raise Exception(f"Could not find paths with {self._target_path_type}")

        normalized_paths = list(map(normalize_path, target_paths))
        try:
            labeled_paths = LabelPaths(normalized_paths
                                       , self._metadata_keys_raw
                                       , self._valid_metadata_keys
                                       ).result
            return labeled_paths
        except Exception:
            return normalized_paths

    def filter_files(self, file_paths):
        target_paths = []
        for file in file_paths:
            if self._filename_contains:
                if self._filename_contains in file:
                    target_paths.append(file)
            elif self._target_path_type:
                if file.endswith(self._target_path_type):
                    target_paths.append(file)
            else:
                target_paths.append(file)
        return target_paths


class LabelPaths:

    def __init__(self
                 , paths
                 , metadata_keys_raw=None
                 , valid_metadata_keys=None
                 ):
        self._paths = paths
        self._metadata_keys_raw = metadata_keys_raw
        self._valid_metadata_keys = valid_metadata_keys
        self.result = self.dispatch()

    def dispatch(self):
        valid_metadata, invalid_metadata = self.extract_metadata()
        if not valid_metadata:
            raise Exception("Filenames do not contain metadata")
        if invalid_metadata:
            print(f"Cannot match filename contents of {invalid_metadata} to the metadata keys {self._metadata_keys_raw}")

        labeled_paths = self.make_subjects(valid_metadata)
        filtered = LabelPaths.filter_metadata_duplicates(labeled_paths)
        return filtered

    def extract_metadata(self):
        num_fields_in_filename = len(self._metadata_keys_raw)
        valid_metadata = []
        invalid_metadata = []
        for path in self._paths:
            name = path.stem.strip()
            split_name_raw = re.split(r'[\-_]|(\d+)', name)
            split_name = list(filter(None, split_name_raw))  # filters out the empty strings

            if _len := len(split_name) == num_fields_in_filename:
                valid_metadata.append((LabelPaths.convert_dtypes(split_name), path))
            else:
                invalid_metadata.append((split_name, path))
        return valid_metadata, invalid_metadata

    @staticmethod
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

    def make_subjects(self, file_metadata):
        path_keys = [*self._valid_metadata_keys[:, 1], 'path']
        Subject = namedtuple('Subject', path_keys)
        labeled_paths = []

        for metadata, path in file_metadata:
            filtered_data = [metadata[int(i)] for i in self._valid_metadata_keys[:, 0]]
            labeled_paths.append(Subject._make([*filtered_data, path]))
        return labeled_paths

    @staticmethod
    def filter_metadata_duplicates(paths):
        metadata = [x[:-1] for x in paths]
        index_container = defaultdict(list)
        for i, key in enumerate(metadata):
            index_container[key].append(i)
        filtered = [paths[indexes[0]] for _, indexes in index_container.items()]
        return filtered
