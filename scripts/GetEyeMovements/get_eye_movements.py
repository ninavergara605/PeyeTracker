import pandas as pd
import numpy as np
from .get_fixations import GetFixations
from .filter_text import FilterText


def get_eye_movements(asc_files, metadata_keys, trial_sets=None):
    metadata_keys = list(metadata_keys)
    filtered_asc = FilterText(asc_files).result
    raw_movements = format_movement_df(filtered_asc, metadata_keys)

    if trial_sets:
        raw_movements = add_trial_set_labels(raw_movements, trial_sets)
    raw_fixations = raw_movements[raw_movements['type'].isin(['EFIX'])].dropna(axis=1, how='all')
    fixations = GetFixations(raw_fixations, metadata_keys).result
    return filtered_asc, raw_movements, fixations


def add_trial_set_labels(raw_movements, trial_sets):
    for _set in trial_sets:
        column_name = _set[0]
        raw_movements[column_name] = np.nan
        for label, trial_range in zip(_set[2], _set[1]):

            if len(trial_range) == 3:
                in_range_filter = raw_movements.index.get_level_values('trial_id').isin(
                    list(range(trial_range[0], trial_range[1] + 1, trial_range[2])))
            else:
                in_range_filter = raw_movements.index.get_level_values('trial_id').isin(
                    list(range(trial_range[0], trial_range[1] + 1)))

            raw_movements[column_name] = np.where(in_range_filter, label, raw_movements[column_name])
    return raw_movements


def format_movement_df(movements, metadata_keys):
    movements.rename(
        columns={0: 'type'
            , 1: 'eye'
            , 2: 'block_relative_start'
            , 3: 'block_relative_stop'
            , 4: 'eprime_duration'}
        , inplace=True)

    movements.sort_values(by=[*metadata_keys, 'file_position'], inplace=True)
    movements_with_trial = get_trial_info(movements, metadata_keys)
    movements = get_movement_info(movements_with_trial)
    return movements


def get_trial_info(df, metadata_keys):
    df['trial_start'] = df.loc[df['type'] == 'START', 'eye']
    df['trial_start'].ffill(axis=0, inplace=True)

    df['trial_id'] = df[df.type == 'START'].groupby(level=metadata_keys).cumcount() + 1
    df['trial_id'].ffill(axis=0, inplace=True)
    df = df[df.type != 'START'].set_index('trial_id', append=True, drop=True)
    return df


def get_movement_info(text_movements):
    movements = get_numeric_df(text_movements)
    movements['start'] = movements['block_relative_start'] - movements['trial_start']
    movements['stop'] = movements['block_relative_stop'] - movements['trial_start']
    movements['duration'] = movements['stop'] - movements['start']
    movements['type_count'] = movements.groupby('type').cumcount() + 1
    return movements


def get_numeric_df(text_df):
    df = text_df.copy()
    str_to_num_columns = ['trial_start'
        , 'block_relative_start'
        , 'block_relative_stop'
        , 'eprime_duration'
                          ]
    df[str_to_num_columns] = df[str_to_num_columns].apply(pd.to_numeric)
    return df
