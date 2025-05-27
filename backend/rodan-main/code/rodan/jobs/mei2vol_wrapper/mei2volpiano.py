"""Converts MEI files to volpiano strings.

Takes in one or more MEI files and outputs their volpiano representation.
See README for flags and usage.
"""

import xml.etree.ElementTree as ET

# namespace for MEI tags
NAMESPACE = "{http://www.music-encoding.org/ns/mei}"


class MEItoVolpiano:
    """
    Class: MEItoVolpiano

    Methods:

        [Main]:
            get_mei_elements(file) -> list[MEI elements]
            sylb_volpiano_map(list[elements]) -> dict[str, str]
            get_syl_key(element, integer) -> str
            get_volpiano(str, str) -> str
            export_volpiano(dict[str, str]) -> str
            convert_mei_volpiano(file, bool = False) -> str

            ^ convert_mei_volpiano handles all methods in Main.

        [Western]:
            sylb_volpiano_map_w(list[elements]) -> dict[str, str]

            ^ convert_mei_volpiano(self, filename, True) calls methods in Main to give
            the volpiano string for MEI files written in Western notation.

        [Debugging]:
            find_clefs(list[elements]) -> list[str]
            find_notes(list[elements]) -> list[str]
            find_syls(list[elements]) -> list[str]
            sylb_note_map(list[elements]) -> dict[str, str]
            compare_volpiano_file(str, file, bool = False) -> bool
            compare_volpiano_volpiano(str, str) -> bool
            standardize_volpiano(str) -> str
            compare_standard(str, file, bool = False) -> bool
            secure_volpiano(str) -> str

            ^ useful for MEI parsing and testing outputs.

    """

    def get_mei_elements(self, filename: str) -> list:
        """Returns a list of all elements in the MEI file.

        Args:
            filename (str): An open MEI file.

        Returns:
            elements (list): List of all elements found.
        """
        tree = ET.parse(filename)
        root = tree.getroot()
        mei_element_objects = root.findall(".//")

        return [mei_element for mei_element in mei_element_objects]

    def find_clefs(self, elements: list) -> list:
        """Finds all clefs in a given elements list

        Args:
            elements (list): List of elements

        Returns:
            clefs (list): char list of all clefs found, in order.
        """
        clefs = []
        for element in elements:
            if element.tag == f"{NAMESPACE}staffDef":
                clefs.append(element.attrib["clef.shape"])
            elif element.tag == f"{NAMESPACE}clef":
                clefs.append(element.attrib["shape"])
        return clefs

    def find_notes(self, elements: list) -> list:
        """Finds all notes in a given elements list

        Args:
            elements (list): List of elements

        Returns:
            notes (list): char list of all notes found, in order.
        """
        return [
            element.attrib["pname"]
            for element in elements
            if element.tag == f"{NAMESPACE}nc"
        ]

    def find_syls(self, elements: list) -> list:
        """Finds all syllables in a given elements list

        Args:
            elements (list): List of elements

        Returns:
            syls (list): string list of all syllables found, in order.
        """
        return [
            element.text
            for element in elements
            if element.tag == f"{NAMESPACE}syl" and element.text
        ]

    def sylb_note_map(self, elements: list) -> dict:
        """Creates a dictionary map of syllables and their notes (with octaves).

        Args:
            elements (list): List of elements

        Returns:
            syl_dict (dict): Dictionary {identifier: notes} of syllables and
            their unique data base numbers as keys and notes (with octaves) as values.
        """

        syl_dict = {"dummy": ""}
        dbase_id = 0
        last = "dummy"

        for element in elements:

            if element.tag == f"{NAMESPACE}syl":
                key = self.get_syl_key(element, dbase_id)
                syl_dict[key] = syl_dict[last]
                dbase_id += 1
                syl_dict["dummy"] = ""
                last = key

            if element.tag == f"{NAMESPACE}nc":
                note = element.attrib["pname"]
                ocv = element.attrib["oct"]
                finNote = f"{note}{ocv}"
                syl_dict[last] = f"{syl_dict[last]}{finNote}"

            if element.tag == f"{NAMESPACE}neume":
                if syl_dict[last] != "":
                    syl_dict[last] = f'{syl_dict[last]}{"-"}'

            if element.tag == f"{NAMESPACE}syllable":
                last = "dummy"

        del syl_dict["dummy"]
        return syl_dict

    def sylb_volpiano_map(self, elements: list) -> dict:
        """Creates a dictionary of syllables and their volpiano values.

        Args:
            elements (list): List of elements

        Returns:
            syl_note (dict): Dictionary {identifier: volpiano notes} of
            syllables and their unique data base numbers as keys and volpiano
            notes with correct octaves as values.
        """
        syl_note = {"dummy": ""}
        dbase_id = 0
        last = "dummy"
        for element in elements:

            if element.tag == f"{NAMESPACE}syl":
                key = self.get_syl_key(element, dbase_id)
                syl_note[key] = syl_note[last]
                dbase_id += 1
                syl_note["dummy"] = ""
                last = key

            if element.tag == f"{NAMESPACE}nc":
                note = element.attrib["pname"]
                ocv = element.attrib["oct"]
                volpiano = self.get_volpiano(note, ocv)
                syl_note[last] = f"{syl_note[last]}{volpiano}"

            if element.tag == f"{NAMESPACE}neume":
                if syl_note[last] != "":
                    syl_note[last] = f'{syl_note[last]}{"-"}'

            if element.tag == f"{NAMESPACE}sb":
                if syl_note[last] != "":
                    syl_note[last] = f'{syl_note[last]}{"7"}'

            if element.tag == f"{NAMESPACE}syllable":
                if syl_note[last] != "":
                    syl_note[last] = f'{syl_note[last]}{"---"}'
                last = "dummy"

        return syl_note

    def sylb_volpiano_map_w(self, elements: list) -> dict:
        """Western notation - Creates a dictionary of syllables and their volpiano values.

        Args:
            elements (list): List of elements

        Returns:
            syl_note (dict): Dictionary {identifier: volpiano notes} of
            syllables and their unique database ids as keys and volpiano
            notes with correct octaves as values.
        """
        syl_note = {"dummy": ""}
        dbase_id = 0
        octave_converter_weight = 2  # C4 in CWMN is octave 2 in volpiano
        invalid_notes = []
        invalid_notes = set(invalid_notes)
        last = "dummy"
        syl_note["invalid"] = ""
        num = True
        for element in elements:
            if element.tag == f"{NAMESPACE}syl":
                key = self.get_syl_key(element, dbase_id)
                if num:
                    syl_note[key] = f"{syl_note[last]}"
                    num = False
                else:
                    syl_note[key] = f'{"--"}{syl_note[last]}'
                dbase_id += 1
                syl_note["dummy"] = ""
                last = "dummy"
            if element.tag == f"{NAMESPACE}note":
                note = element.attrib["pname"]
                ocv = element.attrib["oct"]
                ocv = int(ocv) - octave_converter_weight
                ocv = f"{ocv}"
                volpiano = self.get_volpiano(note, ocv)
                if volpiano == "pname error":
                    invalid_notes.add(note)
                else:
                    syl_note[last] = f"{syl_note[last]}{volpiano}"
        if invalid_notes:
            for val in invalid_notes:
                invalid = "invalid"
                syl_note["invalid"] = f"{syl_note[invalid]} {val}"
        return syl_note

    def get_syl_key(self, element: object, dbase_id: int) -> str:
        """Finds the dictionary key of a syllable from their 'syl' and database
        identifier.

        Args:
            element (element): A single element representing a syllable (syl)
            id (int): The database identifier.

        Returns:
            key (str): The dictionary key for the given syllable.
        """
        key = -1
        if element.text:
            key = "".join(f"{dbase_id}_")
            key = f"{key}{element.text}"
        else:
            key = "".join(f"{dbase_id}")
        return key

    def get_volpiano(self, note: str, ocv: str) -> str:
        """Finds the volpiano representation of a note given its value and octave.

        Args:
            note (str): Note value taken from an element ('c', 'd', 'e' etc.)
            ocv (str): Octave of a given note ('1', '2', '3', or '4')

        Returns:
            oct{x}[note] (str): Volpiano character corresponding to
            input note and octave

            or

            error (str): Error if octave is out of range or note not in
            octave.

        """
        octs = {
            "1": {"f": "8", "g": "9", "a": "a", "b": "b"},
            "2": {"c": "c", "d": "d", "e": "e", "f": "f", "g": "g", "a": "h", "b": "j"},
            "3": {"c": "k", "d": "l", "e": "m", "f": "n", "g": "o", "a": "p", "b": "q"},
            "4": {"c": "r", "d": "s"},
        }

        error = "pname error"

        for key in octs:
            if key == ocv:
                if note in octs[key]:
                    return octs[key][note]
        return error

    def export_volpiano(self, mapping_dictionary: dict) -> str:
        """Creates volpiano string with clef attached.

        Args:
            mapping_dictionary (dict): Dictionary of syllables and their
            corresponding volpiano notes.

        Returns:
            (str): Final, valid volpiano with the clef attached in a single line.
        """
        clef = "1---"
        starting_index = 1  # To avoid adding syllable-independent notes at the start.
        floating_notes = mapping_dictionary["dummy"]
        invalid_notes = ""
        if "invalid" in mapping_dictionary:
            starting_index = 2  # To avoid adding unknown symbols at the start.
            invalid_notes = mapping_dictionary["invalid"]
        floating_string = ""
        invalid_string = ""
        values = list(mapping_dictionary.values())[starting_index::]
        vol_string = "".join(values)
        if len(invalid_notes) == 2:
            invalid_string = f"\n\nWe found an invalid note (pname) inside the MEI file: {invalid_notes.lstrip()}"
        if len(invalid_notes) > 2:
            invalid_string = f"\n\nWe found numerous invalid notes (pnames) inside the MEI file: {invalid_notes.lstrip()}"
        if len(floating_notes) == 1:
            floating_string = f"\n\nWe found one syllable-independent note at the end of the MEI file: {floating_notes}"
        elif len(floating_notes) > 1:
            floating_string = f"\n\nWe found numerous syllable-independent notes at the end of the MEI file: {floating_notes}"

        return f"{clef}{vol_string}{invalid_string}{floating_string}"

    def convert_mei_volpiano(self, filename: str, western: bool = False) -> str:
        """All-in-one method for converting MEI file to valid volpiano string.

        Args:
            filename (file): Open MEI file you want the volpiano of.
            western (bool): MEI file types. False (default) is Neueme and True is CWMN

        Returns:
            volpiano (str): Valid volpiano string representation of the input.
        """
        elements = self.get_mei_elements(filename)
        mapped_values = {}
        if western:
            mapped_values = self.sylb_volpiano_map_w(elements)
        else:
            mapped_values = self.sylb_volpiano_map(elements)
        volpiano = self.export_volpiano(mapped_values)
        return volpiano

    def compare_volpiano_file(
        self, volpiano: str, filename: str, western: bool = False
    ) -> bool:
        """Compares the notes in a given volpiano and MEI file.

        Args:
            volpiano (str): The volpiano string you want to test.
            filename (file): The MEI file you want to compare the volpiano to.
            western (bool): Optional flag to test CWMN.

        Returns:
            bool: True if all the notes match, in order. False otherwise.

        """
        file_output = None
        if western:
            file_output = self.convert_mei_volpiano(filename, True)
        else:
            file_output = self.convert_mei_volpiano(filename)
        clean_output = self.secure_volpiano(file_output)
        clean_volpiano = self.secure_volpiano(volpiano)

        if volpiano == file_output:
            print(
                "Input volpiano is identical to the string output for the given MEI file."
            )
            return True
        elif clean_volpiano == clean_output:
            print(
                "Notes in the input volpiano are identical and in the same order compared to"
                + "the output of the MEI file. However, the hyphens don't match up."
            )
            return True
        else:
            print(
                "Input volpiano has different notes when compared to the output from the MEI file."
            )
            return False
    
    def compare_volpiano_volpiano(self, vol1: str, vol2: str) -> bool:
        """Compares two volpianos. Equality is based solely on notes and their order.

        Args:
            vol1 (str): First volpiano string.
            vol2 (str): Second volpiano string.
        
        Returns:
            bool: Equality based on notes and their order.
        """

        return self.secure_volpiano(vol1) == self.secure_volpiano(vol2)

    def standardize_volpiano(self, volpiano: str) -> str:
        """Standardizes volpiano with only single hyphens, except the clef one.

        Args:
            volpiano(str): The volpiano string you want to standardize.

        Returns:
            str: Standardized volpiano.
        """
        clef = "1---"
        volpiano = volpiano[4:]
        volpiano = volpiano.replace("---", "-").replace("--", "-")
        return f"{clef}{volpiano}"

    def compare_standard(
        self, volpiano: str, filename: str, western: bool = False
    ) -> bool:
        """Standardizes a given volpiano and compare it to the standardized output of an MEI.

        Args:
            volpiano (str): The volpiano string you want to test.
            filename (file): The MEI file you want to compare the volpiano to.
            western (bool): Optional flag to test CWMN.

        Returns:
            bool: True if all the notes match, in order. False otherwise.
        """

        file_output = ""
        standard_volpiano = self.standardize_volpiano(volpiano)
        if western:
            standard_volpiano = self.convert_mei_volpiano(filename, True)
        else:
            standard_volpiano = self.convert_mei_volpiano(filename)

        if file_output == standard_volpiano:
            print("Standardized volpianos are the same.\n")
            return True
        else:
            print("Standardized volpianos are different.\n")
            return False

    def secure_volpiano(self, volpiano: str) -> str:
        """Create the secure version of a given volpiano.

        Args:
            volpiano (str): Volpiano string

        Returns:
            str: Secure volpiano string.
        """

        notes = [letter for letter in volpiano if letter.isalpha()]
        secure_vol = ''

        for note in notes:
            secure_vol = f"{secure_vol}{note}-"
        
        secure_vol = secure_vol[:-1]

        clef = "1---"

        return f"{clef}{secure_vol}"

