from scripts.GetEyeMovements.filter_text import FilterText
import pandas as pd


class ShiftOrigin:

    def __init__(self, df, user_input,  asc_files):
        self._calc_raster_coordinates = user_input['calc_roi_raster_coords']
        self._aspect_ratio = user_input["aspect_ratio"]
        self._asc_metadata_keys = user_input['valid_asc_metadata_keys'][:, 1]
        self._asc_files = asc_files
        self.result = self.raster_conversion(df)

    def raster_conversion(self, df):
        if self._aspect_ratio:
            x_len, y_len = self._aspect_ratio
        elif self._asc_files:
            screen_dim = FilterText(self._asc_files, search_for=["GAZE_COORDS"]).result
            filtered_dim = screen_dim.drop_duplicates().apply(pd.to_numeric, errors='ignore').values

            if len(filtered_dim) > 1:
                raise Exception('More than one aspect ratios are present in ASC files')
            else:
                x_len = filtered_dim[0, 3] - filtered_dim[0, 1]
                y_len = filtered_dim[0, 4] - filtered_dim[0, 2]
        else:
            print("Do not have the necessary inputs to convert Roi Template Coordinates to Raster")
            print("Please specify the aspect ratio or provide an ASC path")
            return df
        df = df.assign(**dict(zip(['x_len', 'y_len'], [x_len, y_len])))
        converted_df = ShiftOrigin.calc_raster_coordinates(df)
        return converted_df

    @staticmethod
    def calc_raster_coordinates(df):
        xcols = ['bottom_right_x', 'top_left_x']
        ycols = ['bottom_right_y', 'top_left_y']
        shift_x, shift_y = df['x_len'] / 2, df['y_len'] / 2
        for col in xcols:
            df[col] = df[col] + shift_x
        for col in ycols:
            df[col] = df['y_len'] - (df[col] + shift_y)
        return df.drop(columns=['x_len', 'y_len'])
