from __future__ import print_function
# In order to use the print() function in python 2.X

import numpy as np
import math

DEBUG = False


def printMatrix(M, str1, str2):

    P = []
    for i in range(len(M)+1):
        P.append([])
        for j in range(len(M[0])+1):
            P[i].append('')

    for i in range(2, len(P[0])):
        P[0][i] = str2[i-2]

    for i in range(2, len(P)):
        P[i][0] = str1[i-2]

    for i in range(1, len(P)):
        for j in range(1, len(P[i])):
            P[i][j] = M[i-1][j-1]

    for i in range(len(P)):
        print()
        for j in range(len(P[0])):
            if i == 0 and j ==0:
                print("       ", end="")
            if i == 1 and j ==0:
                print("    ", end="")
            if len(str(P[i][j])) > 0 and str(P[i][j])[0] != '-':
                print(" ", end="")
            if len(str(P[i][j])) == 1:
                print("  ", end="") 
            print(P[i][j], end=" ")

    print()
    print()


def match():
    return 1

def mismatch(a, b):
    return -1

def indel():
    return -1

def compare(a,b):
    if a == b:
        return match()
    else:
        return mismatch(a, b)

def getDistanceDictionaryFromFile(file):
    '''
    Open a dist file and construct the proper dictionary
    '''
    f=open(file, "r")
    contents = f.read()
    # delete the comments if there is
    if contents.rfind('#') != -1:
        contents = contents[contents.rfind('#'):]
    M = contents.split("\n")

    # Find how many spaces there is at the begining
    d = 0
    for i in range(len(M[0])):
        if M[i] != ' ':
            d = i+1
            break
    if M[0][0] == "#":
        del M[0]

    alpha = M[0][d:].split("  ")[1:]
    dist = {}

    for i in range(1, len(M)-1):
        dist[M[i][0]] = M[i][3:].replace("  ", " ")

    for key in dist:
        temp = dist[key].split(" ")
        dist[key] = {}
        for i in range(len(alpha)):
            # In order to have integers in the dict
            dist[key][alpha[i]] = int(temp[i])

    return dist

def getDist(a, b, matrix = "Linear", bonus=5, malus=-3, dist = ''):

    if matrix == "Linear":
        return (a==b)*bonus + (not a==b)*malus
    else:
        return dist[a][b]




