from gamera.core import init_gamera, load_image, RGBPixel
from gamera import gamera_xml

import numpy as np

from .SliceFinding import SliceFinder

import sys
import datetime
import os
import glob

init_gamera()


class ProjectionSplitter (object):
    # Given an image of a neume, should return
    # a list of separated neume components

    def __init__(self, **kwargs):

        self.kwargs = kwargs

        # Things to use later
        self.image = None
        self.analysis_image = None
        self.sf = None

        self.min_glyph_size = kwargs['min_glyph_size']          # min number of x or y pixels for a glyph
        self.max_recursive_cuts = kwargs['max_recursive_cuts']  # max number of sub-cuts

        self.rotation = kwargs['rotation']

        # analysis image processing
        self.kfill_amount = 3

        # if one dimension has more slices than the other, cut that one first
        self.prefer_multi_cuts = True if kwargs['slice_prioritization'] == 'Multi-Cut' else False
        self.prefer_x = True if kwargs['slice_prioritization'] == 'Vertical' else False
        self.prefer_y = True if kwargs['slice_prioritization'] == 'Horizontal' else False

        self.multi_cut_min = 0

        self.check_axis = kwargs['check_axis']

        # DEBUG
        self.save_cuts = kwargs['save_cuts']
        self.dont_cut = False

        self.cut_number = 0
        self.recursion_number = 0

    ##########
    # Public
    ##########

    def run(self, image):
        # run once
        image = self._preprocess_image(image)
        analysis_image = self._preprocess_analysis_image(image)

        sf = SliceFinder(**self.kwargs)
        sf.set_max_projs(analysis_image)
        self.sf = sf

        return self._recursive_run(image, 0)

    def _recursive_run(self, image, rec):
        # run recursively

        # process image
        images = self._run(image)

        # repeat
        if len(images) > 1 and rec < self.max_recursive_cuts:
            new_images = []
            for i, im in enumerate(images):
                # print 'recurse:', i
                new_images += self._recursive_run(im, rec + 1)

            return new_images

        else:
            # print 'end recursion'
            return images

    def _run(self, image):
        # run each recursion
        analysis_image = self._preprocess_analysis_image(image)
        best_slice_rot = self._get_best_slice(self.sf.get_slices(analysis_image, self.rotation))

        if self.check_axis:
            best_slice_str = self._get_best_slice(self.sf.get_slices(analysis_image, 0))
            best_slice, rotation = self._get_best_rotation(best_slice_rot, self.rotation, best_slice_str, 0)

        else:
            best_slice = best_slice_rot
            rotation = self.rotation

        images = self._split_image(image, best_slice, rotation)
        images = self._postprocess_images(images)
        # if images:
        #     print images

        return images

    ###############
    # Best Slices
    ###############

    def _get_best_rotation(self, slice1, rot1, slice2, rot2):

        print (rot1, slice1, rot2, slice2)

        if not slice1:
            if not slice2:
                return (None, 0)
            else:
                return (slice2, rot2)
        elif not slice2:
            return (slice1, rot1)

        elif slice2[0][1] > slice1[0][1]:
            return (slice2, rot2)

        else:
            return (slice1, rot1)

    def _get_best_slice(self, xy):
        x_slices, y_slices=xy
        best_x_slice = self._best_slice(x_slices)
        best_y_slice = self._best_slice(y_slices)

        if self.prefer_multi_cuts:
            if len(x_slices) > len(y_slices) + self.multi_cut_min:
                return (best_x_slice, 'x')

            elif len(y_slices) > len(x_slices) + self.multi_cut_min:
                return (best_y_slice, 'y')

        if self.prefer_x:
            if best_x_slice:
                return (best_x_slice, 'x')
        elif self.prefer_y:
            if best_y_slice:
                return (best_y_slice, 'y')

        if best_x_slice or best_y_slice:

            if not best_y_slice:
                # print 'No y\tx:', best_x_slice
                return (best_x_slice, 'x')

            elif not best_x_slice:
                # print 'No x\ty:', best_y_slice
                return (best_y_slice, 'y')

            elif best_x_slice > best_y_slice:
                return (best_x_slice, 'x')

            elif best_x_slice < best_y_slice:
                return (best_y_slice, 'y')

                # FIX THIS

        else:
            return None

        # print 'test'

    def _best_slice(self, slices):
        best_slice = None
        for s in slices:
            if not best_slice or s[1] > best_slice[1]:
                best_slice = s

        return best_slice

    ####################
    # Image Processing
    ####################

    def _preprocess_image(self, image):
        image = self._to_onebit(image)
        # image = image.kfill_modified(self.kfill_amount)

        # image = image.outline(0)

        return image

    def _preprocess_analysis_image(self, image):
        image = image.dilate()
        # image = image.to_rgb().simple_sharpen(1.0).to_onebit()
        # image = image.kfill_modified(self.kfill_amount)
        # image = image.convex_hull_as_image(True)
        # image = image.medial_axis_transform_hs()

        return image

    def _split_image(self, image, best_slice, rotation):

        # if no slice, don't split image
        if not best_slice:
            splits = [image]
            fix_bb = False

        else:
            splits = self._split(image, best_slice[0][0], best_slice[1], rotation)

        return splits

    def _split(self, image, pos, dim, rotation):
        theta = rotation

        # image properties
        cols, rows = image.ncols, image.nrows
        i_ul = image.ul_x, image.ul_y
        cp = self._get_center_of_image(image)           # center point

        # rotated image properties
        r_image = self._rotate_image(image, theta)
        r_cols, r_rows = r_image.ncols, r_image.nrows
        rcp = self._get_center_of_image(r_image)        # rotated center point

        # rotated image points
        r_p1 = (pos, r_rows) if dim is 'x' else (0, pos)  # left / bottom
        r_p2 = (pos, 0) if dim is 'x' else (r_cols, pos)  # top / right
        # print r_p1, r_p2

        # # show rotated cuts
        # r_image.draw_line(r_p1, r_p2, RGBPixel(255, 255, 255), 2.0)
        # r_image.save_PNG('./output/rcut_' + str(datetime.datetime.now().time()).replace(':', '.') + '.png')

        # relate points from ul to center of rotated image
        r_p1 = self._translate_point(r_p1, (0, 0), rcp)
        r_p2 = self._translate_point(r_p2, (0, 0), rcp)
        # print r_p1, r_p2

        # rotate points around origin
        p1 = self._rotate_point_around_origin(r_p1, -theta)
        p2 = self._rotate_point_around_origin(r_p2, -theta)
        # print p1, p2

        # relate points from center of image to ul point
        p1 = self._translate_point(p1, cp, (0, 0))
        p2 = self._translate_point(p2, cp, (0, 0))
        # print p1, p2

        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        # print m

        b1 = p1[1] - (m * p1[0])
        b2 = p2[1] - (m * p2[0])
        # print('b1', b1), ('b2', b2)

        def f_x(x): return m * x + b1

        # DRAW on normal image
        draw_p1, draw_p2 = (0, f_x(0)), (image.ncols, f_x(image.ncols))
        draw_p1 = self._translate_point(draw_p1, i_ul, (0, 0))
        draw_p2 = self._translate_point(draw_p2, i_ul, (0, 0))

        cut_image = image.image_copy()
        cut_image.draw_line(draw_p1, draw_p2, RGBPixel(0, 0, 0), 3)     # cut glyph with white line

        # show cuts
        if self.save_cuts:
            rgb = image.to_rgb()
            rgb.draw_line(draw_p1, draw_p2, RGBPixel(255, 0, 0), 1)
            rgb.save_PNG('./output/cut_' + str(self.cut_number + 1) + '.png')

        if self.dont_cut:
            return [cut_image]

        splits = [x.image_copy() for x in cut_image.cc_analysis()]

        # for s in splits:
        #     s = self._trim_image(s)

        self.cut_number += 1

        return splits

    def _to_onebit(self, image):
        return image.to_onebit()

    def _rotate_image(self, image, theta):
        return image.rotate(theta, None, 1)

    def _trim_image(self, image):
        return image.trim_image(None)

    def _maybe_invert_image(self, image):
        # check the amount of blackness of the image. If it's inverted,
        # the black area will vastly outweigh the white area.
        area = image.area().tolist()[0]
        black_area = image.black_area()[0]

        if area == 0:
            raise AomrError("Cannot divide by a zero area. Something is wrong.")

        # if greater than 60% black, invert the image.
        if (black_area / area) > 0.6:
            image.invert()

        return image

    #####################
    # Images Processing
    #####################

    def _postprocess_images(self, images):
        images = self._filter_tiny_images(images)

        processed_images = []
        for i, im in enumerate(images):

            im = self._trim_image(im)
            processed_images.append(im)

        return processed_images

    def _filter_tiny_images(self, images):
        filtered_images = []    # contains glyphs deemed large enough
        for image in images:
            if image.ncols > self.min_glyph_size or image.nrows > self.min_glyph_size:
                filtered_images.append(image)

        return filtered_images

    ########
    # Math
    ########

    def _rotate_point_around_origin(self, xy, degrees):
        x1 ,y1 =xy
        rads = np.radians(degrees)

        x2 = -1 * y1 * np.sin(rads) + x1 * np.cos(rads)
        y2 = y1 * np.cos(rads) + x1 * np.sin(rads)

        return x2, y2

    def _translate_point(self, point, old_origin, new_origin):
        neutral_p = point[0] + old_origin[0], point[1] + old_origin[1]
        relative_p = neutral_p[0] - new_origin[0], neutral_p[1] - new_origin[1]
        return relative_p

    def _get_center_of_image(self, image):
        l, h = image.ncols, image.nrows
        p = int(0.5 + l / 2.0), int(0.5 + h / 2.0)

        return p


