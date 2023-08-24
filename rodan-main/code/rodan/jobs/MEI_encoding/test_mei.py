from enum import Enum
import xml.etree.ElementTree as ET
from uuid import uuid4

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


    def fail(self,input):
        raise ValueError("Failed to invalidate MEI on element with id: " + input[1])
    
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
        if next_state == State.FAIL:
            self.fail(input)
        else:
            self.previous_state = next_state

    def check_status(self):
        return self.previous_state != State.WAIT_FOR_NEUME and self.previous_state != State.FAIL


def find(element,key):
    for key in element.attrib:
        if key.endswith("}id"):
            return element.attrib[key]

if __name__ == "__main__":
    tree = ET.parse('debug/result.mei')
    root = tree.getroot()
    # print([child.tag for child in root.iter()])
    stupid_prefix = '{http://www.music-encoding.org/ns/mei}'
    music = root.find(stupid_prefix + "music")
    facsimile = music.find(stupid_prefix + "facsimile")
    surface = facsimile.find(stupid_prefix + "surface")
    body = music.find(stupid_prefix + "body")
    mdiv = body.find(stupid_prefix + "mdiv")
    score = mdiv.find(stupid_prefix + "score")
    section = score.find(stupid_prefix + "section")
    staff = section.find(stupid_prefix + "staff")
    layer = staff.find(stupid_prefix + "layer")

    elements = []
    for child in layer:
        if child.tag == stupid_prefix + "syllable":
            elements.append(("syl_begin",find(child,"id")))
            for grandchild in child:
                tag = grandchild.tag.replace(stupid_prefix,"")
                id = find(grandchild,"id")
                elements.append((tag,id))   
            elements.append(("syl_end",find(child,"id")))
            continue
        tag = child.tag.replace(stupid_prefix,"")
        id = find(child,"id")
        elements.append((tag,id))


    print("Test 1: Syllables well formed")
    machine = SylMachine()
    for element in elements:
        machine.read(element)
    assert machine.check_status(), "Test 1 failed"
    print("Test 1 passed")


    