def myNeedleman(str1, str2, matrix='atiam-fpa_alpha.dist', gap_open=-5, gap_extend=-5, bonus=5, malus=-3):

    dist = {}
    if matrix != "Linear":
        # We get the distance dictionary from the file
        try:
            dist = getDistanceDictionaryFromFile(matrix)
        except FileNotFoundError :
            try:
                # If the one provided is not found we use the default one
                dist = getDistanceDictionaryFromFile('atiam-fpa_alpha.dist')
            except FileNotFoundError :
                raise FileNotFoundError("No dist file was found.")

            print("The dist file you provided (", matrix,") was not found, we will use the default one.")


    # Initialize matrix
    M = np.ones((len(str1)+1, len(str2)+1))

    M[0][0] = 0
    M[0][1] = gap_open
    M[1][0] = gap_open

    for i in range(2, len(M[0])):
        M[0][i] = M[0][i-1] + gap_extend

    for i in range(2, len(M)):
        M[i][0] = M[i-1][0] + gap_extend

    for i in range(1, len(M)):
        for j in range(1, len(M[i])):

            # in order to see if we already opened a gap
            if i > 1:
                top_opened = (M[i-1][j] == M[i-2][j] + gap_extend) or (M[i-1][j] == M[i-2][j] + (gap_open)) or \
                              (M[i-1][j] == M[i-1][j-1] + gap_extend) or (M[i-1][j] == M[i-1][j-1] + (gap_open))
            else: 
                top_opened = (M[i-1][j] == M[i-1][j-1] + gap_extend) or (M[i-1][j] == M[i-1][j-1] + (gap_open))

            if j > 1:
                left_opened = (M[i][j-1] == M[i][j-2] + gap_extend) or (M[i][j-1] == M[i][j-2] + (gap_open)) or \
                          (M[i][j-1] == M[i-1][j-1] + gap_extend) or (M[i][j-1] == M[i-1][j-1] + (gap_open))
            else:   
                left_opened = (M[i][j-1] == M[i-1][j-1] + gap_extend) or (M[i][j-1] == M[i-1][j-1] + (gap_open))

            # Filling matrix with the recursive formula

            M[i][j] = max(M[i-1][j] + top_opened*gap_extend + (not top_opened)*gap_open, \
                          M[i][j-1] + left_opened*gap_extend + (not left_opened)*gap_open, \
                          M[i-1][j-1] + getDist(str1[i-1], str2[j-1], matrix =matrix, dist = dist))


            if DEBUG:
                print("Position:", i,j,'__',str2[j-1], "vs", str1[i-1], ": max", M[i-1][j] + top_opened*gap_extend + (not top_opened)*gap_open, \
                      M[i][j-1] + left_opened*gap_extend + (not left_opened)*gap_open, (M[i-1][j-1]) + dist[str1[i-1]][str2[j-1]],\
                      "=", max(M[i-1][j] + top_opened*gap_extend + (not top_opened)*gap_open, M[i][j-1] + left_opened*gap_extend + (not left_opened)*gap_open, M[i-1][j-1]) + getDist(str1[i-1], str2[j-1], matrix =matrix, dist = dist))
    if DEBUG:
        printMatrix(M, str1, str2)

    # We construct the alignement from the matrix
    i,j = (len(M)-1, len(M[0])-1)

    retA = ""
    retB = ""
    posA = len(str1) -1
    posB = len(str2) -1

    while (i,j) != (0, 0):

        if M[i][j] == M[i][j-1] + gap_extend or M[i][j] == M[i][j-1] + gap_open :
            retB = str2[posB] + retB
            posB -= 1
            retA = '-' + retA
            j -= 1

        elif M[i][j] == M[i-1][j] + gap_extend or M[i][j] == M[i-1][j] + gap_open:
            retA = str1[posA] + retA
            posA -= 1
            retB = '-' + retB
            i -= 1

        elif M[i][j] == M[i-1][j-1] + getDist(str1[i-1], str2[j-1], matrix =matrix, dist = dist):
            retA = str1[posA] + retA
            posA -= 1
            retB = str2[posB] + retB
            posB -= 1
            i -= 1
            j -= 1  

        else:
            return (str1, str2, 0)

    if DEBUG:
        print(retA)
        print(retB)
        print("SCORE:", int(M[-1][-1]))

    return (retA, retB, int(M[-1][-1]))

# in order to improve computation
def checkFirstSimilarities(a, b):
    dic1 = {}
    for elem in a+b:
        dic1[elem] = 0

    for elem in a:
        dic1[elem] += 1

    dic2 = {}
    for elem in a+b:
        dic2[elem] = 0

    for elem in b:
        dic2[elem] += 1


    similarity = 0

    for elem in dic1:
        similarity += (dic1[elem] - dic2[elem])**2

    similarity = float(similarity) / min(len(a), len(b))

    return similarity


