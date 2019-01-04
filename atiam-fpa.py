"""
This script defines the overall exercise for ATIAM structure course

 - Use this as a baseline script
 - You are authorized to define other files for functions
 - Write a (small) report document (PDF) explaining your approach
 - All your files should be packed in a zip file named
     [ATIAM][FpA2017]FirstName_LastName.zip

@author: esling
"""

# Define mode (keep it on False, this is just for my generative part)
DEV_MODE=False
# Basic set of imports (here you can see if everything passes)
import os
import pickle
import string
from functions import *

#%% Here collect the whole set of tracks
if DEV_MODE:
    # Define MIDI extension
    midExt = ['mid', 'midi', 'MID', 'MIDI']
    # Root directory
    root = '/Users/esling/Research/Coding/aciditeam/orchestral-db/data'
    database = {}
    composers = []
    composers_tracks = {}
    tracks = []
    # List composers first
    for item in os.listdir(root):
        if os.path.isdir(os.path.join(root, item)):
            composers.append(item)
    print('Found ' + str(len(composers)) + ' composers.')
    prev_letter = ''
    # now parse tracks
    for comp in composers:
        # Print advance
        if (comp[0] != prev_letter):
            prev_letter = comp[0]
            print('   - Composers starting with ' + prev_letter)
        # Check each sub-folder
        for item in os.listdir(os.path.join(root, comp)):
            cur_path = os.path.join(os.path.join(root, comp), item)
            if os.path.isdir(cur_path):
                for files in os.listdir(cur_path):
                    if (os.path.splitext(files)[1][1:] in midExt):
                        tracks.append(item)
                        if comp in composers_tracks.keys():
                            composers_tracks[comp].append(item)
                        else:
                            composers_tracks[comp] = [item]
    print('Found ' + str(len(tracks)) + ' tracks.')
    midi_database = {'composers':composers, 'composers_tracks':composers_tracks}
    pickle.dump(midi_database, file('atiam-fpa.pkl', 'w'))
else:
    midi_database = pickle.load(file('atiam-fpa.pkl'))
    composers = midi_database['composers']
    composers_tracks = midi_database['composers_tracks']

#%% 
"""
 
PART 1 - Symbolic alignments and simple text dictionnaries

In this part, we will use our knowledge on computer structures to solve a very 
well-known problem of string alignement. Hence, this part is split between
  1 - Implement a string alignment 
  2 - Try to apply this to a collection of classical music pieces names
  3 - Develop your own more adapted procedure to have a matching inside large set
  
The set of classical music pieces is provided in the atiam-fpa.pkl file, which
is already loaded at this point of the script and contain two structures
    - composers         = Array of all composers in the database
    - composers_tracks  = Hashtable of tracks for a given composer
    
Some examples of the content of these structures

composers[23] => 'Abela, Placido'
composers[1210]  => 'Beethoven, Ludwig van'

composers_tracks['Abela, Placido'] => ['Ave Maria(Meditation on Prelude No. 1 by J.S.Bach)']
composers_tracks['Beethoven, Ludwig van'] => ['"Ode to Joy"  (Arrang.)', '10 National Airs with Variations, Op.107 ', ...]

composers_tracks['Beethoven, Ludwig van'][0] => '"Ode to Joy"  (Arrang.)'

"""
    
#%% Question 1 - Reimplementing text alignment 

'''

Q-1.1 Here perform your Needleman-Wunsch (NW) implementation.
    - You can find the definition of the basic NW here
    https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm
    - First start by implementing the basic gap costs
    - Then extend to complete affine gap costs
    - Remember to rely on a user-defined matrix for symbols distance

'''


    # c.f. functions.py

myNeedleman("CEELECANTH", "PELICAN", matrix= 'atiam-fpa_alpha.dist', gap_open=-5, gap_extend=-2)


# Reference code for testing
import nwalign as nw
print("myNeedleman")
print(myNeedleman("CEELECANTH", "PELICAN", matrix= 'atiam-fpa_alpha.dist', gap_open=-1, gap_extend=-1))
print("Nwalign")
aligned = nw.global_align("CEELECANTH", "PELICAN", matrix='atiam-fpa_alpha.dist')
score = nw.score_alignment(aligned[0], aligned[1], gap_open=-1, gap_extend=-1, matrix='atiam-fpa_alpha.dist')
print('Results for basic gap costs (linear)')
print(aligned[0])
print(aligned[1])
print('Score : ' + str(score))

