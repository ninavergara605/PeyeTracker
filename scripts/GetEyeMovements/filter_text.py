import pandas as pd
import mmap
import pathlib


class FilterText:

    def __init__(self, files, search_for=None):
        if search_for:
            self._search_strs = search_for
        else:
            self._search_strs = ['START', 'EFIX', 'EBLINK', 'SSACC', 'ESACC']
        self._files = files
        self.label_fields = []
        self.result = self.filter_text()

    def filter_text(self):
        search_keys = self.str_to_bytes()
        path_labels = self.get_file_info()
        filtered_text = {}

        for path, label in path_labels:
            with open(path, 'rb', 0) as f:
                m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                for key, key_len in search_keys:
                    search_pos = 0

                    while True:
                        m.seek(search_pos)
                        match_pos = m.find(key)
                        if match_pos == -1:
                            break
                        m.seek(match_pos)
                        filtered_text[(*label, match_pos)] = m.readline().decode("utf-8")
                        search_pos = match_pos + key_len

        filtered_df = self.dict_to_df(filtered_text)
        return filtered_df

    def str_to_bytes(self):
        byte_arrs = [bytearray(_str, encoding='utf-8') for _str in self._search_strs]
        byte_len = [len(arr) for arr in byte_arrs]
        combined = list(zip(byte_arrs, byte_len))
        return combined

    def get_file_info(self):
        if isinstance(self._files, (pathlib.PosixPath, str)):  # one unlabled file to search
            return [[self._files, ['0']]]  # '0' is a dummy file label

        self._label_fields = list(self._files[0]._fields[:-1])
        path_labels = [(f.path, f[:-1]) for f in self._files]  # assumes that path is the last variable in named tuple
        return path_labels

    def dict_to_df(self, filtered_text):
        filtered_df = pd.Series(filtered_text).str.split(expand=True)
        self._label_fields.append('file_position')
        filtered_df.index.set_names(self._label_fields, inplace=True)
        filtered_df.sort_index(axis=0, inplace=True)
        return filtered_df
