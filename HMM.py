"""
Filename:     HMM.py
Version:      1.0
Date:         2018/3/9

Description:  Implements unsupervised HMM learning and emission. Adapted from 
              Homework 6 solutions.

Author(s):    Andrew Kang, Garret Sullivan
Organization: California Institute of Technology
"""

import numpy as np
import random

class HiddenMarkovModel:
    '''
    Class implementation of Hidden Markov Models.
    '''

    def __init__(self, A, O):
        '''
        Initializes an HMM. Assumes the following:
            - States and observations are integers starting from 0. 
            - There is a start state (see notes on A_start below). There
              is no integer associated with the start state, only
              probabilities in the vector A_start.
            - There is no end state. 

        Arguments:
            A:          Transition matrix with dimensions L x L.
                        The (i, j)^th element is the probability of
                        transitioning from state i to state j. Note that
                        this does not include the starting probabilities.

            O:          Observation matrix with dimensions L x D.
                        The (i, j)^th element is the probability of
                        emitting observation j given state i.

        Parameters:
            L:          Number of states.

            D:          Number of observations.
            
            A:          The transition matrix.
            
            O:          The observation matrix.
            
            A_start:    Starting transition probabilities. The i^th element
                        is the probability of transitioning from the start
                        state to state i. For simplicity, we assume that
                        this distribution is uniform.
        '''

        self.L = len(A)
        self.D = len(O[0])
        self.A = A
        self.O = O
        self.A_start = [1. / self.L for _ in range(self.L)]


    def forward(self, x, normalize=False):
        '''
        Uses the forward algorithm to calculate the alpha probability
        vectors corresponding to a given input sequence.

        Arguments:
            x:          Input sequence in the form of a list of length M,
                        consisting of integers ranging from 0 to D - 1.

            normalize:  Whether to normalize each set of alpha_j(i) vectors
                        at each i. This is useful to avoid underflow in
                        unsupervised learning.

        Returns:
            alphas:     Vector of alphas.

                        The (i, j)^th element of alphas is alpha_j(i),
                        i.e. the probability of observing prefix x^1:i
                        and state y^i = j.

                        e.g. alphas[1][0] corresponds to the probability
                        of observing x^1:1, i.e. the first observation,
                        given that y^1 = 0, i.e. the first state is 0.
        '''

        M = len(x)      # Length of sequence.
        alphas = [[0. for _ in range(self.L)] for _ in range(M + 1)]

        # Note that alpha_j(0) is already correct for all j's.
        # Calculate alpha_j(1) for all j's.
        for curr in range(self.L):
            alphas[1][curr] = self.A_start[curr] * self.O[curr][x[0]]

        # Calculate alphas throughout sequence.
        for t in range(1, M):
            # Iterate over all possible current states.
            for curr in range(self.L):
                prob = 0

                # Iterate over all possible previous states to accumulate
                # the probabilities of all paths from the start state to
                # the current state.
                for prev in range(self.L):
                    prob += alphas[t][prev] \
                            * self.A[prev][curr] \
                            * self.O[curr][x[t]]

                # Store the accumulated probability.
                alphas[t + 1][curr] = prob

            if normalize:
                norm = sum(alphas[t + 1])
                for curr in range(self.L):
                    alphas[t + 1][curr] /= norm

        return alphas


    def backward(self, x, normalize=False):
        '''
        Uses the backward algorithm to calculate the beta probability
        vectors corresponding to a given input sequence.

        Arguments:
            x:          Input sequence in the form of a list of length M,
                        consisting of integers ranging from 0 to D - 1.

            normalize:  Whether to normalize each set of alpha_j(i) vectors
                        at each i. This is useful to avoid underflow in
                        unsupervised learning.

        Returns:
            betas:      Vector of betas.

                        The (i, j)^th element of betas is beta_j(i), i.e.
                        the probability of observing prefix x^(i+1):M and
                        state y^i = j.

                        e.g. betas[M][0] corresponds to the probability
                        of observing x^M+1:M, i.e. no observations,
                        given that y^M = 0, i.e. the last state is 0.
        '''

        M = len(x)      # Length of sequence.
        betas = [[0. for _ in range(self.L)] for _ in range(M + 1)]

        # Initialize initial betas.
        for curr in range(self.L):
            betas[-1][curr] = 1

        # Calculate betas throughout sequence.
        for t in range(-1, -M - 1, -1):
            # Iterate over all possible current states.
            for curr in range(self.L):
                prob = 0

                # Iterate over all possible next states to accumulate
                # the probabilities of all paths from the end state to
                # the current state.
                for nxt in range(self.L):
                    if t == -M:
                        prob += betas[t][nxt] \
                                * self.A_start[nxt] \
                                * self.O[nxt][x[t]]

                    else:
                        prob += betas[t][nxt] \
                                * self.A[curr][nxt] \
                                * self.O[nxt][x[t]]

                # Store the accumulated probability.
                betas[t - 1][curr] = prob

            if normalize:
                norm = sum(betas[t - 1])
                for curr in range(self.L):
                    betas[t - 1][curr] /= norm

        return betas


    def unsupervised_learning(self, X, N_iters):
        '''
        Trains the HMM using the Baum-Welch algorithm on an unlabeled
        datset X. Note that this method does not return anything, but
        instead updates the attributes of the HMM object.

        Arguments:
            X:          A dataset consisting of input sequences in the form
                        of lists of length M, consisting of integers ranging
                        from 0 to D - 1. In other words, a list of lists.

            N_iters:    The number of iterations to train on.
        '''

        # Note that a comment starting with 'E' refers to the fact that
        # the code under the comment is part of the E-step.

        # Similarly, a comment starting with 'M' refers to the fact that
        # the code under the comment is part of the M-step.

        for iteration in range(1, N_iters + 1):
            if iteration % 10 == 0:
                print("Iteration: " + str(iteration))

            # Numerator and denominator for the update terms of A and O.
            A_num = [[0. for i in range(self.L)] for j in range(self.L)]
            O_num = [[0. for i in range(self.D)] for j in range(self.L)]
            A_den = [0. for i in range(self.L)]
            O_den = [0. for i in range(self.L)]

            # For each input sequence:
            for x in X:
                M = len(x)
                # Compute the alpha and beta probability vectors.
                alphas = self.forward(x, normalize=True)
                betas = self.backward(x, normalize=True)

                # E: Update the expected observation probabilities for a
                # given (x, y).
                # The i^th index is P(y^t = i, x).
                for t in range(1, M + 1):
                    P_curr = [0. for _ in range(self.L)]
                    
                    for curr in range(self.L):
                        P_curr[curr] = alphas[t][curr] * betas[t][curr]

                    # Normalize the probabilities.
                    norm = sum(P_curr)
                    for curr in range(len(P_curr)):
                        P_curr[curr] /= norm

                    for curr in range(self.L):
                        if t != M:
                            A_den[curr] += P_curr[curr]
                        O_den[curr] += P_curr[curr]
                        O_num[curr][x[t - 1]] += P_curr[curr]

                # E: Update the expectedP(y^j = a, y^j+1 = b, x) for given (x, y)
                for t in range(1, M):
                    P_curr_nxt = [[0. for _ in range(self.L)] for _ in range(self.L)]

                    for curr in range(self.L):
                        for nxt in range(self.L):
                            P_curr_nxt[curr][nxt] = alphas[t][curr] \
                                                    * self.A[curr][nxt] \
                                                    * self.O[nxt][x[t]] \
                                                    * betas[t + 1][nxt]

                    # Normalize:
                    norm = 0
                    for lst in P_curr_nxt:
                        norm += sum(lst)
                    for curr in range(self.L):
                        for nxt in range(self.L):
                            P_curr_nxt[curr][nxt] /= norm

                    # Update A_num
                    for curr in range(self.L):
                        for nxt in range(self.L):
                            A_num[curr][nxt] += P_curr_nxt[curr][nxt]

            for curr in range(self.L):
                for nxt in range(self.L):
                    self.A[curr][nxt] = A_num[curr][nxt] / A_den[curr]

            for curr in range(self.L):
                for xt in range(self.D):
                    self.O[curr][xt] = O_num[curr][xt] / O_den[curr]


    def generate_emission(self, M):
        '''
        Generates an emission of length M, assuming that the starting state
        is chosen uniformly at random. 

        Arguments:
            M:          Length of the emission to generate.

        Returns:
            emission:   The randomly generated emission as a list.

            states:     The randomly generated states as a list.
        '''

        emission = []
        state = random.choice(range(self.L))
        states = []

        for t in range(M):
            # Append state.
            states.append(state)

            # Sample next observation.
            rand_var = random.uniform(0, 1)
            next_obs = 0

            while rand_var > 0:
                rand_var -= self.O[state][next_obs]
                next_obs += 1

            next_obs -= 1
            emission.append(next_obs)

            # Sample next state.
            rand_var = random.uniform(0, 1)
            next_state = 0

            while rand_var > 0:
                rand_var -= self.A[state][next_state]
                next_state += 1

            next_state -= 1
            state = next_state

        return emission, states


    def generate_line(self, syllables, syllable_dict, reverse=False, initial=None):
        '''
        Generates an emission with a set number of syllables, assuming that the 
        starting state is chosen uniformly at random. 

        Arguments:
            syllables:     Number of syllables in the emission to generate.
            syllable_dict: Information about the syllables of each word.
            reverse:       Whether to perform generaation forwards or backwards.
            initial:       The initial observation in the generated output.

        Returns:
            emission:      The randomly generated emission as a list.

            states:        The randomly generated states as a list.
        '''
        
        emission = []
        states = []
        state = None
        
        normal_syllable_count = [0]
        end_syllable_count = [0]
        
        # Reverse the transitions matrix if we're generating backwards
        transitions = self.A
        if reverse:
            #transitions = list(map(list, zip(*self.A)))
            transitions = np.array(transitions).T.tolist()
            
            # Renormalize each row of the transitions matrix
            for i in range(len(transitions)):
                transitions[i] = [transitions[i][j]/sum(transitions[i]) for j in range(len(transitions[i]))] 
        
        if initial != None:
            # We have the initial word for this line already
            emission.append(initial)
            
            normal_syllable_count = syllable_dict[initial]['normal']
            end_syllable_count = normal_syllable_count + syllable_dict[initial]['end'] 
            
            # Find the probability that a given state would generate this word
            prob_states = list(map(list, zip(*self.O)))[initial]
            prob_states = [prob_states[i]/sum(prob_states) for i in range(len(prob_states))]
            
            # Sample the initial state for this word
            rand_var = random.uniform(0, 1)
            initial_state = 0

            while rand_var > 0:
                rand_var -= prob_states[initial_state]
                initial_state += 1

            initial_state -= 1
            states.append(initial_state)
            
            # Sample the next state as well using the initial state
            rand_var = random.uniform(0, 1)
            next_state = 0

            while rand_var > 0:
                rand_var -= transitions[initial_state][next_state]
                next_state += 1

            next_state -= 1
            state = next_state
        else:
            # We don't have anything; just pick an initial state
            state = random.choice(range(self.L))
                
        # Generate words until we reach the requested number of syllables
        while syllables not in end_syllable_count:
            # Add the state to the beginning or end of the state list
            if reverse:
                states.insert(0, state)
            else:
                states.append(state)

            # Sample next observation.
            rand_var = random.uniform(0, 1)
            next_obs = 0
            
            # Zero out the weights of words whose syllables would not fit in this line
            possible_emissions = list(self.O[state])
            for i in range(len(possible_emissions)):
                if i not in syllable_dict:
                    possible_emissions[i] = 0
                else:
                    word_syllables = syllable_dict[i]['normal'] + syllable_dict[i]['end']
                    if min(normal_syllable_count) + min(word_syllables) > 10:
                        possible_emissions[i] = 0
            possible_emissions = [possible_emissions[i]/sum(possible_emissions) for i in range(len(possible_emissions))]

            while rand_var > 0:
                rand_var -= possible_emissions[next_obs]
                next_obs += 1

            next_obs -= 1
            
            # Add the emission to the beginning or end of the emission list
            if reverse:
                emission.insert(0, next_obs)
            else:
                emission.append(next_obs)
            
            # Keep track of how many syllables this line could have
            obs_syllables_normal = syllable_dict[next_obs]['normal']
            obs_syllables_end = syllable_dict[next_obs]['end']
            
            new_normal_syllable_count = []
            new_end_syllable_count = []
            
            for i in range(len(normal_syllable_count)):
                # Add syllables in this word to syllables of the line
                for j in range(len(obs_syllables_normal)):
                    new_normal_syllable_count.append(normal_syllable_count[i] + obs_syllables_normal[j])
                    
                # Include all previous possibilies plus the end possibilies for this word
                new_end_syllable_count = list(new_normal_syllable_count)
                for j in range(len(obs_syllables_end)):
                    new_end_syllable_count.append(normal_syllable_count[i] + obs_syllables_end[j])
                    
            # Update the syllable counts
            normal_syllable_count = new_normal_syllable_count
            end_syllable_count = new_end_syllable_count
                
            # Sample next state.
            rand_var = random.uniform(0, 1)
            next_state = 0

            while rand_var > 0:
                rand_var -= transitions[state][next_state]
                next_state += 1

            next_state -= 1
            state = next_state

        return emission, states
            
    
    def save(self, filename):
        ''' Save the HMM to file. '''
        
        file = open(filename, 'w')
        
        # Save the parameters
        file.write(str(self.L) + "\t" + str(self.D) + "\n")
        
        # Save the transition matrix
        for i in range(len(self.A)):
            file.write("\t".join(str(x) for x in self.A[i]) + "\n")
        
        # Save the observation matrix
        for i in range(len(self.O)):
            file.write("\t".join(str(x) for x in self.O[i]) + "\n")
            
        file.close()
        

