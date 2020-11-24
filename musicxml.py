"""
Contains class that converts MusicXML to a sequence
by parsing it
"""

import sys
import xml.etree.ElementTree as ET 

from measure import Measure

class MusicXML():

    def __init__(self, input_file=None, output_file=None, gt_file=None):

        """
        Stores MusicXML file passed in 
        """

        self.input_file = input_file
        self.output_file = output_file
        self.gt_file = gt_file

        #print('Created object: ', musicxml_file)

    def write_sequence(self):

        """
        Outputs the sequence of this MusicXML object
        to the output file
        """

        staves = self.get_sequence()

        with open(self.output_file, 'w') as out_file:

            print()
            out_file.write('')
            for num, staff in enumerate(staves):
                #out_file.write(('Sequence staff # ' + str(num) + '\n' + staff + '\n'))
                out_file.write((staff + '\n'))
                print('Sequence staff #', num)
                print(staff,'\n')
            out_file.write('')
            print()

            out_file.close()

    def get_sequence(self):

        """
        Parses MusicXML file and returns sequence
        (list of symbols for each staff)
        """

        with open(self.input_file, 'r') as input_file:

            tree = ET.parse(input_file)
            root = tree.getroot()

            #print('Root:', root)

            # TODO: Expand to handle multiple parts
            part_list_idx = -1
            part_idx = -1

            # Find <part-list> and <part> element indexes
            for i, child in enumerate(root):
                if child.tag == 'part-list':
                    part_list_idx = i
                elif child.tag == 'part':
                    part_idx = i

            # Check for bad MusicXML
            if part_list_idx == -1 or part_idx == -1:
                print('MusicXML file:', self.input_file,' missing <part-list> or <part>')
                return ['']
                sys.exit(0)

            # Get number of staves in the MusicXML
            num_staves = 1
            for e in root[part_idx][0][0]:
                if e.tag == 'staff-layout':
                    num_staves = int(e.attrib['number'])
            staves = ['' for x in range(num_staves)]

            # Read each measure
            r_iter = iter(root[part_idx])
            for i, measure in enumerate(r_iter):

                # Gets the symbol sequence of each staff in measure
                measure_staves, skip = self.read_measure(measure, num_staves, i)

                for j in range(num_staves):
                    staves[j] += measure_staves[j]

                for j in range(skip-1):
                    next(r_iter)

        return staves

    def read_measure(self, measure, num_staves, num):

        """
        Reads a measure and returns a sequence of symbols
        """

        m = Measure(measure, num_staves)

        staves = ['' for x in range(num_staves)]
        skip = 0

        # Iterate through all elements in measure
        for elem in measure:

            r = ['' for x in range(num_staves)]

            if elem.tag == 'attributes':
                # Skip is number of measures to skip for multirest
                r,skip = m.parse_attributes(elem)
            elif elem.tag == 'note':
                r = m.parse_note(elem)
            elif elem.tag == 'direction':
                r = m.parse_direction(elem)

            for i in range(num_staves):
                staves[i] += r[i]

            # Skip rest of measure if multirest
            if skip > 0:
                break

        # Add measure separator to each staff
        for i in range(num_staves):
            #staves[i] = '|' + str(num) + '| ' + staves[i] 
            #staves[i] = 'barline ' + staves[i] 
            staves[i] = staves[i] + 'barline '

        return staves, skip

    def check_correctness(self):

        """
        Compares output and groundtruth files and returns
        1 if correct, 0 otherwise
        """

        with open(self.output_file, 'r') as output_file, open(self.gt_file, 'r') as gt_file:

            out_lines = output_file.readlines()
            gt_lines = gt_file.readlines()

            # Check for inequality
            if len(out_lines) != len(gt_lines):
                return 0

            # Check for inequality
            for i in range(len(out_lines)):
                out_split = out_lines[i].split()
                gt_split = gt_lines[i].split()

                if len(out_split) != len(gt_split):
                    return 0

                for j in range(len(out_split)):
                    # Treat slur and tie as equivalent
                    if out_split[j] != gt_split[j] and\
                        ('slur' not in out_split[j] and 'tie' not in out_split[j]) and\
                           ('slur' not in gt_split[j] and 'tie' not in gt_split[j]):
                        return 0

        return 1

    def edit_distance(self):

        """
        Compares output and groundtruth files and returns
        1 if correct, 0 otherwise
        """

        edit_dist = 0

        with open(self.output_file, 'r') as output_file, open(self.gt_file, 'r') as gt_file:

            out_lines = output_file.readlines()
            gt_lines = gt_file.readlines()

            num_symbols = 0

            # Go through all lines
            for i in range(len(out_lines)):
                # Skip comparing sequence staff line
                if 'Sequence staff' in gt_lines[i]:
                    continue

                out_split = out_lines[i].split()
                gt_split = gt_lines[i].split()

                num_symbols += len(gt_split)    # for calculating symbol error rate

                _a = [symbol for symbol in out_split if symbol != '\n' and symbol != -1]
                _b = [symbol for symbol in gt_split if symbol != '\n' and symbol != -1]

                ed = self.levenshtein(_a,_b)
                
                # Account for barline at end (don't use when checking CRNN output)
                #if ed == 1 and out_split[-1] == 'barline' and gt_split[-1] != 'barline':
                #    ed = 0
                
                edit_dist += ed
                
                staff_num = (i + 1) // 2
                print('Edit dist (staff #%d): %d' % (staff_num, ed))

                '''
                if len(out_split) != len(gt_split):
                    return 0

                for j in range(len(out_split)):
                    # Treat slur and tie as equivalent
                    if out_split[j] != gt_split[j] and\
                        ('slur' not in out_split[j] and 'tie' not in out_split[j]) and\
                           ('slur' not in gt_split[j] and 'tie' not in gt_split[j]):
                        return 0
                '''

        return edit_dist, num_symbols

    def levenshtein(self,a,b):
        "Computes the Levenshtein distance between a and b."
        n, m = len(a), len(b)

        #print(a)
        #print(b)

        if n > m:
            a,b = b,a
            n,m = m,n

        current = range(n+1)
        for i in range(1,m+1):
            previous, current = current, [i]+[0]*n
            for j in range(1,n+1):
                add, delete = previous[j]+1, current[j-1]+1
                change = previous[j-1]
                if a[j-1] != b[i-1]:
                    change = change + 1
                current[j] = min(add, delete, change)

        return current[n]

    def compare(self):

        """
        Compares xml file to corresponding ground truth
        xml
        """

        with open(self.musicxml_file, 'r') as musicxml_file, open(self.gt_file, 'r') as gt_file:

            input_tree = ET.parse(musicxml_file)
            input_root = input_tree.getroot()

            truth_tree = ET.parse(gt_file)
            truth_root = truth_tree.getroot()

            print('Input Root:', input_root)

            part_list_idx = -1
            part_idx = -1

            # Find <part-list> and <part> element indexes
            for i, child in enumerate(input_root):
                if child.tag == 'part-list':
                    part_list_idx = i
                elif child.tag == 'part':
                    part_idx = i

            # Check for bad MusicXML
            if part_list_idx == -1 or part_idx == -1:
                print('MusicXML file:', self.musicxml_file,' missing <part-list> or <part>')
                sys.exit(0)

            # Compare <part-list> elements
            #part_list_matching = self.compare_elements(input_root[part_list_idx], truth_root[part_list_idx])
            #print('Part list idx:', part_list_idx)

            # Compare <part> elements
            parts_matching = self.compare_elements(input_root[part_idx], truth_root[part_idx])
            print('Part idx:', part_idx)

    def compare_elements(self, elem1, elem2):

        """
        Recursively goes through XML elements and compares them 
        for equality (ignores attributes)
        """

        if elem1.tag == elem2.tag and elem1.tag == 'print':
            return True

        print('ELem1 Len:', len(elem1))
        print(elem1)
        print('Elem2 Len:', len(elem2))
        print(elem2)

        # If no children for both, this element is equal if same text
        if len(elem1) == 0:
            print('Child element found')
            return len(elem2) == 0 and elem1.tag == elem2.tag\
                   and elem1.text == elem2.text

        # Check for different number of children
        if len(elem1) != len(elem2) and 'details' not in elem1[-1].tag:
            print('Diff number children', elem1[-1].tag)
            return False

        matching = True
        for i, e1 in enumerate(elem1):
            matching = matching and self.compare_elements(e1, elem2[i])

        print('Matching status:', matching)
        return matching
