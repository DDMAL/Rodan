from os.path import isfile, join
import numpy as np
import os
from skimage import io
from skimage.color import rgb2gray, rgba2rgb
from skimage.util import img_as_float32
from skimage.filters import gaussian, threshold_otsu
from skimage.morphology import binary_opening, binary_closing
from skimage.transform import rescale, rotate
from skimage.segmentation import flood_fill


# PARAMETERS FOR PREPROCESSING
soften_amt = 5          # size of gaussian blur to apply before taking threshold
fill_holes = 5          # size of kernel used for morphological operations when despeckling

# PARAMETERS FOR TEXT LINE SEGMENTATION
filter_size = 80                # size of moving-average filter used to smooth projection
prominence_tolerance = 0.70     # log-projection peaks must be at least this prominent


def calculate_peak_prominence(data, index):
    '''
    returns the log of the prominence of the peak at a given index in a given dataset. peak
    prominence gives high values to relatively isolated peaks and low values to peaks that are
    in the "foothills" of large peaks.
    '''
    current_peak = data[index]

    # ignore values at either end of the dataset or values that are not local maxima
    if (index == 0 or
            index == len(data) - 1 or
            data[index - 1] > current_peak or
            data[index + 1] > current_peak or
            (data[index - 1] == current_peak and data[index + 1] == current_peak)):
        return 0

    # by definition, the prominence of the highest value in a dataset is equal to the value itself
    if current_peak == max(data):
        return np.log(current_peak)

    # find index of nearest maxima which is higher than the current peak
    higher_peaks_inds = [i for i, x in enumerate(data) if x > current_peak]

    right_peaks = [x for x in higher_peaks_inds if x > index]
    if right_peaks:
        closest_right_ind = min(right_peaks)
    else:
        closest_right_ind = np.inf

    left_peaks = [x for x in higher_peaks_inds if x < index]
    if left_peaks:
        closest_left_ind = max(left_peaks)
    else:
        closest_left_ind = -np.inf

    right_distance = closest_right_ind - index
    left_distance = index - closest_left_ind

    if (right_distance) > (left_distance):
        closest = closest_left_ind
    else:
        closest = closest_right_ind

    # find the value at the lowest point between the nearest higher peak (the key col)
    lo = min(closest, index)
    hi = max(closest, index)
    between_slice = data[lo:hi]
    key_col = min(between_slice)

    prominence = np.log(data[index] - key_col + 1)

    return prominence


def find_peak_locations(data, tol=prominence_tolerance, ranked=False):
    '''
    given a vertical projection in @data, finds prominent peaks and returns their indices
    '''

    prominences = [(i, calculate_peak_prominence(data, i)) for i in range(len(data))]

    # normalize to interval [0,1]
    prom_max = max([x[1] for x in prominences])
    if prom_max == 0 or len(prominences) == 0:
        # failure to find any peaks; probably monotonically increasing / decreasing
        return []

    prominences[:] = [(x[0], x[1] / prom_max) for x in prominences]

    # take only the tallest peaks above given tolerance
    peak_locs = [x for x in prominences if x[1] > tol]

    # if a peak has a flat top, then both 'corners' of that peak will have high prominence; this
    # is rather unavoidable. just check for adjacent peaks with exactly the same prominence and
    # remove the lower one
    to_remove = [peak_locs[i] for i in range(len(peak_locs) - 2)
                if peak_locs[i][1] == peak_locs[i+1][1]]
    for r in to_remove:
        peak_locs.remove(r)

    if ranked:
        peak_locs.sort(key=lambda x: x[1] * -1)
    else:
        peak_locs[:] = [x[0] for x in peak_locs]

    return peak_locs


