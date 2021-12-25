import numpy as np
import pandas as pd
from .create_matrices import CreateTransitionMatrices

class CalculateEntropy:


    def __init__(self
                ,fixation_roi
                ,target_roi= None
                ,exclude_diagonals = False
                ):
        self.stationary_entropies = None
        self.raw_entropies = None
        self.normalized_entropies = None
        self.result = None
        self.fixation_roi = fixation_roi
        self._exclude_diagonals = exclude_diagonals
        
        self._transition_counts, self._metadata = CreateTransitionMatrices(fixation_roi,target_roi, exclude_diagonals).result   
        print(self._transition_counts)
        self.transition_probabilities = self.get_trans_probability()
        
        self.stationary_distributions = self.calc_stationary_distribution()
        if len(self.stationary_distributions) > 0:

            self.stationary_entropies = self.calculate_stationary_entropy()
            self.raw_entropies = self.calc_entropy()
            self.normalized_entropies = self.normalize()
            self.result = self.format_entropies()
    
    def format_entropies(self):
        if 'roi_id' in self.fixation_roi.index.names:
            index_names = self.fixation_roi.index.names[:-3]
        else:
            index_names = self.fixation_roi.index.names
        df = pd.DataFrame(self.normalized_entropies, columns=['transition_entropy'], index=pd.MultiIndex.from_tuples(self._metadata))
        
        df.index.names = index_names
        #df['stationary_entropy'] = self.stationary_entropies
        
        return df.replace(-1,None)
        
    def get_trans_probability(self):
        transition_prob_all = []
        for matrix in self._transition_counts:
            if self._exclude_diagonals:
                np.fill_diagonal(matrix,0)
            
            row_sums = np.sum(matrix, axis=1)
            trans_prob = matrix / row_sums[:,None]
            transition_prob_all.append(trans_prob)
        return transition_prob_all

    def calc_stationary_distribution(self):
        stationary_distributions = []
        for matrix in self.transition_probabilities:
            np.nan_to_num(matrix,copy=False)
            '''
            Since the sum of each row is 1, our matrix is row stochastic.
            We'll transpose the matrix to calculate eigenvectors of the stochastic rows.
            '''
            transition_matrix_transp = matrix.T
            eigenvals, eigenvects = np.linalg.eig(transition_matrix_transp)
            '''
            Find the indexes of the eigenvalues that are close to one.
            Use them to select the target eigen vectors. Flatten the result.
            '''
            close_to_1_idx = np.isclose(eigenvals,1)
            if len(close_to_1_idx[close_to_1_idx == True]) == 0:
                stationary_distributions.append([])
            else:   
                target_eigenvect = eigenvects[:,close_to_1_idx]
                target_eigenvect = target_eigenvect[:,0]
                # Turn the eigenvector elements into probabilites
                stationary_distrib = target_eigenvect / sum(target_eigenvect)
                stationary_distributions.append(stationary_distrib.real)
        return stationary_distributions

    def calc_entropy(self):
        raw_entropies = []
        for prob_matrix, distributions in zip(self.transition_probabilities, self.stationary_distributions):
            if len(distributions) > 0:
                entropy_matrix = distributions[:,None]*(prob_matrix* np.log2(prob_matrix))
                entropy_matrix = np.nan_to_num(entropy_matrix)
                
                total_entropy = np.sum(entropy_matrix)
                raw_entropies.append(total_entropy)
            else: 
                raw_entropies.append(-1)
        return raw_entropies

    def normalize(self):
        s = len(self._transition_counts[0])
        if self._exclude_diagonals:
            probability = 1/(s-1)
        else:
            probability = 1/s
        max_entropy = np.log2(probability)
        
        normalized = []
        for entropy in self.raw_entropies:
            if entropy == -1:
                normalized.append(-1)
            else:
                norm_entropy = np.round(entropy/max_entropy,3)
                normalized.append(np.abs(norm_entropy))
        return normalized

    def calculate_stationary_entropy(self):
        stationary_entropies = []
        for distributions in self.stationary_distributions:
            if len(distributions) > 0:
                stationary_entropy = sum([x*np.log2(1/x) for x in distributions])
            
                normalized = stationary_entropy/np.log2(len(distributions))
                stationary_entropies.append(np.round(normalized,3))
            else: 
                stationary_entropies.append([])
        return stationary_entropies