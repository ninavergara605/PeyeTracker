import pandas as pd


def import_behavior_test(behavior_path, metadata_cols):
    df = pd.read_excel(behavior_path)
    
    #if possible, convert values to numeric dtype
    df = df.apply(pd.to_numeric, errors='ignore')
    #if characters, ensure that column values are lowercase
    df = df.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
    df.columns = [x.lower() if isinstance(x, str) else x for x in df.columns ]
    
    df = df.dropna(subset=metadata_cols)
    df.set_index(metadata_cols, inplace=True)
    final_df, duplicate_metadata = filter_duplicated(df)
    return final_df, duplicate_metadata


def filter_duplicated(df):
    is_duplicated = df.index.duplicated(keep='last')
    if any(is_duplicated):
        duplicated = df[is_duplicated]
        unique_df = df[~is_duplicated]
        return unique_df, duplicated
    return df, pd.DataFrame()