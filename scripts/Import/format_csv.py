import pandas as pd

def format_csv(path):
    df = pd.read_csv(path)
    index_columns = ['subject'
                ,'block_type'
                ,'block_id'
                ,'fix_id'
                ,'trial_id'
                ,'roi_id'
                ,'roi_label'
                ,'test_response_tags'
                ,'react_time_label'
                ,'bin']

    if converted_columns := str_to_numeric(df.columns):
        df.rename(columns=converted_columns, inplace=True)
    df = df.apply(pd.to_numeric, errors='ignore')
    df.set_index(df.loc[:, df.columns.isin(index_columns)].columns.tolist(), inplace=True, append=True)
    return df

def str_to_numeric(arr):
    renamed = {}
    for x in arr:
        try:
            renamed[x] = int(x)
        except ValueError:
            pass
    return renamed