def load(filename):
    ''' Load an HMM from file. '''
    
    A = []
    O = []
    
    file = open(filename, 'r')
    
    # Read the parameters
    L, D = [int(x) for x in file.readline().strip().split('\t')]

    # Read the transition matrix
    for i in range(L):
        A.append([float(x) for x in file.readline().strip().split('\t')])

    # Read the observation matrix
    for i in range(L):
        O.append([float(x) for x in file.readline().strip().split('\t')])
        
    file.close()
    
    return HiddenMarkovModel(A, O)
            

def unsupervised_HMM(X, n_states, N_iters):
    '''
    Helper function to train an unsupervised HMM. The function determines the
    number of unique observations in the given data, initializes
    the transition and observation matrices, creates the HMM, and then runs
    the training function for unsupervised learing.

    Arguments:
        X:          A dataset consisting of input sequences in the form
                    of lists of variable length, consisting of integers 
                    ranging from 0 to D - 1. In other words, a list of lists.

        n_states:   Number of hidden states to use in training.
        
        N_iters:    The number of iterations to train on.
    '''

    # Make a set of observations.
    observations = set()
    for x in X:
        observations |= set(x)
    
    # Compute L and D.
    L = n_states
    D = len(observations)

    # Randomly initialize and normalize matrices A and O.
    A = [[random.random() for i in range(L)] for j in range(L)]

    for i in range(len(A)):
        norm = sum(A[i])
        for j in range(len(A[i])):
            A[i][j] /= norm
    
    # Randomly initialize and normalize matrix O.
    O = [[random.random() for i in range(D)] for j in range(L)]

    for i in range(len(O)):
        norm = sum(O[i])
        for j in range(len(O[i])):
            O[i][j] /= norm

    # Train an HMM with unlabeled data.
    HMM = HiddenMarkovModel(A, O)
    HMM.unsupervised_learning(X, N_iters)

    return HMM

