from scripts.ValidateUserInput.user_input import validate_user_input
from scripts.dispatch import Dispatch

if __name__ == "__main__":

    user_input = validate_user_input({
        # Export Options
        'output_directory_path': None
        , 'output_folder_name': None
        , 'attach_event_cols': None
        , 'attach_movement_cols': None

        # Eye Movement Options
        , 'asc_directory_path': r'C:\Users\janavic2\Downloads\PeyeTracker\test_data\asc_files'
        , 'asc_metadata_keys': ['subject_id', 'block_id']

        # Roi Template Options
        , 'roi_template_path': r'C:\Users\janavic2\Downloads\PeyeTracker\test_data\roi_templates\roi_template_version_1.xlsx'
        , 'calc_roi_raster_coords': False
        , 'aspect_ratio': None

        # Roi Event Map Options
        , 'roi_event_map_path': r'C:\Users\janavic2\Downloads\PeyeTracker\test_data\roi_event_maps'
        , 'roi_event_map_metadata_keys': ['subject_id', 'block_id']
        , 'roi_event_map_trial_column': 'trial_id'
        , 'roi_event_map_extension': '.csv'

        , 'roi_event_map_filename_contains': None
        , 'roi_event_map_import_skip_rows': None
        , 'roi_event_map_columns': None
        , 'add_roi_event_map_trial_id': False


        # Trial Set Options (creates new columns based on trial ranges)
        , 'roi_event_map_trial_sets': None
        , 'asc_trial_sets': None

        # Binning Options
        , 'time_bin_size': 250
        , 'summary_filter_out': None
        , 'summary_filter_for': None

        # Entropy Options
        , 'calculate_entropy': True
        , 'target_roi_entropy': None
        , 'exclude_diagonals': False

        # Plotting Options
        , 'plot_fixations': False
        , 'group_by': []
        , 'figure_shape': None
    })
Dispatch(user_input)
