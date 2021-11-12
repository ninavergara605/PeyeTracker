import pandas as pd
import numpy as np


def bin_by_rt(react_time_boundaries, movement_roi):
    rt_df = get_rt_df(movement_roi, react_time_boundaries)
    filtered = rt_df.groupby(level='bin').apply(filter_by_time)
    with_duration = get_duration_per_bin(filtered)
    summed = sum_by_trial_roi(with_duration)
    return summed

def get_rt_df(movement_roi, trial_rt):
    merge_on = ['subject', 'block_type', 'block_id', 'trial_id']
    fix_rt = movement_roi.merge(trial_rt
                            ,left_on=merge_on
                            ,right_index=True
                            ,how='left'
                            )
    with_bins = add_bins(fix_rt)
    return with_bins

def filter_by_time(df):
    _bin = df.name
    if _bin == '[-250, 0]':
        lower_bound = 'before_resp_start'
        upper_bound = 'reaction_times'
    else:
        lower_bound = 'reaction_times'
        upper_bound = 'after_resp_stop'

    start_filter = df['constrained_start'] < df[lower_bound]
    stop_filter = df['constrained_stop'] > df[lower_bound]
    df.loc[~(start_filter & stop_filter), ['constrained_start', 'constrained_stop']] = np.nan
    
    df.rename(columns={lower_bound:
                            'lower_bound'
                        ,upper_bound:
                            'upper_bound'}
                        ,inplace=True)
    return_columns = ['constrained_start'
                    ,'constrained_stop'
                    ,'lower_bound'
                    ,'upper_bound'
                    ]
    return df[return_columns]



def export(df, file_name):
    base_path = r'/Users/ninavergara/Desktop/3fnd_bin_revised_3/'
    export_path = ''.join([base_path, file_name, '.csv'])
    df.to_csv(export_path)

def get_duration_per_bin(df):
    constrained_start = np.where(df['constrained_start'] < df['lower_bound']
                            ,df['lower_bound']
                            ,df['constrained_start']
                            )
    constrained_stop = np.where(df['constrained_stop'] > df['upper_bound']
                            ,df['upper_bound']
                            ,df['constrained_stop']
                            )
    df['bin_duration'] = constrained_stop - constrained_start
    return df

def add_bins(fix_rt):
    before_resp = fix_rt.copy()
    after_resp = fix_rt.copy()
    
    before_resp['bin'] = np.repeat('[-250, 0]', len(fix_rt))
    after_resp['bin'] = np.repeat('[0, 250]', len(fix_rt))

    before_resp.set_index('bin', append=True, inplace=True)
    after_resp.set_index('bin', append=True, inplace=True)

    bin_df = pd.concat([before_resp, after_resp])
    return bin_df


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
    sum_by_trial_roi = df['bin_duration'].groupby(group_by_index).sum() 
    return sum_by_trial_roi


   
