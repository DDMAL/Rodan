# MEI2Volpiano
MEI2Volpiano is a Python library developed for the purpose of converting Neume and CWMN MEI files to Volpiano strings.

## Licence
MEI2Volpiano is released under the MIT license.

## Installation

* `pip install mei2volpiano`

## Development Setup

MEI2Volpiano requires at least Python 3.6.
* Clone project `https://github.com/DDMAL/MEI2Volpiano.git`
* Enter the project checkout
* Execute `pip install .` or `poetry install` (this will install development dependencies)

## Usage

As long as you're in the python environment, you can execute `mei2volpiano` or the shorthand `mei2vol` while in your python virtual environment

### Flags

| Flag        | Use           |
| ------------- |:-------------:|
| `-W` or `-N` | Used to specify the type of MEI to converted (Neume or CWN) |
| `txt`| Used to specify whether the user is inputtng MEI files or a text file containing MEI paths |
| `--export` | Signifies that the converted Volpiano string(s) should be outputted to '.txt' files    |

### Standard Usage (Neume notation)

To output the MEI file's volpiano string to the terminal, run

`mei2vol -N mei filename1.mei`

Multiple files can be passed in at once

`mei2vol -N mei filename1.mei filename2.mei`

### Western

To convert MEI files written in Common Western Music Notation (CWMN), run

`mei2vol -W mei filename1.mei`

All of the CWMN files processed by this library (so far) come from [this collection](https://github.com/DDMAL/Andrew-Hughes-Chant/tree/master/file_structure_text_file_MEI_file). Thus, we followed the conventions of those files. Namely:

- Every neume is encoded as a quarter note
- Stemless notes
- Syllables are preceded by their notes
- All notes must have syllables after them
  * If there are notes that are not followed by a syllable, the script will display a message containing these notes. They will not be recorded in the volpiano
  * This can only happen at the end of an MEI file 

The resulting volpiano string will have multiple notes seperated by two hyphens. This seperation is dictated by the syllables, representented by: `<syl>`. The notes themselves are located with the `<note>` tag and represented by the `pname` attribute.

### Mutiple MEI File Runs

To make it easier to pass in multiple MEI files, the `-t` flag can be specified as `txt`:

`mei2vol -W txt filename1.txt` or `mei2vol -N txt filename1.txt filename2.txt ...`

where the ".txt" file being passed in must hold the name/relative path of the required MEI files on distinct lines.

**Note: If passing inputs through this method, the formats of the MEI files within the text file must be of the same type** (either neume for `-N` or western for `-W`)

### Exporting

The `--export` tag can be used on any valid input to the program. Simply tack it on to the end of your command like so

`mei2vol -N mei filename1.mei --export`

and the program will output each mei file's volpiano to a similarly named file as its input.


## Tests

To run the current test suite, execute `pytest`
