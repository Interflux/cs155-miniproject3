"""
Filename:     preprocess.py
Version:      1.0
Date:         2018/3/9

Description:  Handles preprocessing of data for CS 155's third miniproject.

Author(s):    Dennis Lam, Garret Sullivan
Organization: California Institute of Technology
"""

import HMM

def parse_line(line):
    """ Parses a line of the sonnets. """
    
    # Remove unwanted characters
    for char in line:
        if char in ",.!?;:":
            line = line.replace(char, '')

    # Convert to all-lowercase
    line = line.lower()
    
    # Store as a list of words
    words = line.split()
    
    # Return the line as a list of words
    return words


def parse_file(filename):
    """ Parses the "shakespeare.txt" file containing the sonnets. """
    
    # Exclude these sonnets because they don't follow the typical pattern
    excluded_sonnets = [99, 126]
    
    quatrain_lines = []
    volta_lines = []
    couplet_lines = []
    
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

    # Return the lists of lines
    return (quatrain_lines, volta_lines, couplet_lines, obs_word_to_int, obs_int_to_word)


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
    """ Do some testing here! """
    
    # Parse the sonnets
    quatrain_lines, volta_lines, couplet_lines, word_to_int_map, int_to_word_map = parse_file("data\\shakespeare.txt")
    all_lines = quatrain_lines + volta_lines + couplet_lines
    
    # Parse the syllable data
    syllable_dictionary = parse_syllables("data\\Syllable_dictionary.txt", word_to_int_map)
    
    '''
    # Print the converted lines
    converted_lines = []
    for all_line in all_lines:
        converted_line = []
        for word in all_line:
            converted_line.append(word_map[word])
        converted_lines.append(converted_line)
    
    # Print the number of lines in each category
    print("Number of quatrain lines:", len(quatrain_lines))
    print("Number of volta lines:", len(volta_lines))
    print("Number of couplet lines:", len(couplet_lines))
    '''
    
    # Train an HMM and generate a 14-line sonnet
    hmm10 = HMM.unsupervised_HMM(all_lines, 10, 100)
    for i in range(14):
        emission, states = hmm10.generate_line(10, syllable_dictionary)
        line = [int_to_word_map[i] for i in emission]
        print(' '.join(line).capitalize())
    
if __name__ == "__main__":
    main()
