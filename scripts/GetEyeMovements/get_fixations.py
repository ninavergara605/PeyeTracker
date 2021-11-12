import pandas as pd
import numpy as np


class GetFixations:


    def __init__(self, raw_fixations, metadata_keys):
        self._raw_fixations = raw_fixations
        self._metadata_keys = metadata_keys
        self.result = self.get_fixations()

    def get_fixations(self):
        fixations = self._raw_fixations.copy()
        
        fixations.rename(columns={
                                    5:'x' 
                                    ,6:'y' 
                                    ,7:'avg_pupil_size'
                                    }, inplace=True)
        '''        
        fixations.rename(columns={
                                     '5':'x' 
                                    ,'6':'y' 
                                    ,'7':'avg_pupil_size'
                                    }, inplace=True)
        '''
        fixations = fixations.groupby(self._metadata_keys).filter(lambda x: len(x) > 1) #returns trials with more than one fixation
        fixations['fix_id'] = np.arange(1, len(fixations) + 1)
        return fixations
    


    