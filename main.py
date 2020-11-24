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
    -truth <ground truth directory to compare to>
    -c (compares input to ground truth)
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

        total_ed = 0
        total_symbols = 0

        # Go through all outputs comparing to corresponding groundtruths
        for i, file_name in enumerate(os.listdir(args.output)):

            # Ignore non .txt/.semantic files
            if not file_name.endswith('.txt') and not file_name.endswith('.semantic'):
                continue

            print('Output file', total_compared+1, ':', file_name)

            # Create a MusicXML object for comparing ground truth
            output_path = os.path.join(args.output, file_name)
            gt_path = os.path.join(args.truth, file_name)
            musicxml_obj = MusicXML(output_file=output_path, gt_file=gt_path)

            # Compare to ground truth
            #total_matching += musicxml_obj.check_correctness()
            total_compared += 1
            edit_dist, num_symbols = musicxml_obj.edit_distance()
            total_matching += (edit_dist == 0)

            total_ed += edit_dist
            total_symbols += num_symbols

        print('Accuracy:', (total_matching / total_compared))
        print('Symbol Error Rate:', (total_ed / total_symbols))

    else:               # Read inputs and generate output sequences

        file_num = 0

        # Go through all inputs generating output sequences
        for i, file_name in enumerate(os.listdir(args.input)):

            # Ignore non .xml files
            if not file_name.endswith('.xml'):
                continue

            print('Input file', file_num+1, ':', file_name)

            # Create a MusicXML object for generating sequences
            input_path = os.path.join(args.input, file_name)
            output_path = os.path.join(args.output, ''.join(file_name.split('.')[:-1]) + '.semantic')
            musicxml_obj = MusicXML(input_file=input_path, output_file=output_path)

            # Generate output sequence
            musicxml_obj.write_sequence()

            file_num += 1