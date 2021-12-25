import pandas as pd
from collections import defaultdict

def get_missing_asc(metadata):
    trial_group_on = ['subject', 'block_type', 'block_id']
    block_group_on = ['subject', 'block_type']
    ranges = get_ranges(metadata)
    
    missing_blocks = metadata.groupby(block_group_on).apply(get_missing_info, ranges, 'block_id').explode().dropna()
    missing_trials = metadata.groupby(trial_group_on).apply(get_missing_info, ranges, 'trial_id').explode().dropna()
    
    res=pd.DataFrame()
    if not missing_blocks.empty and not missing_trials.empty:
        res = pd.concat([missing_blocks, missing_trials], keys = ['missing_blocks', 'missing_trials'])
    elif not missing_blocks.empty:
        res = pd.concat([missing_blocks], keys=[missing_blocks])
    elif not missing_trials.empty:
        res = pd.concat([missing_trials], keys=['missing_trials'])
    return res

def get_ranges(metadata):
    block_types = metadata['block_type'].unique()
    ranges = defaultdict(dict)
    for _type in block_types:
        type_data = metadata[metadata['block_type'] == _type]
        ranges[_type]['trial_id'] = list(range(1,max(type_data.trial_id)+1))
        ranges[_type]['block_id'] = list(range(1,max(type_data.block_id)+1)) 
    return ranges

def get_missing_info(group, ranges, col):
    block_type = group.name[1]
    type_range = ranges[block_type][col]
    missing = list(set(type_range) - set(group[col].values))
    return missing