import pandas as pd
from .get_stim_locked_bins import GetStimLockedBins
from .get_time_bin_ranges import GetTimeBinRanges
from scripts.Analysis.Summary.binning_summary import create_bin_summaries
from .bin_by_rt import bin_by_rt

    
def bin_fixations(roi, time_bin_size, behavior_test_df, fixation_roi, filter_out, filter_for):
    time_bins = GetTimeBinRanges(behavior_test_df,time_bin_size, roi, fixation_roi)
    
    stimulus_locked_fixations = GetStimLockedBins(fixation_roi
                                                    ,time_bins.stim_locked_bins
                                                    ,time_bin_size).result
    response_locked_fixations = get_resp_locked_fixations(time_bins, fixation_roi)
    
    #stim_summary_all, stim_summary_filtered, resp_summary_all, resp_summary_filtered = create_summaries(stimulus_locked_fixations, response_locked_fixations, filter_out, filter_for) 
    return stimulus_locked_fixations, response_locked_fixations,pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def create_summaries(stim_locked, resp_locked, filter_out, filter_for):
    stim_summary_all, stim_summary_filtered = create_bin_summaries(stim_locked
                                                            ,filter_out = filter_out
                                                        ,filter_for = filter_for
                                            ,summary_type = 'stimulus_locked' )
    
    try: 
        resp_summary_all, resp_summary_filtered = create_bin_summaries(resp_locked['bin_duration']
                                                            ,filter_out= filter_out
                                                            ,filter_for = filter_for
                                                            ,summary_type = 'response_locked')
    except KeyError:
        resp_summary_all, resp_summary_filtered = create_bin_summaries(resp_locked
                                                            ,filter_out= filter_out
                                                            ,filter_for = filter_for
                                                            ,summary_type = 'response_locked')
    return stim_summary_all, stim_summary_filtered, resp_summary_all, resp_summary_filtered

def get_resp_locked_fixations(time_bins, fixation_roi):
    rt_col_names, rt_boundaries = time_bins.resp_locked_bins
    resp_binned = []
    if not rt_col_names:
        print('Do not have timing data for Response-Locked Binning')
        return pd.DataFrame()
    for react_time_bounds in rt_boundaries:
        rt_binned = bin_by_rt(react_time_bounds,fixation_roi)
        resp_binned.append(rt_binned)
    all_resp_df = pd.concat(resp_binned, keys=rt_col_names)
    all_resp_df.index.rename('react_time_label', level=0, inplace=True)
    return all_resp_df
    