def musicNameDist(a, b):

    # We define all atom that are the same
    Table = [["n", "number", "numero", "num", "no.","no"], \
             ["1", "un", "one", "premier"], \
             ["2", "deux", "two", "second"], \
             ["3", "trois", "three", "toisieme"], \
             ["4", "quatre", "four", "quatrieme"], \
             ["5", "cinq", "five", "cinquieme"], \
             ["6", "six", "six", "sixieme"], \
             ["7", "sept", "seven", "septieme"], \
             ["8", "huit", "eight", "huitieme"], \
             ["9", "neuf", "nine", "neuvieme"], \
             ["10", "dix", "ten", "dixieme"], \
             ["11", "onze", "eleven", "onzieme"], \
             ["12", "douze", "twelve", "douzieme"], \
             ["13", "treize", "thirteen", "treizieme"], \
             ["14", "quatorze", "fourteen", "quatorzieme"], \
             ["15", "quize", "fiveteen", "quinzieme"], \
             ["16", "seize", "sixteen", "seizieme"], \
             ["17", "dix-sept", "seventeen", "dix-spetieme"], \
             ["18", "dix-hui", "eighteen", "dix-huitieme"], \
             ["19", "dix-neuf", "nineteen", "dix-neuvieme"], \
             ["20", "vingt", "twenty", "vingtieme"], \
             ["mineur", "minor", "mino"], \
             ["majeur", "major", "majo"], \
             ["c", "do", "ut"],\
             ["c#", "do diese", "do#"], \
             ["d", "re"], \
             ["d#", "re diese", "re#"], \
             ["e", "mi"], \
             ["f", "fa"], \
             ["f#", "fa dise", "fa#"], \
             ["g", "sol"], \
             ["g#", "sol diese", "sol#"], \
             ["a", "la"], \
             ["a#", "la diese", "la#"], \
             ["b", "si"], \
             ["bb", "si bemol", "sib"], \
             ["eb", "mi bemol", "mib"], \
             ["ab", "la bemol", "lab"], \
             ["db", "re bemol", "reb"], \
             ["gb", "sol bemol", "solb"], \
             ["cb", "do bemol", "dob"], \
             ["fb", "fa bemol", "fab"]]

    # For digit we have to be clear equal or not equal
    if a.isdigit():
        if b.isdigit() and int(a) == int(b):
            return 1
        else:
            return 0

    if b.isdigit():
        if a.isdigit() and int(a) == int(b):
            return 1
        else:
            return 0

    # if we see a match in the table return 1
    for elem in Table:
        if a in elem:
            if b in elem:
                return 1

    # else we rely on Needleman for the taping mistakes
    if len(a)>0 and len(b)>0 and abs(len(a)-len(b))<3 and checkFirstSimilarities(a, b) < 0.5 and \
        myNeedleman(a, b, matrix= "Linear", gap_extend=-2, gap_open=-2)[2] > 0.9*min(len(a), len(b))*5 - 0.4*min(len(a), len(b)):
        return 1

    return 0

def musicNameMatching(name1, name2):

    # we process the replacement for the flat and sharp and put the names in lower case

    # Sharp
    name1 = name1.replace("#", " diese").lower()
    name2 = name2.replace("#", " diese").lower()

    # Flat
    flat = [ ["bb", "si bemol", "sib"], \
             ["eb", "mi bemol", "mib"], \
             ["ab", "la bemol", "lab"], \
             ["db", "re bemol", "reb"], \
             ["gb", "sol bemol", "solb"], \
             ["cb", "do bemol", "dob"], \
             ["fb", "fa bemol", "fab"]]
    for elem in flat:
        name1 = name1.replace(elem[0], elem[1]).replace(elem[2], elem[1])
        name2 = name2.replace(elem[0], elem[1]).replace(elem[2], elem[1])


    # we split the names and replace some sybols
    name1 = name1.replace("(","").replace(")","").replace("_", " ").replace(".", " ").split(" ")
    name2 = name2.replace("(","").replace(")","").replace("_", " ").replace(".", " ").split(" ")

    temp = []
    for elem in name1:
        if elem != "":
            temp.append(elem)
    name1 = temp

    temp = []
    for elem in name2:
        if elem != "":
            temp.append(elem)
    name2 = temp


    # Case catalog Bach-Werke-Verzeichnis
    for i in range(len(name1)-1):
        if name1[i] == "bwv":
            name1 = ["bwv "+ name1[i+1]]
            break

    for i in range(len(name2)-1):
        if name2[i] == "bwv":
            name2 = ["bwv "+ name2[i+1]]
            break

    # Case catalog Kochel
    for i in range(len(name1)-1):
        if name1[i] == "kv":
            name1 = ["kv "+ name1[i+1]]
            break

    for i in range(len(name2)-1):
        if name2[i] == "kv":
            name2 = ["kv "+ name2[i+1]]
            break


    score = 0
    # We assume that there is no missing word
    for word in name1:
        for word2 in name2:
            if musicNameDist(word, word2) == 1:
                score += 1
                break

    if score >= min(len(name1), len(name2)):
        return True
    return False

