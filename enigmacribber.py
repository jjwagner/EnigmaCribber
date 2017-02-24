# 
# Enigma Cribber
#
# To use, edit this script below by entering
# the ciphertext, the expected crib text,
# and the rotor order.
#
# The ciphertext and crib text MUST be the
# same length.
#
# This simulates the three-rotor Enigma I
# machine, with rotors I, II and III, and
# reflector B.
#


#
# Helper functions
#

def bound(input):
    # Wraps offsets around the wheel.
    # i.e. Z + 1 = A
    #      B - 5 = W
    if input > 25:
       return (input - 26)
    elif input < 0:
       return (input + 26)
    else:
       return input


def rotor_RtoL (rotor, index, rotorpos):
    # Compute the rotor offsets for signals
    # flowing from right (input/plugboard)
    # to left (reflector).
    #
    position = bound(index + rotorpos)
    return bound(rotor[position] - rotorpos)

    
def rotor_LtoR (rotor, index, rotorpos):
    # Compute the rotor offsets for signals
    # flowing from left (reflector) to 
    # right (input/plugboard)
    #
    position = bound(index + rotorpos)
    for idx in range(26):
        if rotor[idx] == position:
            return bound(idx - rotorpos)


def rotors_advance(LeftRotorPos, MiddleRotorPos, RightRotorPos, LeftRotor, MiddleRotor, RightRotor):
    # Advance three rotors (args), paying
    # attention to the notch placement
    # and double-stepping at the appropriate 
    # times.
    #
    
    # Pull the notch positions off the ends
    # of the wheel arrays
    LeftRotorNotch = LeftRotor[26]
    MiddleRotorNotch = MiddleRotor[26]
    RightRotorNotch = RightRotor[26]

    advanceRandM = False
    advanceMandL = False
    
    # If any of the pawls will fall in a
    # notch, set a flag.
    if(RightRotorPos == RightRotorNotch):
        advanceRandM = True
    if(MiddleRotorPos == MiddleRotorNotch):
        advanceMandL = True

    # the rightmost rotor always advances
    RightRotorPos = bound(RightRotorPos + 1)
    
    # the middle one advances if its pawl falls
    # in the rightmost wheel's notch, or if 
    # the left wheel's pawl falls in the middle
    # wheel's notch. Take care of the first
    # condition here
    if(advanceRandM and not advanceMandL):
        MiddleRotorPos = bound(MiddleRotorPos + 1)
    
    # If the left wheel's pawl falls in the
    # middle wheel's notch, advance them both.
    if(advanceMandL):
        MiddleRotorPos = bound(MiddleRotorPos + 1)
        LeftRotorPos = bound(LeftRotorPos + 1)

    rotors_advance.RightRotorPos = RightRotorPos
    rotors_advance.MiddleRotorPos = MiddleRotorPos
    rotors_advance.LeftRotorPos = LeftRotorPos


def Compute(stepcount, signalin, RotorL, RotorM, RotorR, RotorLPos, RotorMPos, RotorRPos, Reflector):
    # Automate stepping the rotors and
    # computing the substitutions back
    # and forth across the wheels and 
    # reflector
    #
    for step in range(stepcount):
       rotors_advance(RotorLPos, RotorMPos, RotorRPos, RotorL, RotorM, RotorR)
       RotorRPos = rotors_advance.RightRotorPos
       RotorMPos = rotors_advance.MiddleRotorPos
       RotorLPos = rotors_advance.LeftRotorPos

    # finished advancing. save rotor positions
    # for the function caller
    Compute.RotorRPos = RotorRPos
    Compute.RotorMPos = RotorMPos
    Compute.RotorLPos = RotorLPos
    
    # compute offsets from input/plugboard to reflector
    RotorROutL = rotor_RtoL(RotorR, signalin, RotorRPos)
    RotorMOutL = rotor_RtoL(RotorM, RotorROutL, RotorMPos)
    RotorLOutL = rotor_RtoL(RotorL, RotorMOutL, RotorLPos)
    ReflectorOutR  = rotor_RtoL(Reflector, RotorLOutL, 0)

    # compute offsets from reflector back to the input/plugboard
    RotorLOutR = rotor_LtoR(RotorL, ReflectorOutR, RotorLPos)
    RotorMOutR = rotor_LtoR(RotorM, RotorLOutR, RotorMPos)
    RotorROutR = rotor_LtoR(RotorR, RotorMOutR, RotorRPos)

    return RotorROutR

#
# Constants and variables
#

#         0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25
alpha  = "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"
alphastr = "abcdefghijklmnopqrstuvwxyz"

#rotor definitions. the notch position is encoded in element 26
rotorI   = 4,10,12,5,11,6,3,16,21,25,13,19,14,22,24,7,23,20,18,15,0,8,1,17,2,9, 16
rotorII  = 0,9,3,10,18,8,17,20,23,1,11,7,22,19,12,2,16,6,25,13,15,24,5,21,14,4, 4
rotorIII = 1,3,5,7,9,11,2,15,17,19,23,21,25,13,24,4,8,22,6,0,10,12,20,18,16,14, 21
reflecB  = 24,17,20,7,16,18,11,3,15,23,13,6,14,10,12,8,4,1,5,25,2,22,21,9,0,19

# Set ciphertext and crib text, and rotor order
ciphertext = "YJBDELCZ"
cribtext   = "THECACHE"
rotorL = rotorI
rotorM = rotorII
rotorR = rotorIII
reflector = reflecB

CandidateRotorPositions = []
ReducedRotorPositions = []


# Create initial list of candidate positions 

for rotorLpos in range(26):
    for rotorMpos in range(26):
        for rotorRpos in range(26):
            CandidateRotorPositions.append([rotorLpos, rotorMpos, rotorRpos])


for ch in range(len(ciphertext)):
    
    cipherchar = alphastr.index(ciphertext[ch].lower())
    target = alphastr.index(cribtext[ch].lower())
    #print(cipherchar, alpha[cipherchar], target, alpha[target])

    total = 0
    count = 0

    for rotorPositions in range(len(CandidateRotorPositions)):
        count += 1
        
        rotorLstart = CandidateRotorPositions[rotorPositions][0]
        rotorMstart = CandidateRotorPositions[rotorPositions][1]
        rotorRstart = CandidateRotorPositions[rotorPositions][2]
        
        #print("Run ", ch, " Starting positions: \t", alpha[rotorLstart], alpha[rotorMstart], alpha[rotorRstart])

        if(Compute(ch + 1, cipherchar, rotorL, rotorM, rotorR, rotorLstart, rotorMstart, rotorRstart, reflector) == target):
            #print("Found! starting positions: ", alpha[rotorLstart], alpha[rotorMstart], alpha[rotorRstart])
            #print("       ending positions: ", alpha[Compute.RotorLPos], alpha[Compute.RotorMPos], alpha[Compute.RotorRPos])
            ReducedRotorPositions.append([rotorLstart, rotorMstart, rotorRstart])
            total += 1

    print("Character ", ch, "\tPositions tested:", count, "\tStarting Positions Found:", total)
    CandidateRotorPositions = ReducedRotorPositions
    ReducedRotorPositions = []

for rotorPositions in CandidateRotorPositions:
    print("Possible starting rotor configuration: ", alpha[rotorPositions[0]], alpha[rotorPositions[1]], alpha[rotorPositions[2]])