def moving_avg_filter(data, filter_size=filter_size):
    '''
    returns a list containing the data in @data filtered through a moving-average filter of size
    @filter_size to either side; that is, filter_size = 1 gives a size of 3, filter size = 2 gives
    a size of 5, and so on.
    '''
    smoothed = np.zeros(len(data))
    for n in range(filter_size, len(data) - filter_size):
        vals = data[n - filter_size: n + filter_size + 1]
        smoothed[n] = np.mean(vals)
    return smoothed

def fill_corners(input_image, fill_value=0, thresh=0.5, tol=None, fill_below_thresh=True):
    '''
    Checks each corner of the image to identify areas of black pixels. Converts such regions into white pixels to 
    enable peak location.
    
    @ input image: grayscale or binarized input image (must be in float format, not int)
    @ fill_value: determines the value to flood-fill with.
    @ thresh: pixel value above/below which a flood fill will be instantiated.
    @ tol: tolerance for flood fill algorithm, in [0, 1] (grayscale input only: must be None if a binary image is input).
    @ fill_below_thresh: if true, fill regions lower (darker) than the threshold, if false, fill regions higher (lighter)
    '''

    if (input_image[0,0] < thresh) == fill_below_thresh:
        input_image = flood_fill(input_image, (0, 0), fill_value, tolerance=tol)
    if (input_image[-1, 0] < thresh) == fill_below_thresh:
        input_image = flood_fill(input_image, (-1, 0), fill_value, tolerance=tol)
    if (input_image[0, -1] < thresh) == fill_below_thresh:
        input_image = flood_fill(input_image, (0, -1), fill_value, tolerance=tol)   

    # This statement would cause the job to hang, but a statement like this could be used for the bottom right corner.
    # if input_image[-1, -1] < thresh:
    #     input_image = flood_fill(input_image, (-1, -1), 1, tolerance=tol)

    return input_image

def preprocess_images(input_image, soften=soften_amt, fill_holes=fill_holes):
    '''
    Perform some softening / erosion / binarization on the text layer. Additionally, finds the
    optimal angle for rotation and returns a "cleaned" rotated version along with a raw, binarized
    rotated version.
    '''

    # ensure that all points which are transparent have RGB values of 255 (will become white when
    # converted to non-transparent grayscale.)
    input_image = img_as_float32(input_image)
    if len(input_image.shape) == 3 and input_image.shape[2] == 4:
        input_image = rgba2rgb(input_image)
    # gray_img = fill_corners(rgb2gray(input_image))
    gray_img = rgb2gray(input_image)

    # get the otsu threshold after running a flood fill on the corners, so that those huge clumps of
    # dark pixels don't mess up the statistics too much (we only care about text!)
    thresh = threshold_otsu(fill_corners(gray_img, 1, tol=0.3, fill_below_thresh=True))

    # n.b. here we are setting black pixels from the original image to have a value of 1 (effectively inverting
    # what you would get from a normal binarization, because the math gets easier this way)
    img_bin = gray_img < thresh
    img_blur_bin = gaussian(gray_img, soften) < thresh

    # now, fill corners of binarized images with black (value 0)
    img_bin = fill_corners(img_bin, fill_value=0, tol=None, fill_below_thresh=False)
    img_blur_bin = fill_corners(img_blur_bin, fill_value=0, tol=None, fill_below_thresh=False)

    # run smoothing on the blurred-binarized image so we get blobs of text in neat lines
    kernel = np.ones((fill_holes, fill_holes), np.uint8)
    img_cleaned = binary_opening(binary_closing(img_blur_bin, kernel), kernel)

    # find rotation angle of cleaned, smoothed image. use that to correct the rotation of the unsmoothed image
    angle = find_rotation_angle(img_cleaned)
    img_cleaned_rot = rotate(img_cleaned, angle, order=0, mode='edge') > 0
    img_bin_rot = rotate(img_bin, angle, order=0, mode='edge') > 0

    return img_bin_rot, img_cleaned_rot, angle


