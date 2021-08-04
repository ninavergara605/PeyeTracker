import pandas as pd
import numpy as np
import re

class GetFixationRoi:


    def __init__(self
                ,fixations = None
                ,fixation_metadata_keys = None
                ,roi = None
                ,roi_metadata_keys = None
                ,test_trial_col = None
                ):
        self._fixations = fixations
        self._fixation_metadata_keys = fixation_metadata_keys
        self._roi = roi
        self._roi_metadata_keys = roi_metadata_keys
        self._test_trial_col = test_trial_col
        self.format_dfs()
        self.result = self.get_fixation_roi()

    
    def format_dfs(self):
        filter_out = ['block_relative_start', 'block_relative_stop', 'eprime_duration','avg_pupil_size', 'trial_start', 'type', 'eye', 'type_count']
        fixations = self._fixations[self._fixations.columns.difference(filter_out)]
        self._fixations, self._roi = self.tag_columns(fixations, self._roi)

    def get_fixation_roi(self):
        fix_roi = self.add_roi()
        valid_pairs = self.find_valid_pairings(fix_roi)
        fix_roi[~fix_roi.index.isin(valid_pairs.index)] = np.nan
        
        if not any(True for col in ['start_roi', 'stop_roi'] if col not in fix_roi.columns):
            fix_roi = self.get_constrained_time(fix_roi)
        return fix_roi, valid_pairs


    def find_valid_pairings(self,fix_roi):
        coord_filter = '(top_left_y <= y_fix) & (bottom_right_y >= y_fix) & (top_left_x <= x_fix) & (bottom_right_x >= x_fix)'
        time_filter = '(start_fix < stop_roi) & (stop_fix > start_roi)'
        
        filtered_df = fix_roi.copy()
        for _filt in [coord_filter, time_filter]:
            
            required_cols = list(filter(None, re.split('[^A-Za-z_]+', _filt)))
            missing_req = [col for col in required_cols if col not in fix_roi.columns]
            if missing_req:
                print(f"{missing_req} columns are not present in roi template, trying to pair fixations on other criteria")
            else:
                filtered_df = filtered_df.query(_filt) 

        return filtered_df

    def add_roi(self):
        fix_merge_keys, roi_merge_keys = self.create_merge_keys()
        fix_with_roi =self._fixations.merge(self._roi
                                            ,left_on=fix_merge_keys
                                            ,right_on= roi_merge_keys
                                            ,how='outer'
                                            ).reset_index()
        
        index_keys = self.get_index_keys()
        fix_roi = fix_with_roi.apply(pd.to_numeric, errors='ignore').set_index([*index_keys,'roi_id','roi_label', 'fix_id'])
        #fix_with_roi = drop_columns(fix_with_roi, fix_merge_keys)
        return fix_roi

    def drop_columns(fix_with_roi, fix_merge_keys):
        _drop_columns = ['level_0', 'index']
        drop_these = [col for col in fix_with_roi if any(col == drop_col for drop_col in _drop_columns)]
        if 'trial_id' in fix_with_roi.columns:
            #assume that the user defined trial column has already been added to the index and drop the duplicate fixation column
            drop_these.append('trial_id')
        if drop_these:
            return fix_with_roi.drop(columns=drop_these)
        return fix_with_roi
        
    def get_index_keys(self):
        common_keys = list(np.unique([*self._roi_metadata_keys,*self._fixation_metadata_keys]))
        
        if self._test_trial_col:
            common_keys.append(self._test_trial_col)
        elif 'trial_id' in self._roi.columns:
            common_keys.append('trial_id')
        
        return  common_keys

    def tag_columns(self, fixations, roi):
        renamed = []
        cols_to_tag = ['start', 'stop', 'x', 'y']
        for df, suffix in zip([fixations, roi], ['_fix', '_roi']):
            new_names = {name:''.join([name, suffix]) for name in cols_to_tag if any(col == name for col in df.columns)}
            if new_names:
                renamed.append(df.rename(columns=new_names))
            else:
                renamed.append(df)
        return renamed

    def create_merge_keys(self):
        common_cols = self._roi.columns[self._roi.columns.isin(self._fixations.columns)]
        
        if self._test_trial_col:
            fix_merge_keys = [*common_cols, 'trial_id']
            roi_merge_keys = [*common_cols, self._test_trial_col]
        else:
            fix_merge_keys =  roi_merge_keys = common_cols
        return fix_merge_keys, roi_merge_keys

    def get_constrained_time(self, df):
        df['constrained_start'] = np.where(df['start_fix'] >= df['start_roi']
                            ,df['start_fix']
                            ,df['start_roi'])
        
        df['constrained_stop'] = np.where(df['stop_fix'] >= df['stop_roi']
                            ,df['stop_roi']
                            ,df['stop_fix'])
        return df

