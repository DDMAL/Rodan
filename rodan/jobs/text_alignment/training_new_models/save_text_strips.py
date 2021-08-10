import sys
import os
from skimage import io
from skimage.util import img_as_ubyte
import argparse

# adding parent folder to path so that image_preprocessing is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import image_preprocessing as preproc

parser = argparse.ArgumentParser(description='Generate training data for training text alignment models.')
parser.add_argument('input_folder', type=str,
                help='Folder containing images to segment into training data.')
parser.add_argument('output_folder', type=str,
                help='Folder to save segmented images into.')
parser.add_argument('-w', '--widen_strips', type=float, default=2.0,
                help='Factor by which to manually increase width of text strips (default 2.0). Increase if the tops or bottoms of letters are cut off.')
parser.add_argument('-d', '--despeckling', type=int, default=6,
                help='Controls amount of despeckling to run on image before line-finding. Higher values increase tolerance to noise but may remove small markings or diacritics.')
parser.add_argument('-l', '--letter_height', type=int, default=70,
                help='Approximate height of letters in text lines in the manuscript, from baseline to median (i.e., the height of an "a" or an "e")')


args = vars(parser.parse_args())

in_folder = args['input_folder']
out_folder = args['output_folder']
widen_amt = args['widen_strips']
despeckle = args['despeckling']
letter_height = args['letter_height']


allowed_exts = ['png', 'jpg', 'jpeg']
fnames = [x for x in os.listdir(in_folder) if x.split('.')[-1] in allowed_exts]

for fname in fnames:
    print('processing {}...'.format(fname))
    input_image = io.imread(os.path.join(in_folder, fname))

    img_bin, img_eroded, angle = preproc.preprocess_images(input_image, soften=5, fill_holes=despeckle)
    line_strips, lines_peak_locs, proj = preproc.identify_text_lines(
        img_eroded, widen_strips_factor=widen_amt, filter_size=letter_height // 2)
    img_invert = img_as_ubyte(1 - img_bin.astype(float))

    img_strips = []
    for ls in line_strips:
        x, y, w, h = ls
        strip = img_invert[y:y + h, x:x + w]
        img_strips.append(strip)

    # save all strips
    strip_folder = os.path.join(out_folder, f"{fname}_strips")
    os.mkdir(strip_folder)
    for i, img_strip in enumerate(img_strips):
        out_fname = f"{i:02}_{fname}"
        io.imsave(os.path.join(strip_folder, out_fname), img_strip)

