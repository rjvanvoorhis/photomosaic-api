import math
import os
import numpy as np


from PIL import Image
from photo_mosaic.progress_bar import parallel_process


class TileProcessor(object):
    DEFAULT_CONFIG = {
        'tile_size': 50,
        'tile_match_scale': 0.5,
        'img_type': 'RGB',
    }

    def __init__(self, tile_directory, tile_size=50, tile_match_scale=0.5, img_type='RGB'):
        self.tile_directory = tile_directory
        # self.tile_directory = 'tile_directories/characters'
        self.tile_size = tile_size
        self.img_type = img_type
        self.tile_match_size = math.ceil(tile_size * tile_match_scale)
        self.large_tile_list = []
        self.small_tile_list = []
        self.process_tile_directory()

    @staticmethod
    def get_file_list(directory):
        return [os.path.join(directory, fp) for fp in os.listdir(directory)]

    @staticmethod
    def crop_image(img):
        w, h = img.size
        min_dimension = min(w, h)
        w_crop = (w - min_dimension) // 2
        h_crop = (h - min_dimension) // 2
        crop_rectangle = (w_crop, h_crop, w-w_crop, h-h_crop)
        return img.crop(crop_rectangle)

    @staticmethod
    def rescale_image(img, tile_size):
        return img.resize((tile_size, tile_size), Image.ANTIALIAS)

    def process_tile_data(self, tile_path):
        img = Image.open(tile_path).convert(self.img_type)
        img = self.crop_image(img)
        large_tile = self.rescale_image(img, self.tile_size)
        small_tile = self.rescale_image(img, self.tile_match_size)
        tile_data = (np.array(large_tile), np.array(small_tile))
        return tile_data

    def process_tile_directory(self):
        tile_path_list = self.get_file_list(self.tile_directory)
        # args = zip(*[(self, fp) for fp in tile_path_list])
        progress = parallel_process(self.process_tile_data, tile_path_list, desc='Processing Tiles')
        for idx, data in progress:
            large, small = data
            self.large_tile_list.append(large)
            self.small_tile_list.append(small)

    def get_data(self):
        return self.large_tile_list, self.small_tile_list

