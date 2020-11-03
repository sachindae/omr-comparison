"""
Main file to run generator
"""

import os
import argparse
from musicxml import MusicXML

if __name__ == '__main__':

    """
    Command line args:

    -input <input directory with MusicXMLS>
    -output <output directory to write to>
    """

    # Parse command line arguments for input/output directories
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', dest='input', type=str, required=True, help='Path to the input directory with MusicXMLs.')
    parser.add_argument('-output', dest='output', type=str, required=True, help='Path to the output directory to write sequences.')
    args = parser.parse_args()

    print('Input dir (MusicXMLs):', args.input)
    print('Output dir (Sequences):',args.input)

    # Go through all inputs generating output sequences
    for i, file_name in enumerate(os.listdir(args.input)):

        # Ignore non .xml files
        if not file_name.endswith('.xml'):
            continue

        print('Input file', i+1, ':', file_name)

        # Create an object with the MusicXML file
        file_path = os.path.join(args.input, file_name)
        musicxml_obj = MusicXML(file_path)

        # Generate output sequence
        sequence = musicxml_obj.get_sequence()