import pandas as pd
import numpy as np
from ..Roi.raster_conversion import ShiftOrigin

class ImportIposition:

    def __init__(self, user_input, trial_roi, fixations, asc_files):
        self.trial_roi = trial_roi
        self.fixations = fixations
        self.asc_files = asc_files
        self.user_input = user_input
        self.path = user_input['actual_coordinate_path']
        self.labels = user_input['coordinate_labels']
        self.shift_x = user_input['roi_width'] / 2
        self.shift_y = user_input['roi_height'] / 2
        self.ntrials = None
        self.nrois = None
        self.result = self.iPosition_import()

    def iPosition_import(self):
        with open(self.path, 'r') as f:
            raw_coords = f.readlines()
        coords = self.clean_coordinates(raw_coords)
        iposition_df = self.create_iPosition_df(coords)

        iposition_with_metadata = self.add_subject_metadata(iposition_df)
        return iposition_with_metadata

    def add_subject_metadata(self, iposition_df):
        if not self.trial_roi.empty:
            metadata_labels = list(self.user_input['valid_roi_event_map_metadata_keys'][:, 1])
            metadata_df = self.trial_roi[metadata_labels].assign(key=1)
        else:
            fix_metadata = self.fixations.droplevel(['file_position', 'trial_id']).index.drop_duplicates()
            metadata_df = fix_metadata.to_frame().reset_index(drop=True).assign(key=1)

        iposition_with_metadata = metadata_df.merge(iposition_df.assign(key=1), on='key').drop(columns=['key'])
        return iposition_with_metadata

    def create_iPosition_df(self, coords):
        if self.trial_roi.empty:
            roi_ids = np.arange(self.nrois)
        else:
            max_roi_id = self.trial_roi.roi_id.max()
            roi_ids = np.arange(max_roi_id + 1, max_roi_id + self.nrois)

        if not self.labels:
            self.labels = ['roi_' + str(int(idx)) for idx in roi_ids]

        label_dict = dict(zip(roi_ids, self.labels))
        df = self.initialize_iPosition_df(label_dict.values())
        for trial_num, trial_locs in enumerate(coords):
            for roi_num, roi_loc in zip(roi_ids, trial_locs):
                roi_label = label_dict[roi_num]
                df.loc[(trial_num, roi_label), ('x', 'y')] = list(map(float, roi_loc))

        df.index = df.index.set_levels(df.index.levels[0] + 1, level='trial_id')
        df['roi_id'] = df.index.get_level_values('roi_label').map(dict(zip(self.labels, roi_ids)))

        df[['bottom_right_x', 'top_left_x']] = list(zip(df.x + self.shift_x, df.x - self.shift_x))
        df[['bottom_right_y', 'top_left_y']] = list(zip(df.y - self.shift_y, df.y + self.shift_y))

        if time_window := self.user_input['actual_coordinate_time_window']:
            df[['start', 'stop']] = time_window

        if self.user_input['calc_roi_raster_coords']:
            df = ShiftOrigin(df, self.user_input, self.asc_files).result
        return df.reset_index().drop(columns=['x', 'y'])

    def initialize_iPosition_df(self, roi_labels):
        trial_range = np.arange(self.ntrials)
        index = pd.MultiIndex.from_product([trial_range, roi_labels]
                                           , names=['trial_id', 'roi_label'])
        columns = ['x', 'y']
        df = pd.DataFrame(index=index, columns=columns)
        return df

    def clean_coordinates(self, raw_coords):
        coords = [line.strip('\n').split('\t') for line in raw_coords
                  if line != '\n']

        # Specifying reshaping parameters
        dimension = 2
        self.ntrials = len(coords)
        self.nrois = int(len(coords[0]) / dimension)  # Assumes that the coordinates are 2d

        coords_cleaned = np.reshape(coords, (self.ntrials, self.nrois, dimension))
        coords_cleaned.astype(np.float, copy=False)
        return coords_cleaned