print("myNeedleman")
print(myNeedleman("CEELECANTH", "PELICAN", matrix= 'atiam-fpa_alpha.dist', gap_open=-5, gap_extend=-2))
print("Nwalign")
aligned = nw.global_align("CEELECANTH", "PELICAN", matrix='atiam-fpa_alpha.dist', gap_open=-5, gap_extend=-2)
score = nw.score_alignment(aligned[0], aligned[1], gap_open=-5, gap_extend=-2, matrix='atiam-fpa_alpha.dist')
print('Results for affine gap costs')
print(aligned[0])
print(aligned[1])
print('Score : ' + str(score))

#%% Question 2 - Applying this to a collection of musical scores

import operator
# In order to easily sort dictionaries
from tqdm import tqdm
# for avancement process

# Here an example: print all composers
#for composer,tracks in sorted(composers_tracks.items()):
#    if (len(tracks) >= 10):
#        print(composer + ' : ' + str(len(tracks)) + ' tracks.')
        
'''

Q-2.1 Sort the collection of composers by decreasing number of tracks

'''

def getComposersSorted(composers_tracks, toPrint=False):
    dico = {}
    for composer,tracks in composers_tracks.items():
        if (len(tracks) >= 10):
            dico[composer] = len(tracks)

    ComposersSorted = [composer for (composer, n) in sorted(dico.items(), key=operator.itemgetter(1), reverse=True)]

    if toPrint:
        for elem in ComposersSorted:
            print(elem + ' -> ' + str(dico[elem]) + " tracks")

    return ComposersSorted

CS = getComposersSorted(composers_tracks, toPrint = True)

'''

Q-2.2 Apply the NW algorithm between all tracks of each composer
    * For each track of a composer, compare to all remaining tracks of the same composer
    * Establish a cut criterion (what is the relevant similarity level ?) to only print relevant matches
    * Propose a set of matching tracks and save it through Pickle
    
'''
if not os.path.isfile("Data/matches1.p"):

    dico = {}
    for composer,tracks in composers_tracks.items():
        if (len(tracks) >= 10):
            dico[composer] = list(set(tracks))

    matches = []
    #for composer in dico:
    for composer in tqdm(dico):
        for i in tqdm(range(len(dico[composer]))):
            # we start at i+1 in order to not compute several time the same combination
            for j in range(i+1, len(dico[composer])):
                if abs(len(dico[composer][i]) - len(dico[composer][j])) < 3 and checkFirstSimilarities(dico[composer][i], dico[composer][j]) < 0.5 and myNeedleman(dico[composer][i], dico[composer][j], matrix="Linear")[2] > 0.8*min(len(dico[composer][i]), len(dico[composer][j]))*5 - 0.6*min(len(dico[composer][i]), len(dico[composer][j])):
                    matches.append((dico[composer][i], dico[composer][j]))

    pickle.dump(matches, open( "Data/matches1.p", "wb" ) )          

'''

Q-2.3 Extend your previous code so that it can compare
    * A given track to all tracks of all composers (full database)
    * You should see that the time taken is untractable (computational explosion)
    * Propose a method to avoid such a huge amount of computation
    * Establish a cut criterion (what is relevant similarity)
    * Propose a set of matching tracks and save it through Pickle
    
'''

if not os.path.isfile("Data/matches2.p"):

    tracks = []
    for c,t in tqdm(composers_tracks.items()):
        if (len(t) >= 10):
            tracks.extend(set(t))
    tracks = list(set(tracks))

    tracks.sort(key=lambda v: len(v))

    # precompute the sizes (gain a little bit of computations)
    SIZES = []
    for elem in tracks:
        SIZES.append(len(elem))

    matches = []

    for i in tqdm(range(len(tracks))):
        # we start at i+1 in order to not compute several time the same combination
        for j in range(i+1, len(tracks)):
            if SIZES[j] - SIZES[i] >= 3:
                break
            elif checkFirstSimilarities(tracks[i], tracks[j]) < 0.5 and myNeedleman(tracks[i], tracks[j], matrix="Linear", \
                    gap_open=-4, gap_extend=-4)[2] > 0.8*min(len(tracks[i]), len(tracks[j]))*5 - 0.6*min(len(tracks[i]), len(tracks[j])):
                matches.append((tracks[i], tracks[j]))

    pickle.dump(matches, open( "Data/matches2.p", "wb" ) )          


