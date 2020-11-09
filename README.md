# musicxml-to-sequence
Takes input MusicXML files and generates sequence (.txt) of symbols. Also compares sequences (.txt) genereated by the following and determines if they are equal. To be used in OMR research to measure accuracy of commerical software/academic papers for any kind of music score (i.e monophonic or polyphonic).

## MusicXML (.xml) to Sequence (.txt)

Parses MusicXML with a single part and generates a text file with the sequence of each staff separated. After each note, the voice is indicated, and each measure is also indicated. See below for an example  
```
Sequence staff # 0
|0| 7sharps 4/4 G2 G5half-v1 B5half-v1 E4quarter-v2 F4quarter-v2 G4quarter-v2 A4quarter-v2 |1| G5half-v1 B5half-v1 E4quarter-v2 + B4quarter-v2 F4quarter-v2 + B4quarter-v2 G4quarter-v2 A4quarter-v2 + C5quarter-v2 |2| restmeasure-v1|3| restmeasure-v1
```

### TODO
- [ ] More testing with different articulations
- [ ] Potential standard separation of voices 
- [ ] Expand to work for multiple parts in a MusicXML

## Sequence (.txt) Comparison

Compares two sequences generated and determines if they are equivalent. Slurs and ties are treated as the same.

### TODO
- [ ] Make robust to different orders of articulation
- [ ] How to handle different voice numbers, but same notes
- [ ] Think about which staves dynamic/tempo/other should go to
