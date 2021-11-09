import functools
import types

def clean_output(func):
    @functools.wraps(func)

    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        cleaned = clean_cols(output)
        return cleaned
    return wrapper


def clean_cols(df):
    drop_cols_filt = df.columns.str.startswith('Unnamed') | df.columns.str.startswith('level')
    df.drop(df.columns[drop_cols_filt], axis='columns', inplace=True) 
    
    return df