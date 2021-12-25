import pandas as pd
import numpy as np
import pathlib


class ImportEventMaps:

    def __init__(self, paths, user_input):
        self._paths = paths
        self._column_names = user_input['roi_event_map_columns']
        self._add_trial_id = user_input['add_roi_event_map_trial_id']
        self._skip_rows = user_input['roi_event_map_import_skip_rows']
        self._trial_sets = user_input['roi_event_map_trial_sets']
        self._target_path_extension = user_input['roi_event_map_extension']
        self._trial_column = user_input['roi_event_map_trial_column']
        self._metadata_keys = user_input['valid_roi_event_map_metadata_keys']

        if self._column_names:
            self._header = None
        else:
            self._header = 0
        self.result = self.import_roi_event_map()

    def import_roi_event_map(self):
        events = self.create_df()
        if self._add_trial_id:
            events['trial_id'] = events.groupby(level=events.index.names[:-1]).cumcount() + 1
        events.set_index([self._trial_column], append=True, inplace=True, drop=True)

        if self._trial_sets:
            self.add_trial_set_labels(events)
        return events

    def create_df(self):
        read_csv_kwargs = {'header': self._header, 'names': self._column_names}
        if self._skip_rows:
            read_csv_kwargs['skiprows'] = self._skip_rows

        if 'csv' in self._target_path_extension:
            reading_func = pd.read_csv
        else:
            reading_func = pd.read_excel

        if isinstance(self._paths[0], pathlib.PurePath):
            # Metadata could not be found in filename so they must be columns in each file
            dfs = list(map(reading_func, self._paths))
            events_raw = pd.concat(dfs)
            events = ImportEventMaps.clean_df(events_raw)

            # Checks to see if all metadata columns are present, if not then raise exception
            missing_metadata_cols = list(set(self._metadata_keys) - set(events.columns.values))
            if missing_metadata_cols:
                raise Exception(f"Could not find the metadata column(s): {missing_metadata_cols} in roi event maps")
            events.set_index(self._metadata_keys, inplace=True, drop=True)
        else:
            # Metadata was pulled from filenames and should be used for data concatenation
            dfs = np.array([[subject[:-1], reading_func(subject.path, **read_csv_kwargs)]
                            for subject in self._paths]
                           , dtype=object)
            metadata_labels = self._paths[0]._fields[:-1]
            events_raw = pd.concat(dfs[:, 1], keys=dfs[:, 0], names=[*metadata_labels, 'index'])
            events = ImportEventMaps.clean_df(events_raw)
        return events

    @staticmethod
    def clean_df(df):
        # convert all strings to lowercase and convert numeric dtypes
        df = df.apply(lambda x: x.str.lower() if (x.dtype == 'object') else x).apply(pd.to_numeric, errors='ignore')
        # drops unnamed columns
        df = df.loc[:, ~df.columns.str.contains("^(Unnamed|level)")]

        # Checks if there's duplicated metadata in index
        is_duplicated = df.index.duplicated(keep='last')
        if any(is_duplicated):
            # if duplicated data, return dataframe with last occurrence of values
            print(f"Found duplicated metadata in event map files: {df[is_duplicated]}. Continuing with values from "
                  "last occurrence")
            return df[~is_duplicated]
        return df

    def add_trial_set_labels(self, events):
        for _set in self._trial_sets:
            column_name = _set[0]
            events[column_name] = np.nan

            for label, trial_range in zip(_set[2], _set[1]):
                if len(trial_range) == 3:
                    in_range_filter = events.index.get_level_values(self._trial_column).isin(
                        list(range(trial_range[0], trial_range[1] + 1, trial_range[2])))
                else:
                    in_range_filter = events.index.get_level_values(self._trial_column).isin(
                        list(range(trial_range[0], trial_range[1] + 1)))
                events[column_name] = np.where(in_range_filter, label, events[column_name])
        return events
