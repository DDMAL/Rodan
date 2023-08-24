from enum import Enum
import xml.etree.ElementTree as ET
from uuid import uuid4
import argparse
class Inputs(Enum):
    NEUME = 0
    IN_SYL = 1
    OUT_SYL = 2
    SYL_START = 3
    SYL_END = 4

class State(Enum):
    BEFORE_SYLLABLE = 0
    WAIT_FOR_NEUME = 1
    IN_SYLLABLE = 2
    FAIL = 3

class SylMachine:
    
    def __init__(self):
       
        self.previous_state = State.BEFORE_SYLLABLE
        self.adjacency_matrix = []

        self.can_be_inside = ["clef","divLine","accid"]

        before_syllable_transitions = [None]*5
        before_syllable_transitions[Inputs.NEUME.value] = State.FAIL
        before_syllable_transitions[Inputs.IN_SYL.value] = State.BEFORE_SYLLABLE
        before_syllable_transitions[Inputs.OUT_SYL.value] = State.BEFORE_SYLLABLE
        before_syllable_transitions[Inputs.SYL_START.value] = State.WAIT_FOR_NEUME
        before_syllable_transitions[Inputs.SYL_END.value] = State.FAIL
        self.adjacency_matrix.append(before_syllable_transitions)

        wait_for_neume_transitions = [None]*5
        wait_for_neume_transitions[Inputs.NEUME.value] = State.IN_SYLLABLE
        wait_for_neume_transitions[Inputs.IN_SYL.value] = State.FAIL
        wait_for_neume_transitions[Inputs.OUT_SYL.value] = State.FAIL
        wait_for_neume_transitions[Inputs.SYL_START.value] = State.FAIL
        wait_for_neume_transitions[Inputs.SYL_END.value] = State.FAIL
        self.adjacency_matrix.append(wait_for_neume_transitions)

        in_syllable_transitions = [None]*5
        in_syllable_transitions[Inputs.NEUME.value] = State.IN_SYLLABLE
        in_syllable_transitions[Inputs.IN_SYL.value] = State.IN_SYLLABLE
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
            return Inputs.IN_SYL
        elif input == "syl_begin":
            return Inputs.SYL_START
        elif input == "syl_end":
            return Inputs.SYL_END
        else:
            return Inputs.OUT_SYL

    def read(self,input):
        if input[0] == "syl": return
        transition = self.input_to_enum(input[0])
        next_state = self.adjacency_matrix[self.previous_state.value][transition.value]    
        
        assert next_state != State.FAIL, "Failed to invalidate MEI on element with id: " + input[1]

        self.previous_state = next_state

    def check_status(self):
        return self.previous_state != State.WAIT_FOR_NEUME and self.previous_state != State.FAIL


def find_attrib(element,key):
    for k in element.attrib:
        if k.endswith(key):
            return element.attrib[k]
        
def find_child(element,tag):
    for child in element:
        if child.tag.endswith("" + tag):
            return child

def clean(string):
    index = string.index("}")
    if index == -1:
        return string
    return string[index+1:]

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


    print("Test 1: Syllables well formed")
    machine = SylMachine()
    for element in elements:
        machine.read(element)
    assert machine.check_status(), "Test 1 failed"
    print("Test 1 passed")

    print("Test 2: Matching zones and elements")

    zones = []
    for zone in surface:
        zones.append(find_attrib(zone,"id"))
    
    faces = traverse_layer(layer)

    # check that zones and faces is a bijection
    assert len(zones) == len(faces), "Test 2 failed"
    for zone in zones:
        assert zone in faces, "Test 2 failed, zone: " + zone + " not in a facsimile"
    
    for fac in faces:
        assert fac in zones, "Test 2 failed, facsimile: " + fac + " not in a zone"
    
    print("Test 2 passed")

    print("Test 3: Proceeds and follows")

    syllables = []
    for child in layer:
        if child.tag.endswith("syllable"):
            syllables.append(child)

    for syllable in syllables:
        follows = find_attrib(syllable,"follows")
        syl_child = find_child(syllable,"syl")
        assert follows == None or syl_child == None, "Test 3 failed, syllable: " + find_attrib(syllable,"id") + " has both a follows and a syl child"

    for i, syllable in enumerate(syllables[:-1]):
        proceeds = find_attrib(syllable,"precedes")
        if proceeds != None:
            assert proceeds[1:] == find_attrib(syllables[i+1],"id"), "Test 3 failed, syllable: " + find_attrib(syllable,"id") + " does not precede syllable: " + find_attrib(syllables[i+1],"id")
    
    for i, syllable in enumerate(syllables):
        follows = find_attrib(syllable,"follows")
        if follows != None:
            assert follows[1:] == find_attrib(syllables[i-1],"id"), "Test 3 failed, syllable: " + find_attrib(syllable,"id") + " does not follow syllable: " + find_attrib(syllables[i-1],"id")
        
    print("Test 3 passed")



    