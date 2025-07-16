from enum import Enum
import xml.etree.ElementTree as ET
from uuid import uuid4
from rodan.jobs.MEI_encoding import build_mei_file as bm


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

    def __init__(self, text, bb, surface, layer):
        self.surface = surface
        self.bb = bb
        self.layer = layer

        # The initial element for this syllable
        self.curr_syl = ET.Element("syllable")
        self.curr_syl.set("xml:id", "m-" + str(uuid4()))

        # Create the syl tag, has the text but don't set facs yet
        self.syl = ET.SubElement(self.curr_syl, "syl")
        self.syl.set("xml:id", "m-" + str(uuid4()))
        self.syl.text = text
        # Only set facs when/if the syllable gets added to layer

        # initial state is NO_NEUME
        self.prev_state = States.NO_NEUME

        # elements that can be in the syllable or outside
        # neume in always inside so it is not in this list
        self.can_be_in_syllable = {"divLine", "clef", "accid"}

        # build the adjacency matrix for the state machine as shown in the diagram.
        # An adjacency matrix is a data structure that represents a graph. Rows of the adjacency
        # matrix represent the states, the columns are possible inputs, and a square in the matrix
        # contains which state should be moved to from some state given some input.
        #
        # Ex: When you are at state NEUME_ADDED and see OUT_SYL, the transition should
        # be to BREAK_OUT. As such,
        # self.adjacency_matrix[States.NEUME_ADDED.value][Inputs.OUT_SYL.value] = States.BREAK_OUT
        # The first dimension here grabs the current state, returning a list of transitions. Indexing it by
        # the input provides the next state.
        self.adjacency_matrix = []

        # transitions for the NO_NEUME state
        no_neume_transitions = [None, None, None]
        no_neume_transitions[Inputs.NEUME.value] = States.FIRST_NEUME
        no_neume_transitions[Inputs.IN_SYL.value] = States.NO_NEUME
        no_neume_transitions[Inputs.OUT_SYL.value] = States.NO_NEUME
        self.adjacency_matrix.append(no_neume_transitions)

        # transitions for the FIRST_NEUME state
        first_neume_transitions = [None, None, None]
        first_neume_transitions[Inputs.NEUME.value] = States.ADD_INSIDE
        first_neume_transitions[Inputs.IN_SYL.value] = States.ADD_INSIDE
        first_neume_transitions[Inputs.OUT_SYL.value] = States.BREAK_OUT
        self.adjacency_matrix.append(first_neume_transitions)

        # transitions for the ADD_INISDE state
        add_inside_transitions = [None, None, None]
        add_inside_transitions[Inputs.NEUME.value] = States.ADD_INSIDE
        add_inside_transitions[Inputs.IN_SYL.value] = States.ADD_INSIDE
        add_inside_transitions[Inputs.OUT_SYL.value] = States.BREAK_OUT
        self.adjacency_matrix.append(add_inside_transitions)

        # transitions for the BREAK_OUT state
        break_out_transitions = [None, None, None]
        break_out_transitions[Inputs.NEUME.value] = States.PROCEEDS_FOLLOWS
        break_out_transitions[Inputs.IN_SYL.value] = States.BREAK_OUT
        break_out_transitions[Inputs.OUT_SYL.value] = States.BREAK_OUT
        self.adjacency_matrix.append(break_out_transitions)

        # transitions for the PROCEEDS_FOLLOWS state
        proceeds_follows_transitions = [None, None, None]
        proceeds_follows_transitions[Inputs.NEUME.value] = States.ADD_INSIDE
        proceeds_follows_transitions[Inputs.IN_SYL.value] = States.ADD_INSIDE
        proceeds_follows_transitions[Inputs.OUT_SYL.value] = States.BREAK_OUT
        self.adjacency_matrix.append(proceeds_follows_transitions)

        self.state_mapper = [
            self.no_neume,
            self.first_neume,
            self.add_inside,
            self.break_out,
            self.proceeds_follows,
        ]

    # function for NO_NEUME state
    def no_neume(self, element):
        self.layer.append(element)

    # function for FIRST_NEUME state
    def first_neume(self, element):
        # Generate zone only when we know syllable will be used
        zoneId = bm.generate_zone(self.surface, self.bb)
        self.syl.set("facs", "#" + zoneId)

        self.curr_syl.append(element)
        self.layer.append(self.curr_syl)

    # function for ADD_INSIDE state
    def add_inside(self, element):
        self.curr_syl.append(element)

    # function for BREAK_OUT state
    def break_out(self, element):
        self.layer.append(element)

    # function for PROCEEDS_FOLLOWS state
    def proceeds_follows(self, element):
        new_syllable = ET.Element("syllable")
        new_syllable.set("xml:id", "m-" + str(uuid4()))

        self.curr_syl.set("precedes", "#" + new_syllable.get("xml:id"))
        new_syllable.set("follows", "#" + self.curr_syl.get("xml:id"))

        self.curr_syl = new_syllable
        self.curr_syl.append(element)
        self.layer.append(self.curr_syl)

    # maps an element to an input enum type
    def elm_to_input(self, tag):
        if tag == "neume":
            return Inputs.NEUME
        elif tag in self.can_be_in_syllable:
            return Inputs.IN_SYL
        else:
            return Inputs.OUT_SYL

    # reads an element, moves to the next state and executes the function for that state
    def read(self, tag, element):
        input = self.elm_to_input(tag)
        next_state = self.adjacency_matrix[self.prev_state.value][input.value]
        self.state_mapper[next_state.value](element)
        self.prev_state = next_state

    # reads an element, and adds it outside the syllable
    def read_outside_syllable(self, element):
        self.layer.append(element)
