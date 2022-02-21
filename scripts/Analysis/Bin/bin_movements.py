import pandas as pd
from .get_stim_locked_bins import GetStimLockedBins
from .get_time_bin_ranges import GetTimeBinRanges
from scripts.Analysis.Summary.binning_summary import create_bin_summaries
from .bin_by_rt import bin_by_rt


class BinningDispatch:

    def __init__(self, user_input, results):
        self.user_input = user_input
        self.results = results
        self.bin_results = {}
        self.bin_fixations()

    def bin_fixations(self):
        time_bins = GetTimeBinRanges(self.results['roi_event_map']
                                     , self.user_input['time_bin_size']
                                     , self.results['trial_roi']
                                     , self.results['fixation_roi'])

        self.bin_results['stimulus_locked_fixations'] = GetStimLockedBins(self.results['fixation_roi']
                                                                              , time_bins.stim_locked_bins
                                                                              , self.user_input['time_bin_size']).result
        self.bin_results['response_locked_fixations'] = self.get_resp_locked_fixations(time_bins)
        self.create_summaries()

    def create_summaries(self):
        if not self.bin_results['stimulus_locked_fixations'].empty:
            self.bin_results['stim_locked_summary'], self.bin_results['stim_locked_summary_filtered'] = create_bin_summaries(
                                                                                self.bin_results['stimulus_locked_fixations']
                                                                               , filter_out=self.user_input['summary_filter_out']
                                                                               , filter_for=self.user_input['summary_filter_for']
                                                                              , summary_type='stimulus_locked')
        if not self.bin_results['response_locked_fixations'].empty:
            if isinstance(self.bin_results['response_locked_fixations'], pd.Series):
                response_data = self.bin_results['response_locked_fixations']
            else:
                response_data = self.bin_results['response_locked_fixations']['bin_duration']

            self.bin_results['resp_locked_summary_all'], self.bin_results['resp_summary_filtered'] = create_bin_summaries(
                                                                                   response_data
                                                                                   , filter_out=self.user_input['filter_out']
                                                                                   , filter_for=self.user_input['filter_for']
                                                                                   , summary_type='response_locked')

    def get_resp_locked_fixations(self, time_bins):
        rt_col_names, rt_boundaries = time_bins.resp_locked_bins
        resp_binned = []
        if not rt_col_names:
            print('Do not have timing data for Response-Locked Binning')
            return pd.DataFrame()

        for react_time_bounds in rt_boundaries:
            rt_binned = bin_by_rt(react_time_bounds, self.results['fixation_roi'])
            resp_binned.append(rt_binned)

        all_resp_df = pd.concat(resp_binned, keys=rt_col_names)
        all_resp_df.index.rename('react_time_label', level=0, inplace=True)
        return all_resp_df
