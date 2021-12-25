from .filter_text import FilterText
import pandas as pd


def extract_calibration_data(all_subjects):
    validation_data_raw = FilterText(all_subjects, search_for=['VALIDATE', 'CAL VALIDATION']).result
    group_by = [name for name in validation_data_raw.index.names if name != 'file_position']
    validation_summary = validation_data_raw.groupby(group_by).apply(retrieve_data)
    return validation_summary

def retrieve_data(group):
    last_val_idx = group[group[0] == 'CAL'].index.get_level_values('file_position').max()
    last_val_offset = group.loc[group.index.get_level_values('file_position') > last_val_idx, 8].apply(pd.to_numeric)

    num_points = last_val_offset.count()
    offset_max = last_val_offset.max()
    any_above_1 = last_val_offset[last_val_offset > 1].any()
    labels = ['num_calibration_points', 'max_offset', 'large_offset_flag']
    return pd.Series([num_points, offset_max, any_above_1], index=labels)