#%% Question 3 - Musical matching

'''

Q-3.1 Extending to a true musical name matching
    * You might have seen from the previous results that
        - Purely string matching on classical music names is not the best approach
        - This mostly comes from the fact that the importance of symbols is not the same
        - For instance 
            "Symphony for orchestra in D minor"
            "Symphony for orchestra in E minor"
          Looks extremely close but the key is the most important symbol
    * Start by exploring the collection for well-known composers, what do you see ?
    * Propose a new name matching algorithm adapted to classical music piece names
        - Can be based on a rule-based system
        - Can be a pre-processing for symbol finding and then an adapted weight matrix
        - Can be a local-alignement procedure
        (These are only given as indicative ideas ...)
    * Implement this new comparison procedure adapted to classical music piece names
    * Re-run your previous results (Q-2.2 and Q-2.3) with this procedure
    
'''

# This algorithm (musicNameMatching) allows to compare classical music names, it uses a formal analysis and the knowledge of the composers catalog
# The sources are in the file Functions.py and the algo is explained in the pdf


# You can see that it's working pretty well thanks to these examples
print(musicNameMatching("le Prelude Numero un", "prlude n 2"), "False")
print(musicNameMatching("le Prelude Numero un", "prlude n 1"), "True")
print(musicNameMatching("BWV 345 premier prelude", "prlude n 1 (bwv 345)"), "True")
print(musicNameMatching("BWV 345", "BWV 15"), "False")
print(musicNameMatching("KV 345 premier prelude", "prlude n 1 (kv 345)"), "True")
print(musicNameMatching("KV 345", "KV 15"), "False")


print("Computing myMatches1")
if not os.path.isfile("Data/myMatches1.p"):

    dico = {}
    for composer,tracks in composers_tracks.items():
        if (len(tracks) >= 10):
            dico[composer] = list(set(tracks))

    matches = []
    #for composer in dico:
    for composer in tqdm(dico):
        for i in tqdm(range(len(dico[composer]))):
            # we start at i+1 in order to not compute several time the same combination
            for j in range(i+1, len(dico[composer])):
                if len(dico[composer][j]) - len(dico[composer][i]) >= 3:
                    break
                elif musicNameMatching(dico[composer][i], dico[composer][j]):
                    matches.append((dico[composer][i], dico[composer][j]))

    pickle.dump(matches, open( "Data/myMatches1.p", "wb" ) )    

    dico = {}
    for composer,tracks in composers_tracks.items():
        if (len(tracks) >= 10):
            dico[composer] = list(set(tracks))


# just here in order to proceed quick check
if False:
    dico = {}
    for composer,tracks in composers_tracks.items():
        if (len(tracks) >= 10):
            dico[composer] = list(set(tracks))
    matches = []
    #for composer in dico:
    composer = list(dico.keys())[2]
    for i in tqdm(range(len(dico[composer]))):
        # we start at i+1 in order to not compute several time the same combination
        for j in range(i+1, len(dico[composer])):
            if len(dico[composer][j]) - len(dico[composer][i]) >= 3:
                break
            elif musicNameMatching(dico[composer][i], dico[composer][j]):
                matches.append((dico[composer][i], dico[composer][j]))

    print(matches)


print("Computing myMatches2")
if not os.path.isfile("Data/myMatches2.p"):

    tracks = []
    for c,t in tqdm(composers_tracks.items()):
        if (len(t) >= 10):
            tracks.extend(set(t))
    tracks = list(set(tracks))

    tracks.sort(key=lambda v: len(v))

    # precompute the sizes (gain a little bit of computations)
    SIZES = []
    for elem in tracks:
        SIZES.append(len(elem))

    matches = []

    for i in tqdm(range(len(tracks))):
        # we start at i+1 in order to not compute several time the same combination
        for j in range(i+1, len(tracks)):
            if SIZES[j] - SIZES[i] >= 3:
                break
            elif musicNameMatching(tracks[i], tracks[j]):
                matches.append((tracks[i], tracks[j]))

    pickle.dump(matches, open( "Data/myMatches2.p", "wb" ) ) 


