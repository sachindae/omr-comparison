"""
Contains class that converts MusicXML to a sequence
by parsing it
"""

import xml.etree.ElementTree as ET 

class MusicXML():

    def __init__(self, musicxml_file):

        """
        Stores MusicXML file passed in 
        """

        self.musicxml_file = musicxml_file

        print('Created object: ', musicxml_file)

    def get_sequence(self):

        """
        Parses MusicXML file and returns sequence
        """

        with open(self.musicxml_file, 'r') as musicxml_file:

            tree = ET.parse(musicxml_file)

            print(tree.getroot())