def identify_text_lines(img, widen_strips_factor=1):
    '''
    finds text lines on preprocessed image. step-by-step:
    1. find peak locations of vertical projection
    2. find peak locations of derivative of vertical projection (so, rows where the number of black
    pixels is changing very rapidly, moving down the page)
    3. from every peak found in step 1, associate it with its neighboring peaks found in part 2,
    from above and below.
    4. take a tight bounding box around all content found between two derivative-peaks.
    '''

    # compute y-axis projection of input image and filter with sliding window average
    project = np.clip(img, 0, 1).sum(1)
    smoothed_projection = moving_avg_filter(project, filter_size)

    # calculate normalized log prominence of all peaks in projection
    peak_locations = find_peak_locations(smoothed_projection)
    diff_proj_peaks = find_peak_locations(np.abs(np.diff(smoothed_projection)))

    line_margins = []
    for p in peak_locations:
        # get the largest diff-peak smaller than this peak, and the smallest diff-peak that's larger
        lower_peaks = [x for x in diff_proj_peaks if x < p]
        lower_bound = max(lower_peaks) if len(lower_peaks) > 0 else 0

        higher_peaks = [x for x in diff_proj_peaks if x > p]
        higher_bound = min(higher_peaks) if len(higher_peaks) > 0 else 0

        if higher_bound and not lower_bound:
            lower_bound = p + (p - higher_bound)
        elif lower_bound and not higher_bound:
            higher_bound = p + (p - lower_bound)

        # extend bounds of strip slightly away from peak location, for safety (diacritics, etc)
        lower_bound -= int((p - lower_bound) * widen_strips_factor)
        lower_bound = max(0, lower_bound)
        higher_bound += int((higher_bound - p) * widen_strips_factor)
        higher_bound = min(img.shape[0], higher_bound)

        line_margins.append([lower_bound, higher_bound])

    # iterate through every pair of peak locations to make sure consecutive strips are not overlapping 
    for i in range(len(peak_locations) - 1):
        prev_peak = peak_locations[i]
        next_peak = peak_locations[i + 1]
        prev_higher_bound = line_margins[i][1]
        next_lower_bound = line_margins[i + 1][0]

        # we don't want strips to overlap at all - if they're not overlapping, assume we're doing fine
        # and leave these strips alone
        if prev_higher_bound < next_lower_bound:
            continue

        # if strips are overlapping, find a horizontal line that is 1) between the peaks AND 2) inside the overlap of the strips
        # with the smallest number of black pixels. set their higher and lower bounds to both occur at that line.

        search_end = min(next_peak, prev_higher_bound)
        search_start = max(prev_peak, next_lower_bound)

        # if, somehow, things went SO poorly that the overlap of two strips is not between the two peaks,
        # then use the two peaks themselves as a failsafe
        try:
            new_bound = np.argmin(smoothed_projection[search_start:search_end]) + search_start
        except ValueError:
            new_bound = np.argmin(smoothed_projection[prev_peak:next_peak]) + prev_peak

        line_margins[i][1] = new_bound
        line_margins[i + 1][0] = new_bound

    # extract actual strip bounds from the refined margins from above
    line_strips = []
    for i, lm in enumerate(line_margins):
        lower_bound, higher_bound = lm
        p = peak_locations[i]
        # tighten up strip by finding bounding box around contents
        mask = np.zeros(img.shape, np.uint8)
        mask[lower_bound:higher_bound, :] = img[lower_bound:higher_bound, :]

        hz_proj = mask.sum(0).nonzero()[0]
        vt_proj = mask.sum(1).nonzero()[0]

        # it is possible for a strip to contain only zero-valued pixels, meaning it's totally empty.
        # this occurs when the page e.g. has an illustration instead of text lines. just skip the offending line.
        if len(hz_proj) == 0 or len(vt_proj) == 0:
            # print('empty strip found! skipping')
            continue

        x, y = hz_proj[0], vt_proj[0]
        w, h = hz_proj[-1] - x, vt_proj[-1] - y

        line_strips.append((x, y, w, h))

    # go back and check to make sure this process didn't fail. if it did, we'll have bounding
    # boxes at [0, 0, 0, 0]. as a failsafe, use the median height of other bounding boxes
    # in place of failed bounding boxes.

    return line_strips, peak_locations, smoothed_projection


