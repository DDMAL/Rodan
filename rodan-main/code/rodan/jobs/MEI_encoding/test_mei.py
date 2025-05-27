from enum import Enum
import xml.etree.ElementTree as ET
from uuid import uuid4
import argparse

# Valid inputs for state machine
class Inputs(Enum):
    NEUME = 0
    EITHER_SYL = 1 # can be inside syllable or outside
    OUT_SYL = 2
    SYL_START = 3
    SYL_END = 4

# Valid states for state machine
class State(Enum):
    BEFORE_SYLLABLE = 0
    WAIT_FOR_NEUME = 1
    IN_SYLLABLE = 2
    FAIL = 3

class SylMachine:

    # Diagram from this state machine can be found at test_state_machine.excalidraw
    
    def __init__(self):
       
        self.previous_state = State.BEFORE_SYLLABLE
        self.can_be_inside = ["clef","divLine","accid"]

        # adjacency matrix for state machine
        self.adjacency_matrix = []

        # transitions for outside syllable state
        before_syllable_transitions = [None]*5
        before_syllable_transitions[Inputs.NEUME.value] = State.FAIL
        before_syllable_transitions[Inputs.EITHER_SYL.value] = State.BEFORE_SYLLABLE
        before_syllable_transitions[Inputs.OUT_SYL.value] = State.BEFORE_SYLLABLE
        before_syllable_transitions[Inputs.SYL_START.value] = State.WAIT_FOR_NEUME
        before_syllable_transitions[Inputs.SYL_END.value] = State.FAIL
        self.adjacency_matrix.append(before_syllable_transitions)

        # transitions for waiting for neume state
        # just saw syllable being, waiting for neume element for this syllable to be valid
        wait_for_neume_transitions = [None]*5
        wait_for_neume_transitions[Inputs.NEUME.value] = State.IN_SYLLABLE
        wait_for_neume_transitions[Inputs.EITHER_SYL.value] = State.FAIL
        wait_for_neume_transitions[Inputs.OUT_SYL.value] = State.FAIL
        wait_for_neume_transitions[Inputs.SYL_START.value] = State.FAIL
        wait_for_neume_transitions[Inputs.SYL_END.value] = State.FAIL
        self.adjacency_matrix.append(wait_for_neume_transitions)

        # transitions for inside syllable state
        in_syllable_transitions = [None]*5
        in_syllable_transitions[Inputs.NEUME.value] = State.IN_SYLLABLE
        in_syllable_transitions[Inputs.EITHER_SYL.value] = State.IN_SYLLABLE
        in_syllable_transitions[Inputs.OUT_SYL.value] = State.FAIL
        in_syllable_transitions[Inputs.SYL_START.value] = State.FAIL
        in_syllable_transitions[Inputs.SYL_END.value] = State.BEFORE_SYLLABLE
        self.adjacency_matrix.append(in_syllable_transitions)


    # TODO
    # add check for gibberish tag?
    def input_to_enum(self,input):
        if input == "neume":
            return Inputs.NEUME
        elif input in self.can_be_inside:
            return Inputs.EITHER_SYL
        elif input == "syl_begin":
            return Inputs.SYL_START
        elif input == "syl_end":
            return Inputs.SYL_END
        else:
            return Inputs.OUT_SYL

    # reads an element, transitions to next state based on element
    # asserts not in a failure state
    def read(self,input):
        if input[0] == "syl": return
        transition = self.input_to_enum(input[0])
        next_state = self.adjacency_matrix[self.previous_state.value][transition.value]    
        
        assert next_state != State.FAIL, "Failed to invalidate MEI on element with id: " + input[1]

        self.previous_state = next_state

    # asserts the final state is a valid finishing state
    def check_status(self):
        return self.previous_state != State.WAIT_FOR_NEUME and self.previous_state != State.FAIL


# gets an attribute from an element. Handles keys having giberish prefixes
def find_attrib(element,key):
    for k in element.attrib:
        if k.endswith(key):
            return element.attrib[k]

# finds a child of an element with a given tag. Handles giberish prefixes 
def find_child(element,tag):
    for child in element:
        if child.tag.endswith("" + tag):
            return child

# removes gibberish prefix from tag
def clean(string):
    index = string.index("}")
    if index == -1:
        return string
    return string[index+1:]

# returns a list of facsimile ids that are in a layer
def traverse_layer(element):
    if element.tag.endswith("pb"):
        return []
    facsimile = find_attrib(element,"facs")
    out = []
    if facsimile != None:
        out.append(facsimile[1:])
    for sub in element:
        out += traverse_layer(sub)
    return out

