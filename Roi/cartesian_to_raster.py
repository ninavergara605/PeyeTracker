from GetEyeMovements.filter_text import FilterText
import pandas as pd

def raster_conversion(roi_template, asc_files=None, metadata_keys=None, aspect_ratio=None):
    if aspect_ratio:
        converted_roi_template=calc_raster_coords(roi_template, aspect_ratio)
    elif asc_files:
        screen_dim = FilterText(asc_files, search_for=["GAZE_COORDS"]).result
        filtered_dim = screen_dim.drop_duplicates().apply(pd.to_numeric, errors='ignore').values
        
        x_len = filtered_dim[:,3] - filtered_dim[:,1]
        y_len = filtered_dim[:,4] - filtered_dim[:,2]      

        if  len(filtered_dim) > 1:
            converted_roi_template = screen_dim.groupby(metadata_keys).apply(lambda x: calc_raster_coords(roi_template, x.iloc[-2:].values))
        else:
            converted_roi_template = calc_raster_coords(roi_template,(x_len, y_len))
        
    else:
        print("Do not have the necessary inputs to convert Roi Template Coordinates to Raster")
        print("Please specify the aspect ratio or provide an ASC path")
        return roi_template
    return converted_roi_template


def calc_raster_coords(roi_template, aspect_ratio):

    x_len, y_len = aspect_ratio
    shift_x, shift_y = x_len/2, y_len/2
    x_cols = ['bottom_right_x', 'top_left_x']
    y_cols = ['bottom_right_y', 'top_left_y']
    for col in x_cols:
        roi_template[('static',col)] = roi_template[('static',col)] + shift_x
        roi_template[('dynamic_event_options',col)] = roi_template[('dynamic_event_options',col)] + shift_x
    for col in y_cols:
        roi_template[('static',col)] = y_len-(roi_template[('static',col)] + shift_y)
        roi_template[('dynamic_event_options',col)]  = y_len-(roi_template[('dynamic_event_options',col)]  + shift_y)
    return roi_template
