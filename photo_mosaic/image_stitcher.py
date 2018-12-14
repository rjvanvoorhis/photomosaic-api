import numpy as np
import math

from PIL import Image
from photo_mosaic.hilbert import HilbertList


class ImageStitcher(object):
    def __init__(self, img, tile_size=8, enlargement=1, tile_rescale=1.0, img_type='RGB'):
        self.tile_size = tile_size
        self.enlargement = enlargement
        self.tile_rescale = tile_rescale
        self.img_type = img_type
        img = self.process_image(img)
        w_final, h_final = img.size
        self.cols = w_final//self.tile_size
        self.rows = h_final//self.tile_size
        small_img = np.array(self.get_small_img(img))
        large_img = np.array(img)

        self.large_image = HilbertList(self.pix_map_to_tile_mat(large_img))
        self.small_image = HilbertList(self.pix_map_to_tile_mat(small_img))

    def get_small_img(self, img):
        w_small = self.cols * math.ceil(self.tile_size*self.tile_rescale)
        h_small = self.rows * math.ceil(self.tile_size*self.tile_rescale)
        return img.resize((w_small, h_small), Image.ANTIALIAS)

    def process_image(self, img):
        w_original, h_original = img.size
        w_large = math.ceil(w_original * self.enlargement)
        h_large = math.ceil(h_original * self.enlargement)
        if w_large % 2 == 1:
            w_large -= 1
        if h_large % 2 == 1:
            h_large -= 1
        img = img.resize((w_large, h_large), Image.ANTIALIAS)
        w_crop, h_crop = [(side % self.tile_size) // 2 for side in (w_large, h_large)]
        if (w_crop + h_crop) > 0:
            img = img.crop((w_crop, h_crop, w_large-w_crop, h_large-h_crop))
        return img.convert(self.img_type)

    def pix_map_to_tile_mat(self, img):
        tiles = [np.split(row, self.cols, axis=1) for row in np.split(img, self.rows)]
        return tiles

    def get_data(self):
        return self.large_image, self.small_image

    def stitch_img(self):
        return self.large_image.stitch_img()
