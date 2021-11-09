import pandas as pd
from .get_missing_asc import get_missing_asc


def get_missing_data(fixations, test_tag, movement_roi):
    bad_resp_trials = pd.DataFrame()
    missing_roi_fixations = pd.DataFrame()
    missing_asc_data = pd.DataFrame()
    
    if not fixations.empty:
        fixation_metadata = extract_metadata(fixations)
        missing_asc_data = get_missing_asc(fixation_metadata)
        if not movement_roi.empty:
            movement_roi_metadata = extract_metadata(movement_roi)
            missing_roi_fixations = get_no_roi_fixations(movement_roi_metadata, fixation_metadata)
    if not test_tag.empty:
        bad_resp_trials = get_bad_resp_trials(test_tag)
    
    return bad_resp_trials, missing_roi_fixations, missing_asc_data


def get_no_roi_fixations(movement_roi, fixations):
    to_compare = ['subject', 'block_type', 'block_id', 'trial_id']
    df = fixations[to_compare].merge(movement_roi[to_compare], how='left', indicator=True)
    return df[(df['_merge'] == 'left_only') &(df['block_type'] == 'R')].drop(['_merge'], axis=1).drop_duplicates()

def get_bad_resp_trials(test_tag):
    bad_resp_trials = test_tag[test_tag.str.contains('bad') | test_tag.str.contains('Bad')]   
    return bad_resp_trials

def extract_metadata(df):
    df.reset_index(inplace=True)
    metadata = df[['subject', 'block_type', 'block_id', 'trial_id']].copy()
    
    numeric_metadata = metadata.apply(pd.to_numeric,errors='ignore', downcast='integer')
    return numeric_metadata