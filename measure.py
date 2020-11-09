class Measure:

    def __init__(self, measure, num_staves):

        self.measure = measure
        self.num_staves = num_staves

    def parse_attributes(self, attributes):
        
        sequence = ''

        # Iterate through all attributes
        for attribute in attributes:

            if attribute.tag == 'key':
                # Sharps are positive, flats neg
                sharps = int(attribute[0].text) > 0
                sequence += str(abs(int(attribute[0].text))) + ('sharps' if sharps else 'flats') + ' '

            elif attribute.tag == 'time':
                # Top and bottom num
                sequence += attribute[0].text + '/' + attribute[1].text + ' '

            elif attribute.tag == 'clef':
                # Clef and line
                sequence += attribute[0].text + attribute[1].text + ' '

        sequence = [sequence for i in range(self.num_staves)]
        return sequence
    
    def parse_note(self, note):

        sequence = ['' for x in range(self.num_staves)]

        # Check that note is printed
        if 'print-object' in note.attrib and note.attrib['print-object'] == 'no':
            return sequence

        # Get staff and voice of note
        staff, voice = 0, 1
        for e in note:
            if e.tag == 'staff':
                staff = int(e.text) - 1
            if e.tag == 'voice':
                voice = int(e.text)

        # Iterate through all elements in note obj
        for elem in note:

            if elem.tag == 'pitch':
                # Step and octave
                sequence[staff] += elem[0].text + elem[-1].text

            if elem.tag == 'rest':
                # Check if measure rest or has a type
                if 'measure' in elem.attrib and elem.attrib['measure'] == 'yes':
                    sequence[staff] += 'rest' + 'measure' + '-v' + str(voice)
                else:
                    sequence[staff] += 'rest' 

            elif elem.tag == 'type':
                # Length of note
                sequence[staff] += elem.text + '-v' + str(voice) + ' '

            elif elem.tag == 'chord':
                # Length of note
                sequence[staff] += ' + '

            elif elem.tag == 'notations':
                # Length of note
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
                    sequence[staff] += elem.attrib['tempo'] + '-tempo' + ' '

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