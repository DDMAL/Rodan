import image_preprocessing as preproc
import os
from skimage import io
from skimage.util import img_as_ubyte
if __name__ == '__main__':

    folder = r"D:\Desktop\rodan resources\aligner\png"
    allowed_exts = ['png', 'jpg', 'jpeg']
    fnames = [x for x in os.listdir(folder) if x.split('.')[-1] in allowed_exts]
    fnames = [f for f in fnames if 'salz' in f]

    for fname in fnames:
        print('processing {}...'.format(fname))
        input_image = io.imread(os.path.join(folder, fname))

        img_bin, img_eroded, angle = preproc.preprocess_images(input_image, soften=5, fill_holes=50)
        line_strips, lines_peak_locs, proj = preproc.identify_text_lines(img_eroded, widen_strips_factor=2)
        img_invert = img_as_ubyte(1 - img_bin.astype(float))

        img_strips = []
        for ls in line_strips:
            x, y, w, h = ls
            strip = img_invert[y:y + h, x:x + w]
            img_strips.append(strip)

        # save all strips
        strip_folder = os.path.join(folder, f"{fname}_strips")
        os.mkdir(strip_folder)
        for i, img_strip in enumerate(img_strips):
            fname = f"{i:02}_{fname}"
            io.imsave(os.path.join(strip_folder, fname), img_strip)

    # plt.clf()