from PathUtilities.general_path_functions import create_path
import pandas as pd


def create_result_paths(output_directory_path):
    folder_data_keys = {
                        'intermediate_eye_movements': [
                                                    'fixations'
                                                    ,'filtered_asc'
                                                    ,'eye_movements'
                        ]
                        ,'intermediate_roi': [
                                            'trial_roi'
                                            ,'test_resp_tag'
                                            ,'fixation_roi'
                                            ,'fixation_roi_condensed'
                        ]
                        ,'binning_results': [
                                        'stimulus_locked_fixations'
                                        ,'responsed_locked_fixations'
                                        ,'resp_locked_summary'
                                        ,'stim_locked_summary'
                                        ,'resp_locked_summary_filtered'
                                        ,'stim_locked_summary_filtered'
                        ]
                        ,'entropy_results': [
                                            'transition_entropy'
                        ]
                        
                        ,'excluded_data': [
                                        'missing_asc'
                                        ,'bad_response_trials'
                                        ,'no_roi_fixation_trials'
                        ]
    }
    paths = {}
    for folder, data_tags in folder_data_keys.items():
        for tag in data_tags:
            paths[tag] = create_path(output_directory_path,tag,folder=folder)

    return paths

def pair_result_data(data_dict):
    path_dict = create_result_paths()
    paired = []
    for key, df in data_dict.items:
        if not df.empty:
            paired.append(path_dict[key], df)
    return paired 

def initialize_result_dict():
    keys = [
        'eye_movements'
        ,'roi_event_map'
        ,'behavior_test'
        ,'fixations'
        ,'filtered_asc'
        ,'trial_roi'
        ,'test_resp_tag'
        ,'fixation_roi'
        ,'fixation_roi_condensed'
        ,'stimulus_locked_fixations'
        ,'responsed_locked_fixations'
        ,'resp_locked_summary'
        ,'stim_locked_summary'
        ,'resp_locked_summary_filtered'
        ,'stim_locked_summary_filtered'
        ,'missing_asc'
        ,'bad_response_trials'
        ,'no_roi_fixation_trials'
    ]
    result_dict = {}
    for key in keys:
        result_dict[key] = pd.DataFrame()
        
    return result_dict


