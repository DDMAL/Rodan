import sys

from gamera.core import init_gamera, load_image, RGBPixel
from gamera.plugins.image_utilities import union_images


init_gamera()


class DirtyLayerRepairman(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.despeckle_size = kwargs['despeckle_size']
        self.density = kwargs['density']

    def run(self, base, dirty):
        # just in case
        base = base.to_onebit()
        dirty = dirty.to_onebit()

        # save a copy of the original just in case
        orig_image = dirty.image_copy()

        # preprocessing
        # remove smudges and skips
        bg_image = self._get_background(dirty)
        proc_image = self._remove_high_density_CCs(dirty, bg_image)

        # get the inverse
        output_dirt = self._XOR_images(orig_image, proc_image)

        # combine dirt with base image
        base.or_image(output_dirt, True)

        # post processing
        output_image = self._despeckle_image(base)

        return output_image

    def _get_background(self, image):
        # returns a white canvas of the original image size
        output = image.image_copy()
        output.fill(RGBPixel(0, 0, 0))
        return output

    def _despeckle_image(self, image):
        image.despeckle(self.despeckle_size)
        return image

    def _remove_high_density_CCs(self, image, bg):
        CCs = image.cc_analysis()
        new_CCs = []

        for g in CCs:
                # throw away glyphs
            if g.compactness()[0] >= self.density:
                continue
            else:
                new_CCs.append(g)

        combine = union_images([bg] + new_CCs)
        return combine

    def _XOR_images(self, image1, image2):
        return image1.xor_image(image2)


if __name__ == "__main__":
    inImage, inImage2 = None, None

    if len(sys.argv) == 3:
        inImage = sys.argv[1]
        inImage2 = sys.argv[2]

    if inImage and inImage2:
        dirty = load_image(inImage)
        base = load_image(inImage2)

        kwargs = {
            'despeckle_size': 500,
            'density': 0.3,
        }

        dlr = DirtyLayerRepairman(**kwargs)
        image = dlr.run(base, dirty)

        image.save_PNG('./output/clean_neumes.png')