def getListRepresentation(dic):
    L = []
    for key in dic:
        L.append(dic[key])
    return L

def compareList(a, b):
    if len(a) != len(b):
        return False

    for i in range(len(a)):
        if str(list(a[i])) != str(list(b[i])):
            return False
            break
    return True

def compareMidiFiles(a, b):

    a = getListRepresentation(a)
    b = getListRepresentation(b)

    tobreak = False
    k = 0

    # 2 loops in order to detect if the voices are not in the same order in the dictionary
    for elem1 in a:
        for elem2 in b:
            if compareList(elem1, elem2):
                k +=1
                break       

    if k >= len(a):
        return True
    return False

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

def quantify(piece, quantization):
    all_parts = {}
    k = 0
    for part in piece.parts:
        try:
            track_name = part[0].bestName()
        except AttributeError:
            track_name = str(k)
        cur_part = get_pianoroll_part(part, quantization);
        if (cur_part.shape[1] > 0):
            all_parts[track_name] = cur_part;
        k +=1
    return all_parts

def getMinDuration(p):
    minDuration  = 10.0 
    for n in p.flat.notes:
        if n.duration.quarterLength < minDuration and n.duration.quarterLength > 0:
            minDuration = n.duration.quarterLength
    return minDuration

'''
The alforithm compute the meaned quadratic loss between a non quantized and a quantized representation of the piece
More the error is worth is the file
'''
def getQuality(p):
    # we quantisize with two different levels (a super-large one and a smaller depends on the smallest duration)

    q1 = 1/getMinDuration(p)
    q2 = 512

    quantified = quantify(p, q1)
    unquantified = quantify(p, q2)

    L_q = []
    L_u = []

    # we store position of all notes in a list
    for key in quantified:
        for elem in quantified[key]:
            rest = True
            for t in range(len(elem)):
                if elem[t] != 0:
                    if rest:
                        L_q.append(t/q1)
                    rest = False
                else:
                    rest = True
    for key in unquantified:
        for elem in unquantified[key]:
            rest = True
            for t in range(len(elem)):
                if elem[t] != 0:
                    if rest:
                        L_u.append(t/q2)
                    rest = False
                else:
                    rest = True

    # In order to be sure that we have all notes in the right order
    L_q.sort() 
    L_u.sort()

    ERROR = 0
    # We add 1 in order to not sqare number less than 1
    for i in range(len(L_q)):
        ERROR += (L_q[i]- L_u[i] + 1)**2

    ERROR = ERROR / len(L_u) -1

    return ERROR

def printAlign(s1, s2, size = 70):
    for i in range(len(s1)//size):
        for e in range(size):
            print(s1[i*size+e], end="")
        print()
        for e in range(size):
            print(s2[i*size+e], end="")
        print("\n")

def alignMidi(p1, p2):
    p1 = quantify(p1, 16)
    p2 = quantify(p2, 16)
    keylist1 = p1.keys()
    keylist2 = p2.keys()
    P1 = []
    P2 = []
    for part in range(min(len(keylist1), len(keylist2))):
        P1.append([])
        P2.append([])
        for i in range(len(p1[keylist1[part]])):
            if "".join(p1[keylist1[part]][i].astype(int).astype(str)) == "".join(p2[keylist2[part]][i].astype(int).astype(str)):
                P1[part].append("".join(p1[keylist1[part]][i].astype(int).astype(str)))
                P2[part].append("".join(p1[keylist1[part]][i].astype(int).astype(str)))
            else:

                N = myNeedleman("".join(p1[keylist1[part]][i].astype(int).astype(str)), "".join(p2[keylist2[part]][i].astype(int).astype(str)), matrix="Linear", gap_open=-4, gap_extend=-2)
                P1[part].append(N[0])
                P2[part].append(N[1])


    for i in range(len(P1)):
        print("New Part: \n")
        for j in range(len(P1[i])):
            print("New Slice: \n")
            printAlign(P1[i][j], P2[i][j])







