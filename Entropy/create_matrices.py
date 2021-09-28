import numpy as np


class CreateTransitionMatrices:


    def __init__(self, fixation_roi, target_roi):
        self._fixation_roi = fixation_roi
        self._target_roi = target_roi
        self._transitions = self.get_transitions()
        self.result = self.create_transition_matrices()

    def get_transitions(self):
        metadata_names = self._fixation_roi.index.names[:-3]
        df = self._fixation_roi.dropna().reset_index().sort_values(metadata_names+['start_fix']).set_index(metadata_names)
        transitions = df['roi_id'].to_frame().rename(columns={'roi_id':'to'})
        transitions['from'] = transitions['to'].groupby(level=transitions.index.names).apply(lambda x: x.shift(1))
    
        if self._target_roi:
            return self.filter_roi(transitions)
        else:
            self._target_ids = self._fixation_roi.reset_index()['roi_id'].drop_duplicates()

        return transitions.dropna()

    def filter_roi(self, transitions):
        if isinstance(self._target_roi[0], str):
            label_ids = self._fixation_roi.reset_index()[['roi_id', 'roi_label']].drop_duplicates()
            self._target_ids = [x[0] for x in label_ids.values if x[1] in self._target_roi]
        else:
            self._target_ids = self._target_roi

        filtered_transitions = transitions[(transitions['to'].isin(self._target_ids)) 
                                                & (transitions['from'].isin(self._target_ids))]        
        return filtered_transitions.dropna()

    def create_transition_matrices(self):
        num_roi = len(self._target_ids)
        matrix_ids = np.arange(0,num_roi)

        replace_dict = dict(zip(self._target_ids, matrix_ids))
        matrix_transitions = self._transitions.replace(replace_dict)

        transition_matrices = []
        metadata = []
        for metadata_vals, transitions in matrix_transitions.groupby(level=matrix_transitions.index.names):
            counts = np.zeros((num_roi, num_roi))
            for to_idx, from_idx in transitions.values:
                counts[int(from_idx), int(to_idx)] += 1
            transition_matrices.append(np.array(counts))
            metadata.append(metadata_vals)
        return transition_matrices, metadata


