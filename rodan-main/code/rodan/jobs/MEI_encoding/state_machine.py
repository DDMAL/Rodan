from enum import Enum
import xml.etree.ElementTree as ET
from uuid import uuid4

class Inputs(Enum):
    NEUME = 0
    IN_SYL = 1
    OUT_SYL = 2

class States(Enum):
    NO_NEUME = 0
    FIRST_NEUME = 1
    ADD_INSIDE = 2
    BREAK_OUT = 3
    PROCEEDS_FOLLOWS = 4

class SylMachine:
    
    def __init__(self,text,zoneId):
        self.layer = []
        self.curr_syl = ET.Element("syllable")
        self.curr_syl.set("xml:id", 'm-'+str(uuid4()))
        syl = ET.SubElement(self.curr_syl,"syl")
        syl.set("xml:id", 'm-'+str(uuid4()))
        syl.text =  text
        syl.set('facs', '#' + zoneId)

        self.prev_state = States.NO_NEUME

        # neume is always in the syllable, these are the elements that can be in the syllable but
        # can also be outside of it
        self.contained_in_syllable = {"divLine", "clef", "accid"}

        self.adjacency_matrix = []

        no_neume_transitions = [None,None,None]
        no_neume_transitions[Inputs.NEUME.value] = States.FIRST_NEUME
        no_neume_transitions[Inputs.IN_SYL.value] = States.NO_NEUME
        no_neume_transitions[Inputs.OUT_SYL.value] = States.NO_NEUME
        self.adjacency_matrix.append(no_neume_transitions)

        first_neume_transitions = [None,None,None]
        first_neume_transitions[Inputs.NEUME.value] = States.ADD_INSIDE
        first_neume_transitions[Inputs.IN_SYL.value] = States.ADD_INSIDE
        first_neume_transitions[Inputs.OUT_SYL.value] = States.BREAK_OUT
        self.adjacency_matrix.append(first_neume_transitions)

        add_inside_transitions = [None,None,None]
        add_inside_transitions[Inputs.NEUME.value] = States.ADD_INSIDE
        add_inside_transitions[Inputs.IN_SYL.value] = States.ADD_INSIDE
        add_inside_transitions[Inputs.OUT_SYL.value] = States.BREAK_OUT
        self.adjacency_matrix.append(add_inside_transitions)

        break_out_transitions = [None,None,None]
        break_out_transitions[Inputs.NEUME.value] = States.PROCEEDS_FOLLOWS
        break_out_transitions[Inputs.IN_SYL.value] = States.BREAK_OUT
        break_out_transitions[Inputs.OUT_SYL.value] = States.BREAK_OUT
        self.adjacency_matrix.append(break_out_transitions)

        proceeds_follows_transitions = [None,None,None]
        proceeds_follows_transitions[Inputs.NEUME.value] = States.ADD_INSIDE
        proceeds_follows_transitions[Inputs.IN_SYL.value] = States.ADD_INSIDE
        proceeds_follows_transitions[Inputs.OUT_SYL.value] = States.BREAK_OUT
        self.adjacency_matrix.append(proceeds_follows_transitions)

        self.state_mapper = [self.no_neume,self.first_neume,self.add_inside,self.break_out,self.proceeds_follows]

    def no_neume(self,element):
        self.layer.append(element)
    
    def first_neume(self,element):
        self.curr_syl.append(element)
        self.layer.append(self.curr_syl)
    
    def add_inside(self,element):
        self.curr_syl.append(element)

    def break_out(self,element):
        self.layer.append(element)

    def proceeds_follows(self,element):
        new_syllable = ET.Element("syllable")
        new_syllable.set("xml:id", 'm-'+str(uuid4()))

        self.curr_syl.set("precedes", '#' + new_syllable.get('xml:id'))
        new_syllable.set("follows", "#" + self.curr_syl.get('xml:id'))

        self.curr_syl = new_syllable
        self.curr_syl.append(element)
        self.layer.append(self.curr_syl)

    def elm_to_input(self,tag):
        if tag == "neume":
            return Inputs.NEUME
        elif tag in self.contained_in_syllable:
            return Inputs.IN_SYL
        else:
            return Inputs.OUT_SYL

    def read(self, tag, element):
        input = self.elm_to_input(tag)
        next_state = self.adjacency_matrix[self.prev_state.value][input.value]
        self.state_mapper[next_state.value](element)
        self.prev_state = next_state

    def add_line_break(self,element):
        assert element.tag == "sb"
        self.layer.append(element)
    
    def add_column_break(self,element):
        assert element.tag == "cb"
        self.layer.append(element)