# asserts no negative coordinates in a zone
def traverse_for_negatives(element):
    ulx = find_attrib(element,"ulx")
    uly = find_attrib(element,"uly")
    lrx = find_attrib(element,"lrx")
    lry = find_attrib(element,"lry")
    if ulx != None:
        assert int(ulx) >= 0, "Element with id: " + find_attrib(element,"id") + " has negative ulx"
    if uly != None:
        assert int(uly) >= 0, "Element with id: " + find_attrib(element,"id") + " has negative uly"
    if lrx != None:
        assert int(lrx) >= 0, "Element with id: " + find_attrib(element,"id") + " has negative lrx"
    if lry != None:
        assert int(lry) >= 0, "Element with id: " + find_attrib(element,"id") + " has negative lry"
    
    for sub in element:
        traverse_for_negatives(sub)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath')
    args = parser.parse_args()
    tree = ET.parse(args.filepath)
    root = tree.getroot()
    music = find_child(root,"music")
    facsimile = find_child(music,"facsimile")
    surface = find_child(facsimile,"surface")
    body = find_child(music,"body")
    mdiv = find_child(body,"mdiv")
    score = find_child(mdiv,"score")
    section = find_child(score,"section")
    staff = find_child(section,"staff")
    layer = find_child(staff,"layer")



    # FIRST TEST CASE: Syllables well formed
    # elements that should be outside syllable are outside syllable
    # elements that should be inside syllable are inside syllable
    # elements that can be either are in only after a neume is in
    print("Test 1: Syllables well formed")

    elements = []
    for child in layer:
        if child.tag.endswith("syllable"):
            elements.append(("syl_begin",find_attrib(child,"id")))
            for grandchild in child:
                tag = clean(grandchild.tag)
                id = find_attrib(grandchild,"id")
                elements.append((tag,id))   
            elements.append(("syl_end",find_attrib(child,"id")))
            continue
        tag = clean(child.tag)
        id = find_attrib(child,"id")
        elements.append((tag,id))


    machine = SylMachine()
    for element in elements:
        machine.read(element)
    assert machine.check_status(), "Test 1 failed"
    print("Test 1 passed")


    # TEST 2: Matching zones and elements
    # Zones and facsimiles are a bijection
    print("Test 2: Matching zones and elements")

    # Get all the zone ids
    zones = []
    for zone in surface:
        zones.append(find_attrib(zone,"id"))
    
    # Get all the facsimile ids
    faces = traverse_layer(layer)

    # check that zones and faces is a bijection
    assert len(zones) == len(faces), "Test 2 failed"
    for zone in zones:
        assert zone in faces, "Test 2 failed, zone: " + zone + " not in a facsimile"
    
    for fac in faces:
        assert fac in zones, "Test 2 failed, facsimile: " + fac + " not in a zone"
    
    print("Test 2 passed")

    # TEST 3: Proceeds and follows
    print("Test 3: Proceeds and follows")

    syllables = []
    for child in layer:
        if child.tag.endswith("syllable"):
            syllables.append(child)

    # Every syllable has a syl XOR a follows
    for syllable in syllables:
        follows = find_attrib(syllable,"follows")
        syl_child = find_child(syllable,"syl")
        assert (follows == None) != (syl_child == None), "Test 3 failed, syllable: " + find_attrib(syllable,"id") + " has both a follows and a syl child, or has neither"

    # Every syllable with a proceeds has a follows immediately after
    for i, syllable in enumerate(syllables[:-1]):
        proceeds = find_attrib(syllable,"precedes")
        if proceeds != None:
            assert proceeds[1:] == find_attrib(syllables[i+1],"id"), "Test 3 failed, syllable: " + find_attrib(syllable,"id") + " does not precede syllable: " + find_attrib(syllables[i+1],"id")

    # Every syllable with a follows has a proceeds immediately before
    for i, syllable in enumerate(syllables):
        follows = find_attrib(syllable,"follows")
        if follows != None:
            assert follows[1:] == find_attrib(syllables[i-1],"id"), "Test 3 failed, syllable: " + find_attrib(syllable,"id") + " does not follow syllable: " + find_attrib(syllables[i-1],"id")
        
    print("Test 3 passed")

    print("Test 4: No negative coordinates")
    traverse_for_negatives(surface)
    print("Test 4 passed")

    