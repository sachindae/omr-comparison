"""
Main file to run generator
"""

import sys
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
    parser.add_argument('-c', dest='compare', action="store_true", default=False, help='Choose if comparing outputs to groundtruth')
    parser.add_argument('-input', dest='input', type=str, required='-c' not in sys.argv, help='Path to the input directory with MusicXMLs.')
    parser.add_argument('-output', dest='output', type=str, required=True, help='Path to the output directory to write sequences.')
    parser.add_argument('-truth', dest='truth', type=str, required='-c' in sys.argv, help='Path to the ground truth directory to compare inputs.')
    args = parser.parse_args()

    print('Comparing:', args.compare)
    print('Input dir (MusicXMLs):', args.input)
    print('Output dir (Sequences):', args.output)
    print('Ground truth dir (Sequences):',args.truth)

    if args.compare:    # Compare outputs to ground truth

        total_matching = 0
        total_compared = 0

        # Go through all outputs comparing to corresponding groundtruths
        for i, file_name in enumerate(os.listdir(args.output)):

            # Ignore non .xml files
            if not file_name.endswith('.txt'):
                continue

            print('Output file', i+1, ':', file_name)

            # Create an object with the txt file
            output_path = os.path.join(args.output, file_name)
            gt_path = os.path.join(args.truth, file_name)
            musicxml_obj = MusicXML(output_file=output_path, gt_file=gt_path)

            # Compare to ground truth
            total_matching += musicxml_obj.check_correctness()
            total_compared += 1

        print('Accuracy:', (total_matching / total_compared))

    else:               # Read inputs and generate output sequences

        # Go through all inputs generating output sequences
        for i, file_name in enumerate(os.listdir(args.input)):

            # Ignore non .xml files
            if not file_name.endswith('.xml'):
                continue

            print('Input file', i+1, ':', file_name)

            # Create an object with the MusicXML file
            input_path = os.path.join(args.input, file_name)
            output_path = os.path.join(args.output, ''.join(file_name.split('.')[:-1]) + '.txt')
            #gt_path = os.path.join(args.truth, file_name)
            musicxml_obj = MusicXML(input_file=input_path, output_file=output_path)

            # Generate output sequence
            musicxml_obj.write_sequence()