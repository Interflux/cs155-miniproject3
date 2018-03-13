"""
Filename:     preprocess_rnn.py
Version:      1.0
Date:         2018/3/12

Description:  Handles preprocessing of data for the RNN portion of CS 155's
              third miniproject.

Author(s):    Dennis Lam, Garret Sullivan
Organization: California Institute of Technology

"""

def remove_number_headings(filename):
    """
    Removes the number headings and blank lines from the "shakespeare.txt"
    file.

    """
    # Exclude these sonnets because they don't follow the typical pattern
    excluded_sonnets = [99, 126]
    
    # Open the file containing the poems
    file_in = open(filename, 'r')

    # Open the file to contain
    file_out = open("sonnets_unlabeled.txt", 'w')

    # Read the first line
    line = file_in.readline()

    while (line != ''):
        # Beginning of a new poem
        if line.strip().isdigit() and int(line.strip()) not in excluded_sonnets:
            for i in range(14):
                # Read a line
                line = file_in.readline()
                
                # Write it to the file
                file_out.write(line)

        # Burn through "unaffiliated" lines
        else:
            line = file_in.readline()
            
    # Close the file containing the poems
    file_in.close()
    
    # Close the output files
    file_out.close()

    
def generate_input_files(filename):
    """
    Generates appropriate input files from the "shakespeare.txt" file
    containing the sonnets.

    """
    
    # Exclude these sonnets because they don't follow the typical pattern
    excluded_sonnets = [99, 126]
    
    # Open the file containing the poems
    file_in = open(filename, 'r')

    # Open the file to contain
    file_out_quatrain = open("quatrain_lines.txt", 'w')
    file_out_volta = open("volta_lines.txt", 'w')
    file_out_couplet = open("couplet_lines.txt", 'w')

    # Read the first line
    line = file_in.readline()

    while (line != ''):
        # Beginning of a new poem
        if line.strip().isdigit() and int(line.strip()) not in excluded_sonnets:
            for i in range(14):

                # Read a line and remove the newline character
                # line = file_in.readline().strip()
                # line = line.rstrip("\n\r")

                # Read a line
                line = file_in.readline()
                
                # Write the line to the appropriate file
                if i in range(0, 8):
                    # First two quatrains
                    file_out_quatrain.write(line)
                elif i in range (8, 12):
                    # Volta (third quatrain)
                    file_out_volta.write(line)
                elif i in range(12, 14):
                    # Couplet
                    file_out_couplet.write(line)

        # Burn through "unaffiliated" lines
        else:
            line = file_in.readline()
            
    # Close the file containing the poems
    file_in.close()
    
    # Close the output files
    file_out_quatrain.close()
    file_out_volta.close()
    file_out_couplet.close()


def main():
    
    # Generate input files
    remove_number_headings("shakespeare.txt")


if __name__ == "__main__":
    main()
