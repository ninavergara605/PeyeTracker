import numpy as np
import pandas as pd


class GetStimLockedBins:

    def __init__(self, movement_roi, bins, frequency):
        self._movement_roi = movement_roi
        self._bins = bins
        self._frequency = frequency
        self._time_columns = self.get_start_stop_cols()
        self.result = self.get_stim_locked_bins()

    def get_stim_locked_bins(self):
        if not self._time_columns:
            print('Do not have timing data for Stimulus-Locked Binning')
            return pd.DataFrame()
        start_bins = self.get_bins(self._time_columns[0])
        stop_bins = self.get_bins(self._time_columns[1])
        start_dur, stop_dur = self.get_durations(start_bins, stop_bins)
        output_df = self.format_durations(start_dur, stop_dur)
        return output_df

    def get_start_stop_cols(self):
        possible_pairs = [['constrained_start', 'constrained_stop'], ['start_fix', 'stop_fix'],
                          ['start_roi', 'stop_roi']]
        for pair in possible_pairs:
            if all(x in self._movement_roi.columns for x in pair):
                return pair
        return None

    def format_durations(self, start_dur, stop_dur):
        merged = pd.concat([start_dur, stop_dur])
        index = merged.index.names.difference(['fix_id'])
        pivot_table = pd.pivot_table(merged.reset_index()
                                     , index=index
                                     , values='duration'
                                     , columns='bin'
                                     , aggfunc='sum'
                                     , fill_value=0)
        return pivot_table

    def get_durations(self, start_bins, stop_bins):
        start_durations = self.get_start_durations(start_bins)
        stop_durations = self.get_stop_durations(stop_bins)
        start_dur, stop_dur = self.get_intra_bin_durations(start_durations, stop_durations)
        return start_dur, stop_dur

    def fill_frequency(self, df):
        fill_filter = (df.ffill(axis=1).notnull() & df.bfill(axis=1).notnull())
        df[fill_filter] = df.fillna(self._frequency)
        return df

    def get_bins(self, name):
        bins = pd.IntervalIndex(pd.cut(self._movement_roi[name], self._bins))
        bin_df = pd.DataFrame(bins, index=self._movement_roi.index, columns=['bin'])
        bin_df[name] = self._movement_roi[name]
        bin_df['lower_bound'] = bins.left
        bin_df['upper_bound'] = bins.right
        bin_df.loc[:, 'bin'] = bins.astype(str)
        return bin_df

    def get_start_durations(self, df):
        start = self._time_columns[0]
        df['duration'] = np.where(df[start] == df['lower_bound']
                                  , df['upper_bound'] - df['lower_bound']
                                  , df['upper_bound'] - df[start])
        return df

    def get_stop_durations(self, df):
        stop = self._time_columns[1]
        df['duration'] = np.where(df[stop] == df['lower_bound']
                                  , df['upper_bound'] - df['lower_bound']
                                  , df[stop] - df['lower_bound'])
        return df

    def get_intra_bin_durations(self, start_df, stop_df):
        # check to see if start and stop have the same bin
        # if so, start duration is stop - start, and stop duration is set to 0
        start_df['duration'] = np.where(start_df['bin'] == stop_df['bin']
                                        , stop_df[self._time_columns[1]] - start_df[self._time_columns[0]]
                                        , start_df['duration'])
        stop_df['duration'] = np.where(start_df['bin'] == stop_df['bin']
                                       , 0
                                       , stop_df['duration'])
        return start_df, stop_df

    @staticmethod
    def fill_durations(column, start_dur, stop_dur):
        _bin = column.name
        matching_start_dur = start_dur[start_dur['bin'] == _bin]
        matching_stop_dur = stop_dur[stop_dur['bin'] == _bin]

        if not matching_start_dur.empty:
            column.loc[matching_start_dur.index] = column.loc[matching_start_dur.index].fillna(
                matching_start_dur['duration'])
        if not matching_stop_dur.empty:
            column.loc[matching_stop_dur.index] = column.loc[matching_stop_dur.index].fillna(
                matching_stop_dur['duration'])
        return column
