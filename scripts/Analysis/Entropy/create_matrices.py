import numpy as np


class CreateTransitionMatrices:

    def __init__(self, fixation_roi, target_roi, exclude_diagonals):
        self._fixation_roi = fixation_roi
        self._target_roi = target_roi
        self._exclude_diagonals = exclude_diagonals
        self._transitions = self.get_transitions()
        self.result = self.create_transition_matrices()

    def get_transitions(self):
        if 'roi_id' in self._fixation_roi.index.names:
            metadata_names = self._fixation_roi.index.names[:-3]
        else:
            metadata_names = self._fixation_roi.index.names

        df = self._fixation_roi.reset_index().dropna(subset=['roi_id']).sort_values(
            metadata_names + ['start_fix']).set_index(metadata_names)

        if self._target_roi:
            df = self.filter_roi(df)
        else:
            self._target_ids = df.reset_index()['roi_id'].drop_duplicates()

        transitions = df['roi_id'].to_frame().rename(columns={'roi_id': 'to'})
        transitions['from'] = transitions['to'].groupby(level=transitions.index.names).apply(lambda x: x.shift(1))
        return transitions.dropna()

    def filter_roi(self, df):
        if isinstance(self._target_roi[0], str):
            label_ids = self._fixation_roi.reset_index()[['roi_id', 'roi_label']].drop_duplicates()
            self._target_ids = [x[0] for x in label_ids.values if x[1] in self._target_roi]
        else:
            self._target_ids = self._target_roi
        filtered_df = df[df.roi_id.isin(self._target_ids)]
        return filtered_df

    def create_transition_matrices(self):
        num_roi = len(self._target_ids)
        matrix_ids = np.arange(0, num_roi)

        replace_dict = dict(zip(self._target_ids, matrix_ids))
        matrix_transitions = self._transitions.replace(replace_dict)

        transition_matrices = []
        metadata = []
        for metadata_vals, transitions in matrix_transitions.groupby(level=matrix_transitions.index.names):
            counts = np.zeros((num_roi, num_roi))
            for to_idx, from_idx in transitions.values:
                counts[int(from_idx), int(to_idx)] += 1

            fill_value = 1 / num_roi
            for i in range(num_roi):
                if all(x == 0 for x in counts[i, :]):
                    counts[i, :] = fill_value

            transition_matrices.append(np.array(counts))
            metadata.append(metadata_vals)
        return transition_matrices, metadata
