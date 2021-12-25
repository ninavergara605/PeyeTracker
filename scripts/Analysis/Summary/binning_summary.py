import pandas as pd
import numpy as np
from collections import defaultdict


def create_bin_summaries(all_data, summary_type=None, filter_out=None, filter_for=None):
    summary_all_roi = pd.DataFrame()
    summary_filtered_roi= pd.DataFrame()
    
    if not all_data.empty:
        group_on = get_groupby(summary_type, all_data)
        summary_all_roi = calculate_prop_viewing(all_data, group_on)
        if isinstance(summary_all_roi, pd.Series):
            summary_all_roi.rename('prop_of_view', inplace = True)
        
        filtered_data = filter_data(all_data, filter_out, filter_for)
        if not filtered_data.empty:
            summary_filtered_roi = calculate_prop_viewing(filtered_data, group_on)
            if isinstance(summary_filtered_roi, pd.Series):
                summary_filtered_roi.rename('prop_of_view', inplace=True)
    return summary_all_roi, summary_filtered_roi

def filter_data(all_data, filter_out, filter_for):
    filters = defaultdict(list)
    for _dict, tag in zip([filter_out, filter_for], ['out', 'for']):
        if _dict:
            for key, filter_value in _dict.items():
                try:
                    values = all_data.index.get_level_values(key)
                    
                except KeyError:
                    values = all_data[key]
                
                if isinstance(filter_value, list):
                        filters[tag].append(values.isin(filter_value))
                elif isinstance(filter_value, str):
                    filters[tag].append(values.str.contains(filter_value))
                else:
                    filters[tag].append(values.isin([filter_value]))
    
    if filters:
        filtered_data = all_data
        for filter_key, arr in filters.items():
            if arr:
                if filter_key == 'out':
                    for rows in arr:
                        filtered_data = filtered_data[~rows]
                else:
                    for rows in arr:
                        filtered_data = filtered_data[rows]
        return filtered_data
    else:
        return pd.DataFrame()

def get_groupby(summary_type, all_data):
    metadata = [name for name in all_data.index.names if name != 'roi_id' and name != 'roi_label']
    if summary_type == 'response_locked':
        group_on = [*metadata,'react_time_label', 'bin']
    else:
        group_on = metadata
    return group_on

def calculate_prop_viewing(data, group_on):
    totals = data.groupby(level=group_on).transform('sum')

    
    prop_of_viewing = data / totals
    return prop_of_viewing