# Example of creating a dummy matrix
if DEV_MODE:
    dist = open('atiam-fpa_alpha.dist', 'w')
    dist.write('   ')
    for m1 in string.ascii_uppercase:
        dist.write(m1)
        if (m1 < 'Z'):
            dist.write('  ')
    dist.write('\n')
    for m1 in string.ascii_uppercase:
        dist.write(m1 + '  ')
        for m2 in string.ascii_uppercase:
            if (m2 == m1):
                dist.write('5  ')
            else:
                dist.write('-3  ')
        dist.write('\n')
    dist.close()

#%% 
"""
 
PART 2 - Alignments between MIDI files and error-detection

Interestingly the problem of string alignment can be extended to the more global 
problem of aligning any series of symbolic information (vectors). Therefore,
we can see that the natural extension of this problem is to align any sequence
of symbolic information.

This definition matches very neatly to the alignement of two musical scores 
that can then be used as symbolic similarity between music, or score following.
However, this requires several key enhancements to the previous approach. 
Furthermore, MIDI files gathered on the web are usually of poor quality and 
require to be checked. Hence, here you will
    1 - Learn how to read and watch MIDI files
    2 - Explore their properties to perform some quality checking
    3 - Extend alignment to symbolic score alignement
    
To fasten the pace of your musical analysis, we will rely on the excellent 
Music21 library, which provides all sorts of musicological analysis and 
properties over symbolic scores. You will need to really perform this part
to go and read the documentation of this library online

"""

#%% Question 4 - Importing and plotting MIDI files

import math
import numpy as np
from music21 import converter, graph
import matplotlib.pyplot as plt

def get_start_time(el,measure_offset,quantization):
    if (el.offset is not None) and (el.measureNumber in measure_offset):
        return int(math.ceil(((measure_offset[el.measureNumber] or 0) + el.offset)*quantization))
    # Else, no time defined for this element and the functino return None

def get_end_time(el,measure_offset,quantization):
    if (el.offset is not None) and (el.measureNumber in measure_offset):
        return int(math.ceil(((measure_offset[el.measureNumber] or 0) + el.offset + el.duration.quarterLength)*quantization))
    # Else, no time defined for this element and the functino return None
    
def get_pianoroll_part(part,quantization):
    # Get the measure offsets
    measure_offset = {None:0}
    for el in part.recurse(classFilter=('Measure')):
        measure_offset[el.measureNumber] = el.offset
    # Get the duration of the part
    duration_max = 0
    for el in part.recurse(classFilter=('Note','Rest')):
        t_end = get_end_time(el,measure_offset,quantization)
        if(t_end>duration_max):
            duration_max=t_end
    # Get the pitch and offset+duration

    piano_roll_part = np.zeros((128,int(math.ceil(duration_max))))
    for this_note in part.recurse(classFilter=('Note')):
        note_start = get_start_time(this_note,measure_offset,quantization)
        note_end = get_end_time(this_note,measure_offset,quantization)
        piano_roll_part[this_note.midi,note_start:note_end] = 1
    return piano_roll_part

# Here we provide a MIDI import function
def importMIDI(f):
    piece = converter.parseFile(f)
    all_parts = {}
    k =0
    for part in piece.parts:
        print(part)
        try:
            track_name = part[0].bestName()
        except AttributeError:
            track_name = str(k)
        cur_part = get_pianoroll_part(part, 16);
        if (cur_part.shape[1] > 0):
            all_parts[track_name] = cur_part;
        k +=1
    print('Returning')
    return piece, all_parts

'''

Q-4.1 Import and plot some MIDI files

Based on the provided MIDI files (random subset of Beethoven tracks), try
to import, plot and compare different files

'''

# Here a small example that only works on my computer
if DEV_MODE:
    composer = 'Beethoven, Ludwig van'
    track_title = composers_tracks[composer][0]
    track_path = root + '/' + composer + '/' + track_title + '/' + track_title + '.mid'
    piece, all_parts = importMIDI(track_path)
    piece.plot()



file = "atiam-fpa/beethoven_2.mid"
bet2 = importMIDI(file)
bet2[0].plot()

file2 = "atiam-fpa/beethoven_7.mid"
bet7 = importMIDI(file2)
bet7[0].plot()

file3 = "atiam-fpa/beethoven_1.mid"
bet1 = importMIDI(file3)
bet1[0].plot()