if __name__ == "__main__":
    inImage, inXML, outputDIR = None, None, None

    (in0) = sys.argv[1]
    if '.png' in in0:
        inImage = in0
        image = load_image(inImage)
    elif '.xml' in in0:
        inXML = in0
        glyphs = gamera_xml.glyphs_from_xml(inXML)

    # remove files already there so they dont get stacked up
    filesPNG = glob.glob('./output/*.png')
    filesXML = glob.glob('./output/*.xml')
    for f in filesPNG + filesXML:
        os.remove(f)

    kwargs = {
        'smoothing': 1,
        'min_glyph_size': 20,
        'max_recursive_cuts': 50,
        'rotation': 45,

        # will it cut?
        'min_slice_spread_rel': 0.2,       # minimum spread for a cut
        'min_projection_segments': 4,       # ++ less likely to cut ligs
        'low_projection_threshold': 0.5,     # allows a cut if valley under a certain value

        'slice_prioritization': 'Vertical',
        'check_axis': False,

        # Debug Options
        'print_projection_array': False,
        'plot_projection_array': False,  # script only
        'save_cuts': True,
    }

    # # for new manuscript
    # kwargs = {
    #     'smoothing': 1,
    #     'min_glyph_size': 20,
    #     'max_recursive_cuts': 50,
    #     'rotation': 45,

    #     # will it cut?
    #     'min_slice_spread_rel': 0.1,       # minimum spread for a cut
    #     'min_projection_segments': 4,       # ++ less likely to cut ligs
    #     'low_projection_threshold': 0.5,     # allows a cut if valley under a certain value

    #     'slice_prioritization': 'Vertical',
    #     'check_axis': False,

    #     # Debug Options
    #     'print_projection_array': False,
    #     'plot_projection_array': False,  # script only
    #     'save_cuts': True,
    # }

    ps = ProjectionSplitter(**kwargs)

    if inImage:

        image = image.to_onebit()
        image = ps._maybe_invert_image(image)
        cc_images = image.cc_analysis()
        cc_images = ps._filter_tiny_images(cc_images)

        output_glyphs = []
        for g in cc_images:
            output_glyphs += ps.run(g)

        # output_glyphs = ps.run(image)

        # save all as images
        for i, g in enumerate(output_glyphs):
            g.save_PNG('./output/piece' + str(i + 1) + '.png')

    elif inXML:

        output_glyphs = []
        for g in glyphs:
            output_glyphs += ps.run(g)

        gamera_xml.glyphs_to_xml('./output/output.xml', output_glyphs)

    # print('do stuff')
