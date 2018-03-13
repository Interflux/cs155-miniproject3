"""
Filename:     preprocess.py
Version:      1.0
Date:         2018/3/9

Description:  Handles preprocessing of data for CS 155's third miniproject.

Author(s):    Dennis Lam, Garret Sullivan
Organization: California Institute of Technology
"""

import random
import HMM
import HMM_helper

def parse_line(line):
    """ Parses a line of the sonnets. """
    
    # Remove unwanted characters
    for char in line:
        if char in ",.!?;:()":
            line = line.replace(char, '')

    # Convert to all-lowercase
    line = line.lower()
    
    # Store as a list of words
    raw_words = line.split()
    
    clean_words = []
    for word in raw_words:
        # Remove quotation marks (apostrophe at the beginning or end of a word)
        if word[0] == "'":
            word = word[1:]
        # Unless it's actually part of a "word" that Shakespeare uses
        if word[-1] == "'" and word != "t'" and word != "th'":
            word = word[:-1]
        clean_words.append(word)       
    
    # Return the line as a list of words
    return clean_words


def parse_file(filename):
    """ Parses the "shakespeare.txt" file containing the sonnets. """
    
    # Exclude these sonnets because they don't follow the typical pattern
    excluded_sonnets = [99, 126]
    
    quatrain_lines = []
    volta_lines = []
    couplet_lines = []
    rhymes = []
    
    obs_counter = 0
    obs_word_to_int = {}
    obs_int_to_word = {}
    
    # Open the file containing the poems
    file_in = open(filename, 'r')

    # Read the first line
    line = file_in.readline()

    while (line != ''):
        # Beginning of a new poem
        if line.strip().isdigit() and int(line.strip()) not in excluded_sonnets:
            for i in range(14):
                obs_elem = []
                
                # Read a line and tokenize it
                line = file_in.readline()
                words = parse_line(line)
                
                # Encode the words as integers
                for word in words:
                    # Add the word to the observation maps if needed
                    if word not in obs_word_to_int:
                        obs_word_to_int[word] = obs_counter
                        obs_int_to_word[obs_counter] = word
                        obs_counter += 1
                        
                    # Add the encoded word
                    obs_elem.append(obs_word_to_int[word])
                
                # Add the encoded line to the appropriate list
                if i in range(0, 8):
                    # First two quatrains
                    quatrain_lines.append(obs_elem)
                elif i in range (8, 12):
                    # Volta (third quatrain)
                    volta_lines.append(obs_elem)
                elif i in range(12, 14):
                    # Couplet
                    couplet_lines.append(obs_elem)

        # Burn through "unaffiliated" lines
        else:
            line = file_in.readline()
            
    # Close the file containing the poems
    file_in.close()
    
    # Add the rhyming words to a list
    raw_rhymes = []
    
    quad_lines = quatrain_lines + volta_lines
    for i in range(0, len(quad_lines), 4):
        raw_rhymes.append(set([quad_lines[i][-1], quad_lines[i+2][-1]]))
        raw_rhymes.append(set([quad_lines[i+1][-1], quad_lines[i+3][-1]]))
        
    for i in range(0, len(couplet_lines), 2):
        raw_rhymes.append(set([couplet_lines[i][-1], couplet_lines[i+1][-1]]))
        
    # Combine the pairs of rhyming words into sets of rhyming words
    for raw_rhyme in raw_rhymes:
        found_rhyme = False
        
        # Check if a matching rhyme is already in the list
        for rhyme_set in rhymes:
            if len(rhyme_set.intersection(raw_rhyme)) != 0:
                # Found a matching rhyme
                rhymes.append(rhyme_set.union(raw_rhyme))
                rhymes.remove(rhyme_set)
                found_rhyme = True
                break
        
        # If we didn't find a matching rhyme, add it to the list directly
        if not found_rhyme:
            rhymes.append(raw_rhyme)
            
    # Return the lines, the maps, and the rhymes
    return (quatrain_lines, volta_lines, couplet_lines, obs_word_to_int, obs_int_to_word, rhymes)


def parse_syllables(filename, word_to_int_map):
    """ Parses the "Syllable_dictionary.txt" file containing the syllable data. """
    
    syllable_dictionary = {}
    
    # Open the file containing the syllable data
    file_in = open(filename, 'r')
    
    # Read the first line
    line = file_in.readline()

    while (line != ''):
        # Read each line of syllable data
        line = file_in.readline()
        data = line.split()
        
        # Only consider words that were in our learning set
        if len(data) > 0 and data[0] in word_to_int_map:
            normal_syllables = []
            end_syllables = []
            
            # Add possible syllables (digits) and possible ending syllables 
            # ('E' followed by a digit) to the appropriate lists
            for i in range(1, len(data)):
                if data[i].isdigit():
                    normal_syllables.append(int(data[i]))
                elif data[i][0] == 'E' and data[i][1:].isdigit():
                    end_syllables.append(int(data[i][1:]))
            
            syllables = {'normal': normal_syllables, 'end': end_syllables}
            syllable_dictionary[word_to_int_map[data[0]]] = syllables
    
    # Close the file containing the syllable data
    file_in.close()
    
    return syllable_dictionary


def main():
    # Parse the sonnets
    quatrain_lines, volta_lines, couplet_lines, word_to_int_map, int_to_word_map, rhymes = parse_file("data\\shakespeare.txt")
    all_lines = quatrain_lines + volta_lines + couplet_lines
    
    # Parse the syllable data
    syllable_dictionary = parse_syllables("data\\Syllable_dictionary.txt", word_to_int_map)
    
    # Train an HMM and generate a 14-line sonnet
    hmm10 = HMM.unsupervised_HMM(all_lines, 10, 100)
    hmm10.save("hmm10.txt")
    #hmm10 = HMM.load("hmm10.txt")
    
    # Generate three quatrains
    for i in range(3):
        # Select rhyming words for this quatrain
        sample_rhymes = random.sample(rhymes, 2)
        rhyme_a = random.sample(sample_rhymes[0], 2)
        rhyme_b = random.sample(sample_rhymes[1], 2)
        initials = [rhyme_a[0], rhyme_b[0], rhyme_a[1], rhyme_b[1]]
        
        # Generate each line backwards using the rhyming word as the initial word
        for i in range(4):
            emission, states = hmm10.generate_line(10, syllable_dictionary, reverse=True, initial=initials[i])
            line = [int_to_word_map[i] for i in emission]
            print(' '.join(line).capitalize())
            
    # Generate one couplet
    rhyme_c = random.sample(random.sample(rhymes, 1)[0], 2)
    for i in range(2):
        emission, states = hmm10.generate_line(10, syllable_dictionary, reverse=True, initial=rhyme_c[i])
        line = [int_to_word_map[i] for i in emission]
        print('  ' + ' '.join(line).capitalize())
        
    # Visualize the matrices and the states of the HMM
    HMM_helper.visualize_sparsities(hmm10, O_max_cols=100, O_vmax=1)
    HMM_helper.states_to_wordclouds(hmm10, word_to_int_map)
    
    
if __name__ == "__main__":
    main()
