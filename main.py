"""
Main file to run generator
"""

import sys
import os
import argparse
from musicxml import MusicXML

def write_output(file_list):

    """
    Writes file list of mispredictions to an output file
    """

    with open('mispredictions.txt', 'w') as f:

        for name,dist in file_list:
            f.write(name.split('.')[0] + '         edit dist: ' + str(dist) + '\n')
            #f.write(name.split('.')[0] + '.png' + '\n')
        f.close()

        print('File written:','mispredictions.txt')

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
    #parser.add_argument('-conf', dest='conflict', type=str, required='-c' in sys.argv, help='Path to the ground truth directory to compare inputs.')
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
        off = 0
        off1 = 0
        mispredictions = []
        bar_diff = 0

        wrong_symbols = dict()
        change_symbols = dict()

        misaligned_preds = []

        #with open(args.conflict, 'r') as f:
        #    prior_files = set(f.read().splitlines())
        #    prior_corr = set()

        # Go through all outputs comparing to corresponding groundtruths
        for i, file_name in enumerate(os.listdir(args.output)):

            # Ignore non .txt/.semantic/agnostic files
            if not file_name.endswith('.txt') and not file_name.endswith('.semantic') and not file_name.endswith('.agnostic'):
                continue

            #print('Output file', total_compared+1, ':', file_name)

            # Create a MusicXML object for comparing ground truth
            output_path = os.path.join(args.output, file_name)
            '''
            if file_name.split('-')[1].startswith('0'):
                if file_name.split('-')[1].startswith('00'):
                    file_name = file_name.split('-')[0] + '-' + file_name.split('-')[1][2:]
                else:
                    file_name = file_name.split('-')[0] + '-' + file_name.split('-')[1][1:]
            '''
            gt_path = os.path.join(args.truth, file_name)
            musicxml_obj = MusicXML(output_file=output_path, gt_file=gt_path)

            # Compare to ground truth
            #total_matching += musicxml_obj.check_correctness()
            
            edit_dist, num_symbols, bd, misaligned = musicxml_obj.edit_distance()

            # Skip bad files
            if edit_dist == -1:
                continue

            off1 += edit_dist == 1
            off += edit_dist > 0
            total_matching += (edit_dist == 0)
            total_compared += 1
            bar_diff += bd

            if edit_dist >= 1:
                #if file_name.split('.')[0] in prior_files:
                #    prior_corr.add(file_name.split('.')[0])

                # Add to list to write to file
                mispredictions.append((file_name,edit_dist))
                
                # Analyze the error
                
                sym = musicxml_obj.get_wrong_symbol()
                #print(output_path)
                #print('Wrong sym:',sym)
                change = sym[1] != 'del' and sym[1] != 'add'
                if sym[0] in wrong_symbols:
                    wrong_symbols[sym[0]] += 1   
                else: 
                    wrong_symbols[sym[0]] = 1

                if change:
                    if sym[0] in change_symbols:
                        change_symbols[sym[0]].append(sym[1])
                    else:
                        change_symbols[sym[0]] = [sym[1]]
                
                

            if misaligned:
                misaligned_preds.append(file_name)

            print(edit_dist, num_symbols)

            total_ed += edit_dist
            total_symbols += num_symbols

        write_output(mispredictions)
        print('Off:', off)
        print('Off by 1:', off1)
        print('Barline diff:',bar_diff)
        print('Accuracy:', (total_matching / total_compared))
        print('Num correct:',total_matching,'Num total:', total_compared)
        print('Symbol Error Rate:', (total_ed / total_symbols))
        print('Total ed:', total_ed)
        print('Total sym:', total_symbols)
        #print('Prior Predictions %d / %d' % (len(prior_corr), len(prior_files)))

        print('Wrong symbols')
        for k,v in sorted(wrong_symbols.items(),reverse=True, key=lambda item: item[1]):
            print(k,' ',v)
        #print(wrong_symbols)

        print('Change symbols')
        for k,v in change_symbols.items():
            print(k,'--',v)
        #print(change_symbols)

        print('Misaligned preds: ', len(misaligned_preds))
        for p in misaligned_preds:
            print(p)

    else:               # Read inputs and generate output sequences

        file_num = 0

        # Go through all inputs generating output sequences
        for i, file_name in enumerate(os.listdir(args.input)):

            # Ignore non .xml files
            if not file_name.endswith('.musicxml'):
                continue

            print('Input file', file_num+1, ':', file_name)

            # Create a MusicXML object for generating sequences
            input_path = os.path.join(args.input, file_name)
            output_path = os.path.join(args.output, ''.join(file_name.split('.')[:-1]) + '.semantic')
            musicxml_obj = MusicXML(input_file=input_path, output_file=output_path)

            # Generate output sequence
            try:
                musicxml_obj.write_sequence()
            except UnicodeDecodeError: # Ignore bad MusicXML
                pass

            file_num += 1