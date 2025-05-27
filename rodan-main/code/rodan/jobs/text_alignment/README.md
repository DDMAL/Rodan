# text-alignment

Given an image of the text layer of a chant manuscript, and a transcript of text that lies entirely within that manuscript, finds the position of each syllable of that text on the page. **NOTE: The syllabification process included in this presently only works on latin text. It has been tested on chants from the Salzinnes Antiphonal (16th century), Einsiedeln 611 (14th century), St. Gallen 388 (12th century), St. Gallen 390, 391 (10th century), and MS Medieval 0073 (15th century).**

### Installation

Python 3.5+ only. Currently requires Calamari 2.1.3

### How To Run Locally
Run from test.py. Change the variables called folder, path_to_transcript, and path_to_image.

# How It Works

### Text Layer Preprocessing / Line Identification

The input text layer can be  messy, so we need to clean it up a bit - this involves despeckling, and also removing narrow "runs," to try to break up letters that are connected to each other by skinny lines of noise. Then, the vertical position of each text line is found by finding the prominent peaks of a vertical projection. The assumption here is that every line is roughly parallel, and each line contains characters that are roughly the same height. Large ornamental letters are treated as noise, since OCRing them at this point would be too difficult. Lines are not assumed to have the same length. After finding the vertical position of the text strips, the next step is to find the bounds of the text strip. The is estimated by center + average_character_height, and center - average_character_height. The bounds are then dilated by a dilation factor of 1.5. The average_character_height is estimated by averaging the heights of the connected components weighted by the component width.

### OCR with OCRopus

Calamari is not intended for use on handwritten text, but it gets a reasonably good result (~80% per-character accuracy on most pages of Salzinnes using the relatively simple model included with this repo). After finding the text strips, they are each individually OCRed by Calamari which returns the characters and their positions within the text strip.

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

### Installation

Unfortunately, Calamari-ocr depends on tfaip, which is now dead. Calamari-ocr is not being maintained. However, the Rodan GPU container's environment is still able to run Calamari-ocr to train a new model.

### How to Run Locally

#### Creating a dataset

What's necessary to train a new model is, essentially, a whole bunch of binarized image files containing individual lines of text, and a bunch of corresponding `.gt.txt` files containing, in plain-text, the text that is on each strip. Each text file should have the same name as its corresponding image file (so `001r_5.png` should be transcribed in `001r_5.gt.txt`). This text should be a perfectly _diplomatic_ transcription: that is, it should represent exactly what characters are in the text script, with no editorializing, expansion of abbreviations, or corrections of spelling. For example: 

- "regnū" should be transcribed as "regnū" and not "regnum"
- "eius" should be transcribed as "eius" and not "ejus"
- "dn̄s" should be transcribed as "dn̄s" and not "dominus." 
- "alla" should be transcribed as "alla" and not "alleluia" 
- "&" should be transcribed as "&" and not "et"

And so on. For blots of ink on the page, large capital characters that are only partially captured in the strip of text, or characters that don't have an equivalent in unicode, just ignore them. For a detailed description of how the training data needs to be set up, check [the Calamari documentation](https://calamari-ocr.readthedocs.io/en/latest/doc.dataset-formats.html).

The script  `/training_new_models/save_text_strips.py` can be used to segment layer-separated images (specifically, whichever layer has the text and doesn't have the neumes or staff lines) into text strips that can then be used for training. Use the command-line interface of that script to point at a folder full of such images and it'll segment each of them, saving the strips from each image into their own folder. For example, you could run: `python save_text_strips.py /path/to/image/files /path/to/output/destination `.

In addition, the script `/training_new_models/save_text_strips.py` has three parameters other than input and output paths. 
- `-w` (default = 2.0): Factor by which to manually increase width of text strips (default 2.0). Increase if the tops or bottoms of letters are cut off.
- `-d` (default = 6): Controls amount of despeckling to run on image before line-finding. Higher values increase tolerance to noise but may remove small markings or diacritics.
- `-l` (default = 70): Approximate height of letters in text lines in the manuscript, from baseline to median (i.e., the height of an "a" or an "e")

You don't need to do _too_ many for text alignment to work correctly; 99% accuracy is overkill! For the Salzinnes manuscript, I transcribed about 40 pages, which took ~3 hours, and let it train for about 12 hours, and this was perfectly sufficient.

#### Running calamari-train

After generating the labeled text strips, it is best to augment the data to artificially inflate the size of the training set and mimic the results of a bad layer seperatation. The script generate_dataset.py will automatically generate an augmented data set. Note that it is recommended that the augmentations are tuned every time a new model is trained. The augmentations are defined at the top of generate_dataset.py right after the import statements. Refer to [here](https://imgaug.readthedocs.io/en/latest/) for how to change the augmentations. \
Each folio that was labelled should have its own folder containing a .gt.txt and .png file for each labelled text strip. These folders should be placed together in a folder with the name of the manuscript they came from. This should be done for each manuscript being used for training. Finally, these folders should be beside generate_dataset.py. The file structure should like something like this:

>generate_dataset.py\
>save_text_strips.py\
>Salzinnes
>>    Folio1
>>>        1.gt.txt
>>>        1.png
>>    Folio2
>>>        2.gt.txt
>>>       2.png
>StGall
>>    Folio1
>>>        1.gt.txt
>>>        1.png
>>    Folio2
>>>        2.gt.txt
>>>        2.png

Next, modify the dirs variable of generate_dataset.py to be a list of the names of the manuscripts. Finally, run python generate_dataset.py, and the data will be generated automatically. 4 folders will be produced. train_aug, val_aug, train_same, and val_same. The folders ending in aug contain the augmented data while the folders ending in same contain the original data. Both are needed for training.

The most successful text alignment models we've trained have been based off of the deep3 architecture as specificed [here](https://github.com/Calamari-OCR/calamari/blob/master/calamari_ocr/resources/networks/deep3.json).

Calamari has a command-line interface for training models, that can be run once enough training data has been collected: [Calamari getting started guide](https://calamari-ocr.readthedocs.io/en/latest/doc.command-line-usage.html#calamari-train).

The first step of training is to produce a model trained on the augmented data from scratch. Create a folder called new_model. The command to train is:

    calamari-train --train.images train_aug/*.png --val.images val_aug/*.png --trainer.output_dir new_model --trainer.write_checkpoints True --network=conv=40:3x3,pool=2x2,conv=60:3x3,pool=2x2,conv=120,lstm=200,lstm=200,lstm=200,dropout=0.5

If you have a gpu, then add --device.gpus 0.

After this is finished, new models can be found in the new_models folder called best.ckpt.h5 and best.ckpt.json. The next step is to tune the model using the unaugmented data. Remove best.ckpt.h5 and best.ckpt.json from new_model, and place them beside the training data folders. Run this command next.

    calamari-train --train.images train_same/*.png --val.images val_same/*.png --trainer.output_dir new_model --warmstart.model best.ckpt.h5 --trainer.write_checkpoints True --network=conv=40:3x3,pool=2x2,conv=60:3x3,pool=2x2,conv=120,lstm=200,lstm=200,lstm=200,dropout=0.5

Now you have a trained an ocr model. It is sometimes worth it to repeat this process by fine tuning the model on the augmented data followed by the unaugmented data.

