import pandas as pd
import numpy as np

def roi_template_import(roi_template_path):
    template_df = pd.read_excel(roi_template_path, header=[0,1])
    template_df = template_df.apply(pd.to_numeric, errors='ignore')
    template_df = template_df.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
    
    static = template_df['static'].apply(get_coords_and_ranges, axis=1)
    dynamic = template_df['dynamic_event_options'].apply(get_coords_and_ranges, axis=1)
    all_dfs =  [static, dynamic, template_df['dynamic_roi_label']]
    template = pd.concat(all_dfs, axis=1, keys=['static','dynamic_event_options', 'dynamic_roi_label'])
    return template

def get_coords_and_ranges(row):    
    if not isinstance(row.top_left_xy,str):
        return row
    xy_labels = [['bottom_right_x','bottom_right_y'],['top_left_x','top_left_y']]
    
    for coord, label in zip([row.bottom_right_xy, row.top_left_xy], xy_labels):
        verified = verify_coord(coord)
        if verified:
            row[label[0]] = verified[0]
            row[label[1]] = verified[1]
        else:
            print(f"invalid roi template coordinate {coord} for {label}")
    return row

def verify_coord(coord):
    try:
        x, y = tuple(map(float, coord.split(',')))
        return x,y
    except ValueError:
        return None



