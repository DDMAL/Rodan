import cv2 as cv
import numpy as np

# converts 4 channel rgba image to grayscale
def convert_to_grayscale(img):    
    img_gray = 255 - img[:, :, 3]
    # save img to disk for debugging
    return img_gray

def moving_avg_filter(data, filter_size):
    """
    returns a list containing the data in @data filtered through a moving-average filter of size
    @filter_size to either side; that is, filter_size = 1 gives a size of 3, filter size = 2 gives
    a size of 5, and so on.

    Ideally, filter_size should be about half the height of a letter on the page (not counting ascenders
    or descenders), in pixels.
    """
    filter_size = int(filter_size)
    smoothed = np.zeros(len(data))
    for n in range(filter_size, len(data) - filter_size):
        vals = data[n - filter_size : n + filter_size + 1]
        smoothed[n] = np.mean(vals)
    return smoothed

def get_split_locations(gray,num_splits):
    # invert colors to make math easier
    flipped = gray == False
    projection = np.sum(flipped,axis=0)
    # apply filter to projection
    # not sure if this is necessary
    filtered = moving_avg_filter(projection,filter_size=5)

    # for the number of columns, find a point in the column,
    # then find the bounds as the first points to the right
    # and left of that point that are 0
    # then make the projection at the column 0 and repeat
    bounds = []
    for i in range(num_splits+1):
        max = np.argmax(filtered)
        left_bound, right_bound = max, max
        while filtered[left_bound] > 0:
            left_bound -= 1
        while filtered[right_bound] > 0:
            right_bound += 1
        bounds.append((left_bound,right_bound))
        filtered[left_bound:right_bound + 1] = 0

    
    # sort column bounds in left to right order
    bounds.sort(key=lambda x: x[0])

    # make sure no bounds overlap
    # I don't have a test case where this happens so this is not tested!!!
    # if this is step is necessary for a folio, then that folio is probably
    # not a good candidate for this algorithm
    for i in range(len(bounds)-1):
        if bounds[i][1] > bounds[i+1][0]:
            bounds[i][1], bounds[i+1][0] = bounds[i+1][0], bounds[i][1]

    # get the split points as the midpoint between the bounds
    splits = []
    for i in range(len(bounds) -1):
        mid = (bounds[i][1] + bounds[i+1][0]) // 2
        splits.append(mid)

    return splits


# gets the ranges of the original image that correspond to the columns
def get_split_ranges(img,splits):
    ranges = [(0,splits[0])]
    for split in splits[1:]:
        ranges.append((ranges[-1][1],split))
    ranges.append((splits[-1],img.shape[1]))
    return ranges

# takes ranges in x, and stacks them vertically
def get_stacked_image(img,ranges):
    chunks = []
    max = 0
    # add each column to a list
    # also find the widest column. All other columns
    # must be padded to this width
    for r in ranges:
        chunks.append(img[:,r[0]:r[1]])
        if chunks[-1].shape[1] > max:
            max = chunks[-1].shape[1]
    
    # pad each column to the widest column
    output = []
    for chunk in chunks:
        output.append(np.pad(chunk,((0,0),(0,max-chunk.shape[1]),(0,0)),mode='constant',constant_values=255))
    # stack and return
    return np.vstack(output)
