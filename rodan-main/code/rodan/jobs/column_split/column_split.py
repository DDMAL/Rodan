import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

# converts 4 channel rgba image to grayscale
def convert_to_grayscale(img):    
    img_gray = 255 - img[:, :, 3]
    # save img to disk for debugging
    return img_gray

# merges all binarized layers into one
def get_merged_layers(images):
    # get the first image
    merged = images[0]
    # merge the rest
    for i in range(1,len(images)):
        merged = np.logical_or(merged,images[i])
    return merged


def preprocess(img):
    kernel = np.ones((3,3),np.uint8)
    cv.morphologyEx(img, cv.MORPH_OPEN, kernel)

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
    projection = np.sum(gray,axis=0)
    # apply filter to projection
    # not sure if this is necessary
    plt.plot(projection,color='blue')
    filtered = moving_avg_filter(projection,filter_size=30)
    rooted = np.sqrt(filtered + 1)
    plt.plot(rooted * np.max(filtered)/np.max(rooted),color='orange')
    normed = rooted / np.max(rooted)
    signal = normed > 0.5
    normed_filtered = signal * np.max(filtered)
    plt.plot(signal * np.max(filtered),color='green')
    # plot the projection and save
    plt.plot(filtered,color='red')
    plt.savefig('test_data/2-projection.png')

    # for the number of columns, find the starting point of the bound (minimum)
    # then find where the end of the bound should be (maximum - 1 --> this is the last minimum value in this portion of the graph)
    # append these two values to the bounds list
    # set all values in the graph before the current max to an arbitrary value that will never be min or max 
    bounds = [(0,0)]
    normed_filtered[:np.argmax(normed_filtered)] = np.argmax(normed_filtered)/2 # first bound is always zero
    for i in range(num_splits-2):
        min = np.argmin(normed_filtered)
        normed_filtered[:min] = np.argmax(normed_filtered)/2 #arbitrary value that will never be min or max
        max = np.argmax(normed_filtered)
        bounds.append((min,max-1))
        normed_filtered[:max] = np.argmax(normed_filtered)/2

    #get last x coordinate in normed_filtered dataset as right most bound.
    bounds.append((np.argmin(normed_filtered),len(normed_filtered)))
    
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
    for i in range(len(bounds)):
        mid = (bounds[i][0] + bounds[i][1]) // 2
        splits.append(mid)

    return splits


# gets the ranges of the original image that correspond to the columns
def get_split_ranges(img,splits):
    ranges = []
    for i in range(len(splits) -1):
        ranges.append((splits[i], splits[i+1]))
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

if __name__ == "__main__":
    # read image
    text = cv.imread('test_data/2-text.png',cv.IMREAD_UNCHANGED)
    staff = cv.imread('test_data/2-staff.png',cv.IMREAD_UNCHANGED)
    neume = cv.imread('test_data/2-neume.png',cv.IMREAD_UNCHANGED)
    # convert to grayscale
    gray_text = convert_to_grayscale(text) == False
    gray_staff = convert_to_grayscale(staff) == False
    gray_neume = convert_to_grayscale(neume) == False
    # merge layers
    merged = get_merged_layers([gray_text,gray_staff,gray_neume])
    # get split locations
    splits = get_split_locations(merged,3)
    # get split ranges
    ranges = get_split_ranges(merged,splits)
    # get stacked image
    stacked_text = get_stacked_image(text,ranges)
    stacked_staff = get_stacked_image(staff,ranges)
    stacked_neume = get_stacked_image(neume,ranges)
    # save stacked images
    cv.imwrite('test_data/2-text-stacked.png',stacked_text)
    cv.imwrite('test_data/2-staff-stacked.png',stacked_staff)
    cv.imwrite('test_data/2-neume-stacked.png',stacked_neume)