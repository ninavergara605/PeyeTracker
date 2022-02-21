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
        , 'asc_directory_path': ''
        , 'asc_metadata_keys': []

        # Roi Template and iPosition Options
        , 'roi_template_path': None
        , 'calc_roi_raster_coords': True
        , 'aspect_ratio': ()

        , 'actual_coordinate_path': ''
        , 'actual_coordinate_time_window': ()
        , 'coordinate_labels': None
        , 'roi_width': None
        , 'roi_height': None

        # Roi Event Map Options
        , 'roi_event_map_path': None
        , 'roi_event_map_metadata_keys': []
        , 'roi_event_map_trial_column': None
        , 'roi_event_map_extension': None

        , 'roi_event_map_filename_contains': None
        , 'roi_event_map_import_skip_rows': None
        , 'roi_event_map_columns': None
        , 'add_roi_event_map_trial_id': True


        # Trial Set Options (creates new columns based on trial ranges)
        , 'roi_event_map_trial_sets': None
        , 'asc_trial_sets': None

        # Binning Options
        , 'time_bin_size': None
        , 'summary_filter_out': None
        , 'summary_filter_for': None

        # Entropy Options
        , 'calculate_entropy': True
        , 'target_roi_entropy': None
        , 'exclude_diagonals': False

        # Plotting Options
        , 'plot_fixations': False
        , 'group_by': []
        , 'figure_shape': ()
    })
Dispatch(user_input)
