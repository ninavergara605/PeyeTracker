import pandas as pd


class CombineDfs:


    def __init__(self):
        self.store_data =CombineDfs.store_output()

    @staticmethod
    def store_output():
        dfs = []
        subject_infos = []

        def add_df(df=None, subject_block=None):
            nonlocal dfs
            nonlocal subject_infos
            if subject_block:
                dfs.append(df)
                subject_infos.append(subject_block)
                return dfs, subject_infos
            
            dfs.append(df)
            return dfs, subject_infos
        return add_df

    def create_df(self):
        index_names = ['subject', 'block_type', 'block_id']
        dfs, concat_keys = self.store_data()
        if concat_keys:
            output_df = pd.concat(dfs, 
                                    keys=concat_keys, 
                                    names=index_names)
        else:
            output_df = pd.concat(dfs)
        return output_df