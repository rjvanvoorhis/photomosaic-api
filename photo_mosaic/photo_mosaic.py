import numpy as np
import time
import os

from PIL import Image

from photo_mosaic.image_stitcher import ImageStitcher
from photo_mosaic.tile_processor import TileProcessor
from photo_mosaic.progress_bar import parallel_process


def get_unique_fp():
    return 'mosaic_{}.jpg'.format(int(time.time() * 1000))


def euclid(t1, t2):
    diff = np.sum((t1 - t2) ** 2)
    return diff


def city_block(t1, t2):
    diff = np.sum(np.fabs(t1 - t2))
    return diff


class SimpleQueue:
    def __init__(self, max_length=0):
        self.queue = []
        self.max_length = max_length

    def __bool__(self):
        return bool(self.queue)

    def __contains__(self, item):
        return item in self.queue

    def put(self, item):
        self.queue.insert(0, item)
        self.queue = self.queue[0: self.max_length]

    def pop(self):
        if not self:
            return None
        return self.queue.pop()


class ComparisonMethod(object):
    def __init__(self, func):
        self.function = func

    def __call__(self, t1, t2):
        t1 = t1.astype(np.int32)
        t2 = t2.astype(np.int32)
        diff = self.function(t1, t2)
        return diff


class PhotoMosaic(object):
    MAX_SIZE = 2500
    MAX_GIF_SIZE = 800
    COMPARISON_CONFIG = {
        'euclid': euclid,
        'city_block': city_block
    }
    """
    The class that builds the photo-mosaic
    """
    def __init__(self, img, tile_directory=None, enlargement=1, tile_size=8, tile_rescale=1.0,
                 output_file=None, method=euclid, threads=5, img_type='RGB', max_repeats=0,
                 intermediate_frames=50, save_intermediates=False):
        enlargement = self.set_enlargement(img, enlargement)
        self.method = self.get_method(method)
        self.save_intermediates = save_intermediates
        self.save_intermediate_frames = intermediate_frames
        kwargs = {'enlargement': enlargement, 'tile_size': tile_size,
                  'tile_rescale': tile_rescale, 'img_type': img_type}
        self.large_image, self.small_image = self.get_image_data(img, kwargs)

        # for multiprocessing
        self.threads = max(threads, 1)
        self.chunksize = len(self.large_image) // self.threads

        self.repeat_queue = SimpleQueue(max_length=max_repeats)
        self.output_file = output_file if output_file is not None else get_unique_fp()

        tiles = TileProcessor(tile_directory, tile_size, tile_match_scale=tile_rescale, img_type=img_type)
        self.large_tile_data, self.small_tile_data = tiles.get_data()
        self.pix_map = self.process_mosaic()

    def set_enlargement(self, img, enlargement):
        h, w = (enlargement * dim for dim in img.size)
        if any(dim > self.MAX_SIZE for dim in (h, w)):
            enlargement = int(self.MAX_SIZE / (max(h, w) ) * enlargement)

        print(h, w)
        print(enlargement)
        return enlargement

    @staticmethod
    def get_image_data(img, kwargs):
        return ImageStitcher(img, **kwargs).get_data()

    def get_image(self):
        return Image.fromarray(self.pix_map)

    def save(self, output_file=None):
        output_file = output_file if output_file is not None else self.output_file
        img = self.get_image()
        img.save(output_file)

    def process_mosaic(self):
        self.replace_tiles()
        return self.large_image.stitch_img()

    def get_best_fit_tile(self, tile):
        best_fit_tile = 0
        min_diff = float('inf')
        for idx, tile_data in enumerate(self.small_tile_data):
            if idx in self.repeat_queue:
                continue
            diff = self.method(tile_data, tile)
            if diff < min_diff:
                min_diff = diff
                best_fit_tile = idx
        return best_fit_tile

    def set_up_intermediates(self):
        intermediates = max(len(self.large_image) // self.save_intermediate_frames, 1)
        basename = os.path.basename(self.output_file).split('.')[0]
        new_dir = os.path.join(os.path.dirname(self.output_file), basename)
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        return new_dir, intermediates

    @staticmethod
    def resize_image(img, max_size):
        max_dim = max(img.size)
        if max_dim > max_size:
            enlargement = max_size / max_dim
            h, w = (int(enlargement * dim) for dim in img.size)
            img = img.resize((h, w), Image.ANTIALIAS)
        return img

    def save_intermediate_frame(self, frame_directory, idx):
        base = os.path.basename(self.output_file)
        fp = os.path.join(frame_directory, '{idx:06}-{base}'.format(idx=idx, base=base))
        pix_map = self.large_image.stitch_img()
        img = self.resize_image(Image.fromarray(pix_map), self.MAX_GIF_SIZE)
        img.save(fp)

    def replace_tiles(self):
        progress = parallel_process(self.get_best_fit_tile, self.small_image, max_workers=self.threads,
                                    desc='Building Mosaic ', chunksize=self.chunksize)
        results = [item for item in progress]
        save_on_idx, frames = (len(self.small_image) + 1, None)
        if self.save_intermediates:
            frames, save_on_idx = self.set_up_intermediates()
        for idx, best_tile in results:
            self.large_image[idx] = self.large_tile_data[best_tile]
            if self.save_intermediates and (idx % save_on_idx == 0 or idx == len(results) - 1):
                self.save_intermediate_frame(frames, idx)

    def get_method(self, method):
        if callable(method):
            method = method
        elif method is None or method not in self.COMPARISON_CONFIG:
            method = euclid
        else:
            method = self.COMPARISON_CONFIG[method]
        return ComparisonMethod(func=method)


def make_mosaic(img, tile_directory, output_file, kwargs):
    print(kwargs)
    PhotoMosaic(img, tile_directory=tile_directory, output_file=output_file, **kwargs).save()
    return output_file