# In order to compare file we can just compare the stringed piano-roll representation
bet1_list = getListRepresentation(bet1[1])
bet2_list = getListRepresentation(bet2[1])
bet7_list = getListRepresentation(bet7[1])


print "Are beethoven_2 and beethoven_7 the same?", compareMidiFiles(bet2[1], bet7[1])
print "Are beethoven_2 and beethoven_1 the same?", compareMidiFiles(bet2[1], bet1[1])

# We can see here that beethoven_2 and beethoven_7 are actually the same but not beethoven_2 and beethoven_1


'''

Q-4.2 Exploring MIDI properties

The Music21 library propose a lot of properties directly on the piece element,
but we also provide separately a dictionary containing for each part a matrix
representation (pianoroll) of the corresponding notes (without dynamics).
    - By relying on Music21 documentation (http://web.mit.edu/music21/doc/)
        * Explore various musicology properties proposed by the library
        * Check which could be used to assess the quality of MIDI files

'''

#piece, all_parts = bet7
# Here a few properties that can be plotted ...
#piece.plot('scatter', 'quarterLength', 'pitch')
#piece.plot('scatterweighted', 'pitch', 'quarterLength')
#piece.plot('histogram', 'pitchClass')

piece, all_parts = bet2

# Those ones can show some information about the quality (i.e. if the quantification is precise)
piece.plot('horizontalbar', 'pitchClass')

p = graph.plot.HistogramQuarterLength(piece)

p.run() # with defaults and proper configuration, will open graph

# Or even simply this one in which we can zoom into
for key in all_parts:
    plt.imshow(all_parts[key]);
plt.colorbar()
plt.show()


#%% Question 5 - Performing automatic MIDI quality checking

'''

Q-5.1 Automatic evaluation of a MIDI file quality

One of the most pervasive problem with MIDI scores is that a large part of the
files that you can find on the internet are of rather low quality.
Based on your exploration in the previous questions and your own intuition,
    - Propose an automatic procedure that could evaluate the quality of a MIDI file.
    - Test how this could be used on a whole set of files

'''

'''
The algorithm computes the meaned quadratic loss between a non quantized and a quantized representation of the piece.
Greater is the error, worth is the file quality. The cut value depends on the usage, but 1 seems to be a nice one.
'''
print("Error of bet1:",getQuality(bet1[0])) # ERROR 0.5
print("Error of bet7:",getQuality(bet7[0])) # ERROR 24
print("Error of bet2:",getQuality(bet2[0])) # ERROR 24

#%% Question 6 - (BONUS) Extending symbolic matching to MIDI alignment

'''

Q-6.1 Extending your alignment algorithm to MIDI scores

As explained earlier, our alignment algorithm can work with any set of symbols,
which of course include even complex scores. The whole trick here is to see
that the "distance matrix" previously used could simply be replaced by a
"distance function", which can represent the similarity between any elements
    - Propose a fit distance measures between two slices of pianorolls
    - Modify your previous algorithm so that it can use your distance
    - Modify the algorithm so that it can work with MIDI files
    - Apply your algorithm to sets of MIDI files

'''

file = "atiam-fpa/beethoven_test.mid"
piece1,_ = importMIDI(file)

file = "atiam-fpa/beethoven_test2.mid"
piece2,_ = importMIDI(file)

'''
The algorithm performs Needleman on each slice of the piece (matching 1 vs 0 is very simple, so we use a linear distance).
It align each slice separatly and merge all.
'''
# Returns two unchanged strings
alignMidi(piece1, piece1)


# Appreciate the nice alignement
alignMidi(piece1, piece2)



#%% Just for preparing a random set of MIDIs to help you out
if DEV_MODE:
    nb_track = 0;
    for val in np.random.randint(0, len(composers_tracks['Beethoven, Ludwig van']), 30):
        cur_track = composers_tracks['Beethoven, Ludwig van'][val]
        track_path = root + '/Beethoven, Ludwig van/' + cur_track + '/' + cur_track + '.mid'
        os.system('cp ' + track_path + ' atiam-fpa/beethoven_' + str(nb_track) + '.mid')
        print('cp "' + track_path + '" atiam-fpa/beethoven_' + str(nb_track) + '.mid')
        nb_track = nb_track + 1






