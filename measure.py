class Measure:

    def __init__(self, measure, num_staves):

        self.measure = measure
        self.num_staves = num_staves

    def parse_attributes(self, attributes):
        
        sequence = ''
        skip = 0

        # Iterate through all attributes
        for attribute in attributes:

            if attribute.tag == 'key':
                # Sharps are positive, flats neg
                #sharps = int(attribute[0].text) > 0
                #sequence += 'keySignature-' + str(abs(int(attribute[0].text))) + ('sharps' if sharps else 'flats') + ' '
                sequence += 'keySignature-' + self.num_sharps_flats_to_key(int(attribute[0].text)) + ' '


            elif attribute.tag == 'time':
                # Top and bottom num
                sequence += 'timeSignature-' + attribute[0].text + '/' + attribute[1].text + ' '

            elif attribute.tag == 'clef':
                # Clef and line (add this first)
                sequence = 'clef-' + attribute[0].text + attribute[1].text + ' ' + sequence

            elif attribute.tag == 'measure-style':
                # Look for multi-rest/repeats
                s, skip = self.parse_measure_style(attribute)
                sequence += s

        sequence = [sequence for i in range(self.num_staves)]
        return sequence, skip
    
    def parse_note(self, note):

        sequence = ['' for x in range(self.num_staves)]

        # Check that note is printed
        if 'print-object' in note.attrib and note.attrib['print-object'] == 'no':
            return sequence

        # Get staff, voice, dot of note
        staff, voice, has_dot = 0, 1, False
        for e in note:
            if e.tag == 'staff':
                staff = int(e.text) - 1
            #if e.tag == 'voice':
            #    voice = int(e.text)
            if e.tag == 'dot':
                has_dot = True

        # Iterate through all elements in note obj
        for elem in note:

            if elem.tag == 'pitch':
                pitch, alter, octave = '', '', ''
                for e in elem:
                    if e.tag == 'step':
                        pitch = e.text
                    elif e.tag == 'alter':
                        alter = '#' if int(e.text) > 0 else 'b'
                    elif e.tag == 'octave':
                        octave = e.text
                # Step and octave
                sequence[staff] += 'note-' + pitch + alter + octave

            if elem.tag == 'rest':
                # Check if measure rest or has a type
                if 'measure' in elem.attrib and elem.attrib['measure'] == 'yes':
                    sequence[staff] += 'rest_' + 'measure' + ' '#'-v' + str(voice) + ' '
                else:
                    sequence[staff] += 'rest' 

            elif elem.tag == 'type':
                # Length of note
                dot = '. ' if has_dot else ' '
                duration = 'sixteenth' if elem.text == '16th' else \
                           'thirty_second' if elem.text == '32nd' else \
                            elem.text
                sequence[staff] += '_' + duration + dot#'-v' + str(voice) + ' '

            elif elem.tag == 'chord':
                # Indicate if chord
                sequence[staff] += '+ '

            elif elem.tag == 'notations':
                # Articulations
                sequence[staff] += self.parse_notations(elem)

        return sequence

    def parse_direction(self, direction):

        sequence = ['' for x in range(self.num_staves)]

        # Get staff of note
        staff = 0
        for e in direction:
            if e.tag == 'staff':
                staff = int(e.text) - 1

        # Iterate through all elements in direction obj
        for elem in direction:

            if elem.tag == 'direction-type':

                if elem[0].tag == 'dynamics':
                    sequence[staff] += elem[0][0].tag + '-dynamic' + ' '

                if elem[0].tag == 'words' and elem[0].text is not None:
                    sequence[staff] += elem[0].text + '-dynamic' + ' '

            elif elem.tag == 'sound':

                if 'tempo' in elem.attrib:
                    pass # don't show tempo for now
                    #sequence[staff] += elem.attrib['tempo'] + '-tempo' + ' '

        return sequence

    def parse_notations(self, notation):

        sequence = ''

        # Iterate through all elements in notation obj
        for n in notation:

            if n.tag == 'tied':
                sequence += 'tie-' +  n.attrib['type'] + ' '

            elif n.tag == 'slur':
                sequence += 'slur-' +  n.attrib['type'] + ' '
        
            elif n.tag == 'articulations':
                # Go through all articulations
                for articulation in n:
                    sequence += articulation.tag + ' '

        return sequence

    def parse_measure_style(self, style):

        sequence = ''
        skip = 0

        # Iterate through all elements in notation obj
        for s in style:

            if s.tag == 'multiple-rest':
                sequence += 'multirest-' + s.text + ' '
                skip = int(s.text)

        return sequence, skip

    def num_sharps_flats_to_key(self, num):

        """
        Converts num sharps/flats to key
        """

        mapping = {7: 'C#M', 6: 'F#M', 5: 'BM', 4: 'EM',
                   3: 'AM', 2: 'DM', 1: 'GM', 0: 'CM',
                   -1: 'FM', -2: 'BbM', -3: 'EbM', -4: 'AbM',
                   -5: 'DbM', -6: 'GbM', -7: 'CbM'}

        return mapping[num]