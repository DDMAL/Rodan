import cv2 as cv
import numpy as np

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
    flipped = gray == False
    projection = np.sum(flipped,axis=0)
    filtered = moving_avg_filter(projection,filter_size=5)
    copy = filtered.copy()
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
        # plt.axvline(x=left_bound,color='r')
        # plt.axvline(x=right_bound,color='r')
    

    bounds.sort(key=lambda x: x[0])

    for i in range(len(bounds)-1):
        if bounds[i][1] > bounds[i+1][0]:
            bounds[i][1], bounds[i+1][0] = bounds[i+1][0], bounds[i][1]

    splits = []
    for i in range(len(bounds) -1):
        mid = (bounds[i][1] + bounds[i+1][0]) // 2
        splits.append(mid)
    #     plt.axvline(x=mid,color='g')

    # plt.plot(copy)
    # plt.savefig('projection.png')
    return splits

def get_split_ranges(img,splits):
    ranges = [(0,splits[0])]
    for split in splits[1:]:
        ranges.append((ranges[-1][1],split))
    ranges.append((splits[-1],img.shape[1]))
    return ranges

def get_stacked_image(img,ranges):
    chunks = []
    max = 0
    for r in ranges:
        chunks.append(img[:,r[0]:r[1]])
        if chunks[-1].shape[1] > max:
            max = chunks[-1].shape[1]
    output = []
    for chunk in chunks:
        output.append(np.pad(chunk,((0,0),(0,max-chunk.shape[1]),(0,0)),mode='constant'))
    return np.vstack(output)

    


if __name__ == '__main__':
    img = cv.imread("staffs.png",cv.IMREAD_UNCHANGED)
    gray = convert_to_grayscale(img)
    splits = get_split_locations(gray,3)
    ranges = get_split_ranges(img,splits)
    color = cv.imread("resized.png")
    stacked = get_stacked_image(img,ranges)
    cv.imwrite('stacked.png',stacked)
