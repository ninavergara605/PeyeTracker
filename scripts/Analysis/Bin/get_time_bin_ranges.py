import pandas as pd
from collections import defaultdict
import numpy as np
import math


class GetTimeBinRanges:

    def __init__(self, behavior_test_df, frequency, test_roi, fix_roi):
        self._behavior_test_df = behavior_test_df
        self._frequency = frequency
        self._test_roi = test_roi
        self._fix_roi = fix_roi

    @property
    def stim_locked_bins(self):
        if 'start_roi' in self._fix_roi.columns:
            start_col, stop_col = 'start_roi', 'stop_roi'
        elif 'start_fix' in self._fix_roi.columns:
            start_col, stop_col = 'start_fix', 'stop_fix'
        else:
            return
        range_start = 0
        range_stop = math.ceil(self._fix_roi[stop_col].max())
        bins = pd.interval_range(range_start, range_stop, freq=self._frequency)
        return bins

    @property
    def resp_locked_bins(self):
        rt_boundaries = []
        rt_columns = [name for name in self._behavior_test_df.columns if 'RT' in str(name)]

        for name in rt_columns:
            reaction_time_raw = self._behavior_test_df[name]
            reaction_time = pd.to_numeric(
                reaction_time_raw, errors='coerce').dropna()
            before_resp_start = self.get_before_resp_start(reaction_time)

            rt_df = pd.DataFrame(before_resp_start.values, index=before_resp_start.index, columns=['before_resp_start'])
            valid_reaction_times = reaction_time[before_resp_start.index]
            rt_df['reaction_times'] = valid_reaction_times

            rt_df['after_resp_stop'] = self.get_after_resp_stop(
                valid_reaction_times)
            rt_boundaries.append(rt_df)
        return rt_columns, rt_boundaries

    def get_before_resp_start(self, reaction_time):
        before_start = reaction_time - self._frequency
        before_start_filt = before_start[before_start >= 0]
        return before_start_filt

    def get_after_resp_stop(self, reaction_time):
        after_stop = reaction_time + self._frequency
        constrained_after_stop = np.where(after_stop > self._test_roi['stop'].max(), self._test_roi['stop'].max(), after_stop)
        return constrained_after_stop
