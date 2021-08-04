import pandas as pd
import numpy as np


class ImportEventMaps:


    def __init__(self
                ,paths
                ,column_names = None
                ,add_trial_id = False
                ,skip_rows = None
                ,trial_column = None
                ):
        self._paths = paths
        self._column_names = column_names
        
        if self._column_names:
            self._header = None
        else:
            self._header = 0

        self._add_trial_id = add_trial_id
        self._skip_rows = skip_rows
        self._trial_column = trial_column
        self.result = self.import_roi_event_map()

    def import_roi_event_map(self):
        events, metadata_labels = self.create_df()
        events = self.clean_df(events, metadata_labels)
        if self._trial_column:
            events.set_index([self._trial_column],append=True,inplace=True)
        elif self._add_trial_id:
            events['trial_id'] = events.groupby(level=events.index.names[:-1]).cumcount() + 1
            events.set_index(['trial_id'],append=True, inplace=True)
        

        return events  
    
    def create_df(self):
        read_csv_kwargs = {'header': self._header
                        ,'names': self._column_names}
        if self._skip_rows:
            read_csv_kwargs['skiprows'] = self._skip_rows

        dfs = np.array([[subject[:-1] , pd.read_csv(subject.path, **read_csv_kwargs)]
                        for subject in self._paths],dtype=object)
        
        
        metadata_labels = self._paths[0]._fields[:-1]
        events = pd.concat(dfs[:,1], keys=dfs[:,0],
                        names=[*metadata_labels, 'index'])
        return events, metadata_labels

    def clean_df(self,df, drop_cols):
        #convert all strings to lowercase and convert numeric dtypes
        df =  df.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
        df =  df.apply(pd.to_numeric, errors='ignore')

        #drop specified and unnamed columns 
        df  =  df.loc[:,~(df.columns.isin(drop_cols))]
        df =  df.loc[:,~df.columns.str.startswith('Unnamed')]
        return df