def save_preproc_image(image, line_strips, lines_peak_locs, out_fname):
    im = Image.fromarray((1 - image.astype('uint8')) * 255)

    text_size = 70
    fnt = ImageFont.truetype('FreeMono.ttf', text_size)
    draw = ImageDraw.Draw(im)

    # draw lines at identified peak locations
    for i, peak_loc in enumerate(lines_peak_locs):
        draw.text((1, peak_loc - text_size), 'line {}'.format(i), font=fnt, fill='gray')
        draw.line([0, peak_loc, im.width, peak_loc], fill='black', width=7)

    # draw rectangles around identified text lines
    for line in line_strips:
        ul = (line[0], line[1])
        lr = (line[0] + line[2], line[1] + line[3])
        draw.rectangle([ul, lr], outline='gray')

    # im.show()
    im.save(out_fname)


def find_rotation_angle(img, coarse_bound=4, fine_bound=0.1, rescale_amt=0.5):
    '''
    find most likely angle of rotation in two-step refining process
    similar process in gamera, see the paper:
    "Optical recognition of psaltic Byzantine chant notation" by Dalitz. et al (2008)
    '''

    num_trials = int(coarse_bound / fine_bound)
    img_resized = rescale(img, rescale_amt, order=0, multichannel=False)

    def project_angles(img_to_project, angles_to_try):
        best_angle = 0
        highest_variation = 0
        for a in angles_to_try:
            rot_img = rotate(img_to_project, a, mode='edge')
            proj = np.sum(rot_img, 1).astype('int64')
            variation = np.sum(np.diff(proj) ** 2)
            if variation > highest_variation:
                highest_variation = variation
                best_angle = a
        return best_angle

    angles_to_try = np.linspace(-coarse_bound, coarse_bound, num_trials)
    coarse_angle = project_angles(img_resized, angles_to_try)

    angles_to_try = np.linspace(-fine_bound + coarse_angle, fine_bound + coarse_angle, num_trials)
    fine_angle = project_angles(img_resized, angles_to_try)

    return fine_angle


if __name__ == '__main__':
    from PIL import Image, ImageDraw, ImageFont

    # To run locally: point the 'folder' variable below at a folder images of the text from manuscripts,
    # and point the 'out_folder' variable at a folder where you'd like the results to be saved.
    # increase "widen strips" if the results for a particular manuscript cut off the tops and bottoms of letters.
    in_folder = r"D:\Desktop\rodan resources\aligner\png"
    out_folder = r'.\\'
    widen_strips = 3

    img_exts = ['png', 'jpg', 'jpeg']
    fnames = [x for x in os.listdir(in_folder) if x.split('.')[-1] in img_exts]

    for fname in fnames:
        print('processing {}...'.format(fname))
        input_image = io.imread(os.path.join(in_folder, fname))

        img_bin, img_eroded, angle = preprocess_images(input_image, soften=soften_amt, fill_holes=3)

        line_strips, lines_peak_locs, proj = identify_text_lines(img_eroded, widen_strips_factor=widen_strips)
        out_fname = os.path.join(out_folder, f'preproc_{fname}')
        save_preproc_image(img_bin, line_strips, lines_peak_locs, out_fname)

    # plt.clf()
    # plt.plot(proj)
    # for x in lines_peak_locs:
    #     plt.axvline(x=x, linestyle=':')
    # plt.show()

    # diff_proj_peaks = find_peak_locations(np.abs(np.diff(proj)))
    # plt.clf()
    # plt.plot(np.diff(proj))
    # for x in diff_proj_peaks:
    #     plt.axvline(x=x, linestyle=':')
    # plt.show()
