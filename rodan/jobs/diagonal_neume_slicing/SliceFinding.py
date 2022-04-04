import numpy as np

try:  # script only imports
    import matplotlib.pyplot as plt
except:
    pass


class SliceFinder (object):

    def __init__(self, **kwargs):
        # projection smoothing
        self.smoothing = kwargs['smoothing']                    # (1, inf) how much convolution to apply

        self.min_proj_seg_length = kwargs['min_projection_segments']    # should be relational

        self.low_projection_threshold = kwargs['low_projection_threshold']

        self.min_slice_spread_rel = kwargs['min_slice_spread_rel']

        self.print_projection_array = kwargs['print_projection_array']
        self.plot_projection_array = kwargs['plot_projection_array']

        self.rotation = kwargs['rotation']

        self.x_max_proj = None
        self.y_max_proj = None

    ##########
    # Public
    ##########

    def get_projections(self, image, rotation):
        col_projs, row_projs = self._get_diagonal_projection_arrays(image, rotation)
        return col_projs, row_projs

    def get_slices(self, image, rotation):
        col_projs, row_projs = self._get_diagonal_projection_arrays(image, rotation)
        col_slices, row_slices = self._get_slices(col_projs, 'x'), self._get_slices(row_projs, 'y')
        return col_slices, row_slices

    def get_extrema(self, image, rotation):
        col_projs, row_projs = self._get_diagonal_projection_arrays(image, rotation)
        col_extrema, row_extrema = self._get_extrema(col_projs), self._get_extrema(row_projs)
        return col_extrema, row_extrema

    def set_max_projs(self, image):
        col_extrema, row_extrema = self.get_extrema(image, self.rotation)

        ui_x_extrema = list(x[1] for x in col_extrema[1])
        ui_y_extrema = list(y[1] for y in row_extrema[1])

        self.x_max_proj = max(ui_x_extrema) if ui_x_extrema else 0
        self.y_max_proj = max(ui_y_extrema) if ui_y_extrema else 0

    ##################
    # Public Helpers
    ##################

    def print_projections(self, projection):
        self._print_projection_array(projection)

    def flatten_extrema(self, extrema):
        output = []
        i = 0
        while i < len(extrema[0]):
            output.append(extrema[1][i])
            output.append(extrema[0][i])
            i += 1
        output.append(extrema[1][-1])

        return output

    ###############
    # Projections
    ###############

    def _get_diagonal_projection_arrays(self, image, rotation):
        # returns an x and y array of diagonal projections
        # separated by segment (0s, ascending, descending)

        col_projs, row_projs = self._get_diagonal_projections(image, rotation)

        col_projs = self._smooth_projection(col_projs)
        row_projs = self._smooth_projection(row_projs)

        col_arrays = self._arrayify_projection(col_projs)
        row_arrays = self._arrayify_projection(row_projs)

        col_arrays = self._filter_projection_array(col_arrays)
        row_arrays = self._filter_projection_array(row_arrays)

        # DEBUG
        if self.print_projection_array:
            print '--------------------------------------------------'
            self._print_projection_array(col_arrays)
            self._print_projection_array(row_arrays)

        if self.plot_projection_array:
            self._plot_projection_array(self._arrays_to_array(col_arrays),
                                        self._arrays_to_array(row_arrays))
            plt.show()

        return col_arrays, row_arrays

    def _smooth_projection(self, projection):
        vals = list(np.convolve(projection, self.smoothing * [1]))
        output_vals = []
        for v in vals:
            output_vals.append(v / self.smoothing)

        return output_vals

    def _arrayify_projection(self, projection):
        projection_spaces = []

        start_pos = 0
        direction = 'up'

        for i, x in enumerate(projection[1:]):

            # found max
            if projection[i] > x and direction is 'up':
                projection_spaces.append(projection[start_pos:i + 1])
                start_pos = i + 1
                direction = 'down'

            # found min
            elif projection[i] < x and direction is 'down':
                projection_spaces.append(projection[start_pos:i + 1])
                start_pos = i + 1
                direction = 'up'

        # grab the last bit
        projection_spaces.append(projection[start_pos:])

        # now projection is of form [0s, up, down, up, ..., down, 0s]
        # first value of each array is a potential split point
        return projection_spaces

    def _filter_projection_array(self, projection):
        # remove 'insignificant' segments by merging them
        i = 0
        while i < len(projection) - 1:
            i += 1
            p = projection[i]

            # print p
            # too few pixels wide, or peak too low, throw out this segment
            if len(p) < self.min_proj_seg_length:  # or not p[-1] < self.low_projection_threshold:
                projection = self._merge_index_with_neighbours(projection, i)
                i -= 1

        return projection

    def _print_projection_array(self, array):
        for x in array:
            print x
        print ''

    def _plot_projection_array(self, array1, array2):
        plt.plot(array1)
        y = np.arange(len(array2))
        plt.plot(array2[::-1], y)

    ##########
    # Slices
    ##########

    def _get_slices(self, proj_arrays, dim):
        extrema = self._get_extrema(proj_arrays)
        slices = self._find_slices(extrema, dim)
        return slices

    def _get_extrema(self, arrays):
        nudge = -1
        minima, maxima = [], []
        for i, a in enumerate(arrays[:-1]):

            if i % 2 == 0:
                maxima.append((len(a) + nudge, a[-1]))
            else:
                minima.append((len(a) + nudge, a[-1]))

            nudge += len(a)

        return minima, maxima

    def _find_slices(self, (minima, maxima), dim):
        slices = []
        rel_max = self.x_max_proj if dim is 'x' else self.y_max_proj

        for i, m in enumerate(maxima[:-1]):
            peak_L, peak_R = maxima[i], maxima[i + 1]
            valley = minima[i]

            spread = min(peak_L[1], peak_R[1]) - valley[1]

            # print spread, self.min_slice_spread_rel * (self.x_max_proj if dim is 'x' else self.y_max_proj)
            # print valley, self.low_projection_threshold * rel_max

            if (spread > self.min_slice_spread_rel * rel_max)and \
                    (valley[1] < self.low_projection_threshold * rel_max):
                slices.append((valley[0], spread))

        return slices

    ##################
    # Image Analysis
    ##################

    def _get_diagonal_projections(self, image, rotation):
        d_image = self._rotate_image(image, rotation)
        projections = list(d_image.projection_cols()), list(d_image.projection_rows())
        return projections

    ####################
    # Image Processing
    ####################

    def _rotate_image(self, image, theta):
        return image.rotate(theta, None, 1)

    ########
    # Misc
    ########

    def _arrays_to_array(self, arrays):
        array = []
        for x in arrays:
            array += x

        return array

    def _merge_index_with_neighbours(self, l, i):
        # given a list of lists, combines the list at i
        # with the list on its left and on its right

        # print 'merge', i, 'size', len(l), l[i]
        # print 'before', l, '\n'

        # if not long enough, merge all
        if len(l) < 4:
            # print 'too short'
            new_l = [[j for i in l for j in i]]

        elif i == 0:              # first position
            # print 'first'
            new_l = [l[0] + l[1]] + l[2:]
        elif i == 1:            # second position
            # print 'second'
            new_l = [l[0] + l[1] + l[2]] + l[3:]

        elif i == len(l) - 1:   # last position
            # print 'last'
            new_l = l[:- 2] + [l[-2] + l[-1]]
        elif i == len(l) - 2:   # second to last position
            # print 'almost last'
            new_l = l[:- 3] + [l[-3] + l[-2] + l[-1]]

        else:                   # middle position
            # print 'middle'
            new_l = l[:i - 1] + [l[i - 1] + l[i] + l[i + 1]] + l[i + 2:]

        # print 'after', new_l, '\n\n'
        return new_l


if __name__ == "__main__":
    pass
