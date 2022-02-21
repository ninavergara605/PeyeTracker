import pandas as pd
from ..Roi.raster_conversion import ShiftOrigin


class ImportRoiTemplate:
    def __init__(self, user_input, asc_files=None):
        self._roi_template_path = user_input['roi_template_path']
        self._calc_raster_coordinates = user_input['calc_roi_raster_coords']
        self.user_input = user_input
        self._asc_files = asc_files
        self.result = self.roi_template_import()

    def roi_template_import(self):
        template_df = pd.read_excel(self._roi_template_path, header=[0, 1]).apply(pd.to_numeric, errors='ignore')
        template_df = template_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)

        coord_headers = ['static', 'dynamic_event_options']
        cleaned_dfs = [template_df['dynamic_roi_label']]
        for header in coord_headers:
            df_section = template_df[header].dropna(how='all')
            cleaned_section = ImportRoiTemplate.get_coords_and_ranges(df_section)

            if self._calc_raster_coordinates:
                converted_section = ShiftOrigin(cleaned_section, self.user_input, self._asc_files).result
                cleaned_dfs.append(converted_section)
            else:
                cleaned_dfs.append(cleaned_section)
        cleaned_template = pd.concat(cleaned_dfs, axis=1, keys=['dynamic_roi_label', 'static', 'dynamic_event_options'])
        return cleaned_template

    @staticmethod
    def get_coords_and_ranges(col):
        xy_labels = [['bottom_right_x', 'bottom_right_y'], ['top_left_x', 'top_left_y']]
        for coords, label in zip([col.bottom_right_xy, col.top_left_xy], xy_labels):
            try:
                verified = coords.str.split(',').apply(lambda x: list(map(float, x)))
                col[label[0]] = verified.str[0]
                col[label[1]] = verified.str[1]
            except ValueError:
                print(f"at least one invalid roi template coordinate exists in {coords} for {label}")
        return col


