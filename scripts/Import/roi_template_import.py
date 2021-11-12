import pandas as pd
from scripts.GetEyeMovements.filter_text import FilterText


class ImportRoiTemplate:
    def __init__(self, user_input, asc_files=None):
        self._roi_template_path = user_input['roi_template_path']
        self._calc_raster_coordinates = user_input['calc_roi_raster_coords']
        self._aspect_ratio = user_input["aspect_ratio"]
        self._asc_metadata_keys = self.user_input['valid_asc_metadata_keys'][:, 1]
        self._asc_files = asc_files
        self.result = self.roi_template_import()

    def roi_template_import(self):
        template_df = pd.read_excel(self._roi_template_path, header=[0, 1])
        template_df = template_df.apply(pd.to_numeric, errors='ignore')
        template_df = template_df.apply(lambda x: x.str.lower() if (x.dtype == 'object') else x)

        static = template_df['static'].apply(ImportRoiTemplate.get_coords_and_ranges, axis=1)
        dynamic = template_df['dynamic_event_options'].apply(ImportRoiTemplate.get_coords_and_ranges, axis=1)
        all_dfs = [static, dynamic, template_df['dynamic_roi_label']]
        template = pd.concat(all_dfs, axis=1, keys=['static', 'dynamic_event_options', 'dynamic_roi_label'])
        if self._calc_raster_coordinates:
            converted_template = self.raster_conversion(template)
            return converted_template
        return template

    @staticmethod
    def get_coords_and_ranges(row):
        if not isinstance(row.top_left_xy, str):
            return row
        xy_labels = [['bottom_right_x', 'bottom_right_y'], ['top_left_x', 'top_left_y']]

        for coord, label in zip([row.bottom_right_xy, row.top_left_xy], xy_labels):
            verified = ImportRoiTemplate.verify_coord(coord)
            if verified:
                row[label[0]] = verified[0]
                row[label[1]] = verified[1]
            else:
                print(f"invalid roi template coordinate {coord} for {label}")
        return row

    @staticmethod
    def verify_coord(coord):
        try:
            x, y = tuple(map(float, coord.split(',')))
            return x, y
        except ValueError:
            return None

    def raster_conversion(self, roi_template):
        if self._aspect_ratio:
            converted_roi_template = ImportRoiTemplate.calc_raster_coordinates(roi_template, self._aspect_ratio)
        elif self._asc_files:
            screen_dim = FilterText(self._asc_files, search_for=["GAZE_COORDS"]).result
            filtered_dim = screen_dim.drop_duplicates().apply(pd.to_numeric, errors='ignore').values

            x_len = filtered_dim[:, 3] - filtered_dim[:, 1]
            y_len = filtered_dim[:, 4] - filtered_dim[:, 2]

            if len(filtered_dim) > 1:
                converted_roi_template = screen_dim.groupby(self._asc_metadata_keys).apply(
                    lambda x: ImportRoiTemplate.calc_raster_coordinates(roi_template, x.iloc[-2:].values))
            else:
                converted_roi_template = ImportRoiTemplate.calc_raster_coordinates(roi_template, (x_len, y_len))
        else:
            print("Do not have the necessary inputs to convert Roi Template Coordinates to Raster")
            print("Please specify the aspect ratio or provide an ASC path")
            return roi_template
        return converted_roi_template

    @staticmethod
    def calc_raster_coordinates(roi_template, aspect_ratio):
        x_len, y_len = aspect_ratio
        shift_x, shift_y = x_len / 2, y_len / 2
        x_cols = ['bottom_right_x', 'top_left_x']
        y_cols = ['bottom_right_y', 'top_left_y']
        for col in x_cols:
            roi_template[('static', col)] = roi_template[('static', col)] + shift_x
            roi_template[('dynamic_event_options', col)] = roi_template[('dynamic_event_options', col)] + shift_x
        for col in y_cols:
            roi_template[('static', col)] = y_len - (roi_template[('static', col)] + shift_y)
            roi_template[('dynamic_event_options', col)] = y_len - (
                    roi_template[('dynamic_event_options', col)] + shift_y)
        return roi_template
