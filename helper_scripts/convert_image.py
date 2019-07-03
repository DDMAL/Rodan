import os

from PIL import Image

if sys.version_info.major == 2:
    input = raw_input

# creates a directory to keep all the converted files
if not os.path.exists('./Converted'):
    os.makedirs('./Converted')

# prompts user to input a path where the files are located ex: /Users/Jacob/Documents/...
path = input('Please enter a path to a directory containing the files to be converted:\n')
# prompts user to input the target format of the image to be converted (ex: 'png', 'jpeg')
img_type = input('Please enter the desired converted format\n')
# loads all the names of the images in the directory
images = [f for f in os.listdir(path) if os.path.isfile(path + f)]

for image in images: # for each image
    if image == '.DS_Store':
       continue
    img = Image.open(path + image) # open the image
    # In pillow 4.2.0, they finally added an error for converting RGBA PNGs to JPEG,
    # Jpeg doesn't have an alpha channel. It just never complained before.
    if img_type.upper() == "JPEG":
        img = img.convert("RGB")
    img_name = os.path.splitext(image)[0] # remove the extension of the image
    img.save('./Converted/'+ img_name + '.' + img_type) # save the image in desired (ex: 'png') format in the "Converted" directory

# Salzinnes Images are not suppported by PIL, use VIPS ('batch_image_convert' command) instead
