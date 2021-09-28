import pandas as pd
from ResultContainers import initialize_result_dict
from GetEyeMovements.get_eye_movements import get_eye_movements
from Roi.get_fix_roi import GetFixationRoi
from Roi.get_test_roi import get_test_roi
from Bin.bin_movements import bin_fixations
from UserInput.user_input import validate_user_input
from PathUtilities.get_directory_paths import GetPathsFromDirectory
from Import.test_import import import_behavior_test
from Export.export import export
from Roi.cartesian_to_raster import raster_conversion
from Import.roi_template_import import roi_template_import
from Import.import_roi_event_map import ImportEventMaps
from Entropy.calculate_entropy import CalculateEntropy


def main(user_input): 
    results = initialize_result_dict()

    if (events_path := user_input['roi_event_map_path']):
        event_files = GetPathsFromDirectory(events_path
                                            ,metadata_keys_raw=user_input['roi_event_map_metadata_keys']
                                            ,valid_metadata_keys=user_input['valid_roi_event_map_metadata_keys']
                                            ,filename_contains=user_input['roi_event_map_filename_contains']
                                            ,target_path_type='.csv'
                                            ).result

        results['roi_event_map'] = ImportEventMaps(event_files
                                ,column_names = user_input['roi_event_map_columns']
                                ,add_trial_id = user_input['add_roi_event_map_trial_id']
                                ,skip_rows = user_input['roi_event_map_import_skip_rows']
                                ,trial_column = user_input['roi_event_map_trial_column']
                                ).result
        print('done: ', 'roi_event_map')
  
    if (test_path := user_input['behavior_test_path']):
        if (user_test_import := user_input['test_import_module']):
            results['behavior_test'] = user_test_import(test_path).result
        else:
            results['behavior_test'], duplicated_subjects = import_behavior_test(test_path, user_input['behavior_metadata_keys'])
    
    if (test_tag := user_input['test_tag_module']):
            results['test_resp_tags'] = test_tag(results['behavior_test']).result
        

    if (asc_dir := str(user_input['asc_directory_path'])):
        asc_files = GetPathsFromDirectory(asc_dir
                                        ,metadata_keys_raw=user_input['asc_metadata_keys']
                                        ,valid_metadata_keys=user_input['valid_asc_metadata_keys']
                                        ,target_path_type='.asc'
                                        ).result
        if asc_files:
            results['filtered_asc'], results['eye_movements'], results['fixations'] = get_eye_movements(asc_files
                                                                                            ,user_input['valid_asc_metadata_keys'][:,1]
                                                                                            ,trial_sets = user_input['asc_trial_sets']
                                                                                            )
            print('done: ', 'fixations')

    if (template_path := user_input['roi_template_path']):
        roi_template_raw = roi_template_import(template_path)
        
        if user_input['calc_roi_raster_coords']:
            roi_template = raster_conversion(roi_template_raw
                                        ,aspect_ratio=user_input["aspect_ratio"]
                                        ,metadata_keys=user_input['valid_asc_metadata_keys']
                                        ,asc_files=asc_files
                                   )
    
        else:
            roi_template = roi_template_raw
        print('done: ', 'roi_template')
    
    if not results['roi_event_map'].empty:
        behavior_data = results['roi_event_map']
        behav_metadata_keys = user_input['valid_roi_event_map_metadata_keys'][:,1]
        trial_col = user_input['roi_event_map_trial_column']
    else:
        behavior_data = results['behavior_test']
        behav_metadata_keys =user_input['valid_behavior_test_metadata_keys']
        trial_col = user_input['behavior_test_trial_column']

    if not roi_template.empty:
        if not behavior_data.empty:
            results['trial_roi'] = get_test_roi(behavior_data, roi_template)
            print('done: ', 'test_roi')

    if not results['fixations'].empty and not results['trial_roi'].empty:
        results['fixation_roi'], results['fixation_roi_condensed'] = GetFixationRoi(fixations=results['fixations']
                                                            ,roi=results['trial_roi']
                                                            ,fixation_metadata_keys=user_input['valid_asc_metadata_keys'][:,1]
                                                            ,roi_metadata_keys=behav_metadata_keys
                                                            ,test_trial_col=trial_col).result
        print('done: ', 'fixation_roi_all')
    if not results['fixation_roi'].empty:
        results['stimulus_locked_fixations'], results['response_locked_fixations'], results['stim_locked_summary'], results['stim_locked_summary_filtered'], results['resp_locked_summary'], results['resp_locked_summary_filtered']  = bin_fixations(results['trial_roi']
                                                                                        ,user_input['time_bin_size']
                                                                                        ,behavior_data
                                                                                        ,results['fixation_roi']
                                                                                        ,user_input['summary_filter_out']
                                                                                        ,user_input['summary_filter_for'])
        print('done: ', 'stimulus_locked_fixations')
    #bad_resp_trials, missing_roi_fixations, missing_asc_data = get_missing_data(fixations, test_resp_tags, fixation_roi_all)                                                                                
    if user_input['calculate_entropy']:
        if not results['fixation_roi'].empty:
            results['transition_entropy'] = CalculateEntropy(results['fixation_roi'], target_roi=user_input['target_roi_entropy'],exclude_diagonals=user_input['exclude_diagonals']).result
        else:
            print('Do not have the required ASC or ROI Inputs to calculate entropy. Please check that ASC paths and ROI template information is valid.')
    export(results, user_input,)
if __name__ == "__main__":
    user_input = validate_user_input({
                                # Export Options
                                 'output_directory_path': None
                                 ,'output_folder_name': None

                                # Eye Movement Options
                                ,'asc_directory_path': 'test_data/asc_files'
                                ,'attach_movement_cols': ['type']
                                ,'asc_metadata_keys': ['subject_id', 'block_id']
                                ,'asc_trial_sets': None
                                
                                #Behavior Test Options
                                ,'behavior_test_path': None
                                ,'behavior_test_trial_col': None
                                ,'behavior_metadata_keys': None
                                ,'attach_behavior_cols': None
                                
                                # Roi Template Options
                                ,'roi_template_path': 'test_data/roi_templates/roi_template_version_1.xlsx'
                                ,'calc_roi_raster_coords': False
                                ,'aspect_ratio': None 
                                
                                # Roi Event Map Options
                                ,'roi_event_map_path' : 'test_data/roi_event_maps'
                                ,'roi_event_map_metadata_keys' : ['subject_id', 'block_id']
                                ,'roi_event_map_trial_column': 'trial_id'   
                                ,'attach_event_cols': ['phase']             
                                ,'roi_event_map_filename_contains' : None   
                                ,'roi_event_map_import_skip_rows': None     
                                ,'roi_event_map_columns' : None             
                                ,'add_roi_event_map_trial_id': False        
                                
                                # Binning Options
                                ,'time_bin_size':250 
                                ,'summary_filter_out': None
                                ,'summary_filter_for': None

                                # Entropy Options
                                ,'calculate_entropy': True
                                ,'target_roi_entropy': None #['target', 'lure']
                                ,'exclude_diagonals': False
                                })
    main(user_input)

