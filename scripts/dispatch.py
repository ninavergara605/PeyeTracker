import pandas as pd
from scripts.ResultContainers import initialize_result_dict
from scripts.GetEyeMovements import get_eye_movements
from scripts.Roi.get_fix_roi import GetFixationRoi
from scripts.Roi import get_test_roi
from scripts.Analysis.Bin import bin_fixations
from scripts.PathUtilities import GetPathsFromDirectory
from scripts.Export import export
from scripts.Import import ImportEventMaps
from scripts.Analysis.Entropy import CalculateEntropy
#from scripts.Plot.plot_fixations import PlotFixations
from scripts.GetEyeMovements.validation_summary import extract_calibration_data
from scripts.Import import ImportRoiTemplate


class Dispatch:

    def __init__(self, user_input):
        self.user_input = user_input
        self._asc_files = []
        self._roi_template = pd.DataFrame()
        self.results = initialize_result_dict()
        self.main_dispatch()

    def main_dispatch(self):

        self.eye_tracking_dispatch()
        self.roi_dispatch()
        self.analysis_dispatch()
        #self.plotting_dispatch()
        export(self.results, self.user_input)

    def roi_dispatch(self):
        if events_path := self.user_input['roi_event_map_path']:
            event_files = GetPathsFromDirectory(events_path
                                                , metadata_keys_raw=self.user_input['roi_event_map_metadata_keys']
                                                ,
                                                valid_metadata_keys=self.user_input['valid_roi_event_map_metadata_keys']
                                                , filename_contains=self.user_input['roi_event_map_filename_contains']
                                                , target_path_type=self.user_input['roi_event_map_extension']
                                                ).result
            self.results['roi_event_map'] = ImportEventMaps(event_files, self.user_input).result
            print('done: ', 'roi_event_map')

        if test_tag := self.user_input['test_tag_module']:
            self.results['test_resp_tags'] = test_tag(self.results['behavior_test']).result

        if self.user_input['roi_template_path']:
            self._roi_template = ImportRoiTemplate(self.user_input, asc_files=self._asc_files)
            print('done: ', 'roi_template')
        if self._roi_template and self.results['roi_event_map']:
            self.results['trial_roi'] = get_test_roi(self.results['roi_event_map'], self._roi_template)

    def eye_tracking_dispatch(self):
        if asc_dir := str(self.user_input['asc_directory_path']):
            asc_files = GetPathsFromDirectory(asc_dir
                                              , metadata_keys_raw=self.user_input['asc_metadata_keys']
                                              , valid_metadata_keys=self.user_input['valid_asc_metadata_keys']
                                              , target_path_type='.asc'
                                              ).result
            if asc_files:
                self.results['calibration_summary'] = extract_calibration_data(self._asc_files)
                eye_tracking_res = get_eye_movements(asc_files
                                                     , self.user_input['valid_asc_metadata_keys'][:, 1]
                                                     , trial_sets=self.user_input['asc_trial_sets'])
                self.results['filtered_asc'], self.results['eye_movements'], self.results[
                    'fixations'] = eye_tracking_res
                print('done: ', 'fixations')

    def analysis_dispatch(self):
        if not self.results['fixations'].empty and not self.results['trial_roi'].empty:
            fix_roi_dfs = GetFixationRoi(fixations=self.results['fixations']
                                         , roi=self.results['trial_roi']
                                         , fixation_metadata_keys=self.user_input['valid_asc_metadata_keys'][:, 1]
                                         , roi_metadata_keys=self.user_input['roi_event_map_metadata_keys']
                                         , test_trial_col=self.user_input['roi_event_map_trial_column']).result
            print('done: ', 'fixation_roi_all')

        if not self.results['fixation_roi'].empty:
            self.results['stimulus_locked_fixations'], self.results['response_locked_fixations'], self.results[
                'stim_locked_summary'], \
            self.results['stim_locked_summary_filtered'], self.results['resp_locked_summary'], self.results[
                'resp_locked_summary_filtered'] = bin_fixations(self.results['trial_roi']
                                                                , self.user_input['time_bin_size']
                                                                , self.results['roi_event_map']
                                                                , self.results['fixation_roi']
                                                                , self.user_input['summary_filter_out']
                                                                , self.user_input['summary_filter_for'])
            print('done: ', 'stimulus_locked_fixations')

        if self.user_input['calculate_entropy']:
            if not self.results['fixation_roi'].empty:
                self.results['transition_entropy'] = CalculateEntropy(self.results['fixation_roi_condensed'],
                                                                      target_roi=self.user_input['target_roi_entropy'],
                                                                      exclude_diagonals=self.user_input[
                                                                          'exclude_diagonals']).result
            else:
                print('Do not have the required ASC or ROI Inputs to calculate entropy'
                      'Please check that ASC paths and ROI template information is valid.')
'''
    def plotting_dispatch(self):
        if (self.user_input['plot_fixations']) & (not self.results['fixations'].empty):
            PlotFixations(self.results['fixations']
                          , self.results['trial_roi']
                          , self.user_input['output_directory_path']
                          , group_by=self.user_input['group_by']
                          , shape=self.user_input['figure_shape']
                          )
'''