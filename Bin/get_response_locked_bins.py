import pandas as pd
import numpy as np


class GetResponseLockedBins:

    def __init__(self, react_time_boundaries, movement_roi):
        self._react_time_bounds = react_time_boundaries
        self._movement_roi =movement_roi
        self.result = self.get_resp_locked_bins()

    def get_resp_locked_bins(self):
        movement_react_time = self.get_movement_react_time()
        before_resp_movements = GetResponseLockedBins.get_movements_in_boundaries(movement_react_time
                                                            ,'before_resp_start'
                                                            ,'reaction_times'
                                                            )
        after_resp_movements = GetResponseLockedBins.get_movements_in_boundaries(movement_react_time
                                                            ,'reaction_times'
                                                            ,'after_resp_stop'
                                                            )
        before_resp_movements['duration'] = GetResponseLockedBins.get_duration_per_bin(before_resp_movements)
        after_resp_movements['duration'] = GetResponseLockedBins.get_duration_per_bin(after_resp_movements)
        
        all_movements = self.get_result_df(before_resp_movements, after_resp_movements)
        return all_movements

    
    def get_result_df(self, before_resp, after_resp):     
        all_resp = pd.concat([before_resp['duration'], after_resp['duration']], keys=['[-250,0]', '[0,250]'])
        all_resp.index.rename('bin', level=0, inplace=True)
        all_resp = GetResponseLockedBins.sum_by_trial_roi(all_resp)
        merge_on = ['subject'
            ,'block_type'
            ,'block_id'
            ,'trial_id'
            ,'roi_id'
            ,'roi_label'
            ,'bin']
        movement_roi = pd.concat([self._movement_roi.drop(index='fix_id').drop_duplicates()], keys=['[-250,0]', '[0,250]'])
        movement_roi.index.rename('bin', level=0, inplace=True)
        res_df = movement_roi.merge(all_resp, left_on = merge_on, right_on = merge_on, how='outer', suffixes=(None, '_bin'))
        
        return res_df
    
    @staticmethod
    def sum_by_trial_roi(df):
        group_by_index = [
                'subject'
                ,'block_type'
                ,'block_id'
                ,'trial_id'
                ,'roi_id'
                ,'roi_label'
                ,'bin'      
                ]
        sum_by_trial_roi = df.groupby(group_by_index).sum() 
        return sum_by_trial_roi

    @staticmethod
    def get_duration_per_bin(df):
        constrained_start = np.where(df['constrained_start'] < df['lower_bound']
                                ,df['lower_bound']
                                ,df['constrained_start']
                                )
        constrained_stop = np.where(df['constrained_stop'] > df['upper_bound']
                                ,df['upper_bound']
                                ,df['constrained_stop']
                                )
        duration = constrained_stop - constrained_start
        return duration

    def get_movement_react_time(self):
        merge_on = ['subject', 'block_type', 'block_id', 'trial_id']
        movement_react_time = self._movement_roi.merge(self._react_time_bounds
                                                ,left_on=merge_on
                                                ,right_index=True
                                                ,how='left'
                                                ).dropna()
        return movement_react_time
   
    @staticmethod
    def get_movements_in_boundaries(df, lower_bound_col, upper_bound_col):
        start_filter = df['constrained_start'] < df[lower_bound_col]
        stop_filter = df['constrained_stop'] > df[lower_bound_col]
        movements_in_bound = df[start_filter & stop_filter]
        movements_in_bound.rename(columns={lower_bound_col:
                                            'lower_bound'
                                        ,upper_bound_col:
                                            'upper_bound'}
                                        ,inplace=True)
        return_columns = ['constrained_start'
                        ,'constrained_stop'
                        ,'lower_bound'
                        ,'upper_bound'
                        ]
        return movements_in_bound[return_columns]
