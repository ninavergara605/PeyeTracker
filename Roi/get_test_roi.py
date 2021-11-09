import pandas as pd
import numpy as np
from Export.clean_output import clean_output

@clean_output
def get_test_roi(test_behavior, roi_template):
    static_test_roi = pair_static_roi(test_behavior,roi_template)
    dynamic_test_roi = pair_dynamic_roi(test_behavior, roi_template)
    all_test_roi = pd.concat([dynamic_test_roi, static_test_roi])
    return all_test_roi

def pair_dynamic_roi(test_behavior, roi_template):
    event_options = roi_template['dynamic_event_options'].dropna().apply(pd.to_numeric, errors='coerce')
    roi_labels = roi_template['dynamic_roi_label'].dropna()
    
    verified_columns = verify_event_columns(test_behavior, roi_labels)
    test_behavior[verified_columns] = test_behavior[verified_columns].apply(pd.to_numeric, errors='coerce')
    paired_events = [test_behavior[name].reset_index().merge(event_options, left_on=name, right_on='key').drop([name,'key'], axis=1) for name in verified_columns]
    
    events_df = pd.concat(paired_events, keys=verified_columns, names = ['dynamic_event_column'])   
    events_with_labels = events_df.merge(roi_labels, on='dynamic_event_column').drop('dynamic_event_column', axis=1)
    return events_with_labels

def verify_event_columns(test_behavior, roi_labels):
    test_event_columns = roi_labels['dynamic_event_column']
    missing_cols = test_event_columns[~test_event_columns.isin(test_behavior.columns)]

    if not missing_cols.empty:
        print('Could not find {} dynamic event column(s) in roi event map or behavior test'.format(missing_cols))
        return test_event_columns[~test_event_columns.isin(missing_cols)].values 
    return test_event_columns.values

def pair_static_roi(test_behavior,roi_template):
    static_df = pd.DataFrame(index=test_behavior.index).assign(key=1)
    static_roi = roi_template['static'].dropna()
    test_roi_static = static_df.reset_index().merge(static_roi.assign(key=1), on='key', how='left').drop('key', axis=1)
    return test_roi_static

