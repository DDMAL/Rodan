# text-alignment

Given an image of the text layer of a chant manuscript, and a transcript of text that lies entirely within that manuscript, finds the position of each syllable of that text on the page. **NOTE: The syllabification process included in this presently only works on latin text. It has been tested on chants from the Salzinnes Antiphonal (16th century), Einsiedeln 611 (14th century), St. Gallen 388 (12th century), and St. Gallen 390, 391 (10th century).**

### Installation

Python 3.5+ only. Currently requires Calamari 1.0.5, which is a slightly older version than current.


### How To Run Locally
Run from alignToOCR.py. Edit the parameters at the top of the ```__main__``` method to change what is processed.

# How It Works

### Text Layer Preprocessing / Line Identification

The input text layer can be  messy, so we need to clean it up a bit - this involves despeckling, and also removing narrow "runs," to try to break up letters that are connected to each other by skinny lines of noise. Then, the vertical position of each text line is found by finding the prominent peaks of a vertical projection. The assumption here is that every line is roughly parallel, and each line contains characters that are roughly the same height. Large ornamental letters are treated as noise, since OCRing them at this point would be too difficult. Lines are not assumed to have the same length.

### OCR with OCRopus

Calamari is not intended for use on handwritten text, but it gets a reasonably good result (~80% per-character accuracy on most pages of Salzinnes using the relatively simple model included with this repo). Each identified text line is saved to a file, and Calamari is used to attempt OCR on each one, retrieving the characters found within the line and the position of each one on the page.

### Aligning OCR with Correct Transcript

The OCR output gives us a list of character locations and a somewhat accurate prediction for what character actually lies at each location; the given transcript gives us the exact characters that appear on the page but no information as to their positions. The object of this step is to combine these two source of information to find locations of each character on the page.

The [Needleman-Wunsch algorithm](https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm) is implemented in ```textSeqCompare.py``` with affine gap penalties. The assumption is that both sequences (the OCRed characters and the transcript) are related through the operations of character replacement and character insertion/deletion (indels). (See also: [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance).) Each operation usually has a cost associated with it depending on the application; replacement may be a less 'costly' operation than indels, for example.  One way to interpret the algorithm is that it finds the least-costly way to transform one sequence into another under the given operations.

Note that many manuscript pages contain text that is not associated with music, and so not present in the transcript; this non-musical text with be OCRed, but the sequence alignment will be able to skip over it as long as the content of the non-musical text is sufficiently different from the musical text.

As long as _most_ of the characters in the OCR are correct, then the sequence alignment algorithm will effectively correct the errors made by the OCR, yielding a list of all characters in the transcript, each associated with a particular bounding box on the image.

### Grouping into Syllables

Since the MEI specification requires that neume notation be presented syllable by syllable, we want to merge our individual characters into syllables of text. Figuring out the syllable grouping is handled by ```latinSyllabification.py``` -- luckily, the rules for syllabification in latin are straightforward (Of course, abbreviations like "Dns" for "Dominus" require special cases). This section involves finding the bounding boxes for each syllable of text, and dealing with strange edge cases such as when a syllable is split by a line break.

### JSON Output

The output of this process is a JSON file which contains a list of elements formatted as:
```
syl_boxes:[{
    syl: [a syllable of text]
    ul: [upper-left point of bounding box]
    lr: [lower-right point of bounding box]
} ... ],
median_line_spacing: [median space between adjacent text lines, in pixels]
```

# Training a New Calamari model

What's necessary to train a new model is, essentially, a whole bunch of binarized image files containing individual lines of text, and a bunch of corresponding `.gt.txt` files containing, in plain-text, the text that is on each strip. Each text file should have the same name as its corresponding image file (so `001r_5.png` should be transcribed in `001r_5.gt.txt`). This text should be a perfectly _diplomatic_ transcription: that is, it should represent exactly what characters are in the text script, with no editorializing, expansion of abbreviations, or corrections of spelling. For example: 

- "regnū" should be transcribed as "regnū" and not "regnum"
- "eius" should be transcribed as "eius" and not "ejus"
- "dn̄s" should be transcribed as "dn̄s" and not "dominus." 
- "alla" should be transcribed as "alla" and not "alleluia" 
- "&" should be transcribed as "&" and not "et"

And so on. For blots of ink on the page, large capital characters that are only partially captured in the strip of text, or characters that don't have an equivalent in unicode, just ignore them. For a detailed description of how the training data needs to be set up, check [the Calamari documentation](https://calamari-ocr.readthedocs.io/en/latest/doc.dataset-formats.html).

The script  `/training_new_models/save_text_strips.py` can be used to segment layer-separated images (specifically, whichever layer has the text and doesn't have the neumes or staff lines) into text strips that can then be used for training. Use the command-line interface of that script to point at a folder full of such images and it'll segment each of them, saving the strips from each image into their own folder. For example, you could run: `python save_text_strips.py /path/to/image/files /path/to/output/destination `.

Calamari has a command-line interface for training models, that can be run once enough training data has been collected: [Calamari getting started guide](https://calamari-ocr.readthedocs.io/en/latest/doc.command-line-usage.html#calamari-train)

 You don't need to do _too_ many for text alignment to work correctly; 99% accuracy is overkill! For the Salzinnes manuscript, I transcribed about 40 pages, which took ~3 hours, and let it train for about 12 hours, and this was perfectly sufficient.
