#!/usr/bin/env python

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
    
    # Open the file containing the poems
    file_in = open(filename, 'r')

    quatrain_lines = []
    volta_lines = []
    couplet_lines = []

    # Read the first line
    line = file_in.readline()

    while (line != ''):
        # Beginning of a new poem
        if line.strip().isdigit():
            # First two quatrains
            for i in range(8):
                line = file_in.readline()
                quatrain_lines.append(parse_line(line))
                
            # Volta (third quatrain)
            for i in range(4):
                line = file_in.readline()
                volta_lines.append(parse_line(line))
                
            # Couplet
            for i in range(2):
                line = file_in.readline()
                couplet_lines.append(parse_line(line))

        # Burn through "unaffiliated" lines
        else:
            line = file_in.readline()
    
    # Close the file containing the poems
    file_in.close()

    # Return the lists of lines
    return (quatrain_lines, volta_lines, couplet_lines)


def main():
    """ Do some testing here! """
    
    # Let's test the functions!
    quatrain_lines, volta_lines, couplet_lines = parse_file("shakespeare.txt")

    # Print the quatrain lines
    print(quatrain_lines)

    # Print the number of lines in each category
    print("Number of quatrain lines:", len(quatrain_lines))
    print("Number of volta lines:", len(volta_lines))
    print("Number of couplet lines:", len(couplet_lines))

    
if __name__ == "__main__":
    main()
