from scripts.PathUtilities.general_path_functions import create_path
class GetResultPaths:


    def __init__(self, user_input):
        self._user_input = user_input
        self._fixations = ''
        self._test_roi = ''
        self._test_resp_tag = ''
        self._filtered_asc = ''
        self._fixation_roi = ''
        self._stimulus_locked_bin = ''
        self._duplicate_data_asc = ''
        self._duplicate_data_behavior_test = ''
        self._response_locked_bin = ''
        self._saccades = ''
        self._entropy = ''
        self._eye_movements = ''
        self._resp_locked_summary_all_roi = ''
        self._stim_locked_summary_all_roi = ''
        self._resp_locked_summary_filtered_roi = ''
        self._stim_locked_summary_filtered_roi = ''
        self._missing_asc = ''
        self._bad_response_trials = ''
        self._no_roi_fixation_trials = ''
        self._fixation_roi_dropna = ''

    @property
    def fixations(self):
        if not self._fixations:
            self._fixations = create_path(
                                    self._user_input['output_directory_path'] 
                                    ,'fixations'
                                    ,folder='processed_eye_movements')
        return self._fixations

    @property
    def test_roi(self):
        if not self._test_roi:
            self._test_roi = create_path(
                                    self._user_input['output_directory_path'] 
                                    ,'test_roi'
                                    ,folder='processed_behavior_test')
        return self._test_roi
    
    @property
    def test_resp_tag(self):
        if not self._test_resp_tag:
            self._test_resp_tag = create_path(
                                    self._user_input['output_directory_path'] 
                                    ,'test_tag'
                                    ,folder='processed_behavior_test')
        return self._test_resp_tag
    
    @property
    def filtered_asc(self):
        if not self._filtered_asc:
            self._filtered_asc = create_path(
                                                self._user_input['output_directory_path'] 
                                                ,'filtered_asc'
                                                ,folder='processed_eye_movements')
        return self._filtered_asc

    @property
    def stimulus_locked_bin(self):
        if not self._stimulus_locked_bin:
            self._stimulus_locked_bin = create_path(
                                                self._user_input['output_directory_path'] 
                                                ,'stimulus_locked_movements'
                                                ,folder='analysis')
        return self._stimulus_locked_bin
    
    @property
    def response_locked_bin(self):
        if not self._response_locked_bin:
            self._response_locked_bin = create_path(
                                                self._user_input['output_directory_path'] 
                                                ,'response_locked_movements'
                                                ,folder='analysis')
        return self._response_locked_bin
    

    @property
    def duplicate_data_asc(self):
        if not self._duplicate_data_asc:
            self._duplicate_data_asc = create_path(
                                                self._user_input['output_directory_path']
                                                ,'duplicate_data_asc'
                                                ,folder='metadata_summary')
        return self._duplicate_data_asc

    
    @property
    def duplicate_data_behavior_test(self):
        if not self._duplicate_data_behavior_test:
            self._duplicate_data_behavior_test = create_path(
                                                    self._user_input['output_directory_path']
                                                    ,'duplicate_data_behavior_test'
                                                    ,folder='metadata_summaries')
        return self._duplicate_data_behavior_test

    @property
    def fixation_roi(self):
        if not self._fixation_roi:
            self._fixation_roi = create_path(
                                            self._user_input['output_directory_path']
                                            ,'fixation_roi'
                                            ,folder='analysis')
        return self._fixation_roi
    
    @property
    def eye_movements(self):
        if not self._eye_movements:
            self._eye_movements = create_path(
                                            self._user_input['output_directory_path']
                                            ,'eye_movements'
                                            ,folder='processed_eye_movements')
        return self._eye_movements
    
    @property
    def saccades(self):
        if not self._saccades:
            self._saccades = create_path(
                                        self._user_input['output_directory_path']
                                        ,'saccades'
                                        ,folder='processed_eye_movements')
        return self._saccades

    @property
    def entropy(self):
        if not self._entropy:
            self._entropy = create_path(
                                        self._user_input['output_directory_path']
                                        ,'entropy'
                                        ,folder='analysis')
        return self._entropy

    @property
    def stim_locked_summary_all_roi(self):
        if not self._stim_locked_summary_all_roi:
            self._stim_locked_summary_all_roi = create_path(
                                        self._user_input['output_directory_path']
                                        ,'stim_locked_summary_all_roi'
                                        ,folder='analysis_summaries')
        return self._stim_locked_summary_all_roi
    
    @property
    def resp_locked_summary_all_roi(self):
        if not self._resp_locked_summary_all_roi:
            self._resp_locked_summary_all_roi = create_path(
                                        self._user_input['output_directory_path']
                                        ,'resp_locked_summary_all_roi'
                                        ,folder='analysis_summaries')
        return self._resp_locked_summary_all_roi

    @property
    def stim_locked_summary_filtered_roi(self):
        if not self._stim_locked_summary_filtered_roi:
            self._stim_locked_summary_filtered_roi = create_path(
                                        self._user_input['output_directory_path']
                                        ,'stim_locked_summary_filtered_roi'
                                        ,folder='analysis_summaries')
        return self._stim_locked_summary_filtered_roi
    
    @property
    def resp_locked_summary_filtered_roi(self):
        if not self._resp_locked_summary_filtered_roi:
            self._resp_locked_summary_filtered_roi = create_path(
                                        self._user_input['output_directory_path']
                                        ,'resp_locked_summary_filtered_roi'
                                        ,folder='analysis_summaries')
        return self._resp_locked_summary_filtered_roi

    @property
    def missing_asc(self):
        if not self._missing_asc:
            self._missing_asc = create_path(
                                        self._user_input['output_directory_path']
                                        ,'missing_asc'
                                        ,folder='metadata_summaries')
        return self._missing_asc

    @property
    def bad_response_trials(self):
        if not self._bad_response_trials:
            self._bad_response_trials = create_path(
                                        self._user_input['output_directory_path']
                                        ,'bad_response_trials'
                                        ,folder='metadata_summaries')
        return self._bad_response_trials

    @property
    def no_roi_fixation_trials(self):
        if not self._no_roi_fixation_trials:
            self._no_roi_fixation_trials = create_path(
                                        self._user_input['output_directory_path']
                                        ,'no_roi_fixation_trials'
                                        ,folder='metadata_summaries')
        return self._no_roi_fixation_trials

    @property
    def fixation_roi_dropna(self):
        if not self._fixation_roi_dropna:
            self._fixation_roi_dropna = create_path(
                                        self._user_input['output_directory_path']
                                        ,'fixation_roi_dropna'
                                        ,folder='analysis')
        return self._fixation_roi_dropna