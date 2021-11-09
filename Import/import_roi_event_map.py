import pandas as pd
import numpy as np


class ImportEventMaps:


    def __init__(self
                ,paths
                ,column_names = None
                ,add_trial_id = False
                ,skip_rows = None
                ,trial_column = None
                , trial_sets = None
                ):
        self._paths = paths
        self._column_names = column_names
        self._add_trial_id = add_trial_id
        self._skip_rows = skip_rows
        self._trial_sets = trial_sets
        
        if self._column_names:
            self._header = None
        else:
            self._header = 0

        if trial_column:
            self._trial_column = trial_column
        else: 
            self._trial_column = 'trial_id'
            self._add_trial_id = True
        self.result = self.import_roi_event_map()

    def import_roi_event_map(self):
        events, metadata_labels = self.create_df()
        events = self.clean_df(events, metadata_labels)
        
        if self._add_trial_id:
            events['trial_id'] = events.groupby(level=events.index.names[:-1]).cumcount() + 1
        events.set_index([self._trial_column],append=True,inplace=True)
        
        if self._trial_sets:
            self.add_trial_set_labels(events)
        return events  
    
    def create_df(self):
        read_csv_kwargs = {'header': self._header
                        ,'names': self._column_names}
        if self._skip_rows:
            read_csv_kwargs['skiprows'] = self._skip_rows

        dfs = np.array([[subject[:-1] , pd.read_csv(subject.path, **read_csv_kwargs)]
                            for subject in self._paths]
                        ,dtype=object)
        
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

    def add_trial_set_labels(self, events):
        
        for _set in self._trial_sets:
            column_name = _set[0]            
            events[column_name] = np.nan

            for label, trial_range in zip(_set[2], _set[1]):
                if len(trial_range) == 3:
                    in_range_filter = events.index.get_level_values(self._trial_column).isin(list(range(trial_range[0],trial_range[1]+1, trial_range[2])))
                else:
                    in_range_filter = events.index.get_level_values(self._trial_column).isin(list(range(trial_range[0], trial_range[1]+1)))
                
                events[column_name] = np.where(in_range_filter, label, events[column_name])
        return events