import os
import imageio

from PIL import Image
from helpers.file_helpers import prepend_to_path, fp_list, optimize_gif


class GifProcessorError(Exception):
    pass


class GifSplitter(object):
    """
    Splits gifs into a directory of images
    """
    def __init__(self, path):
        self.in_path = path
        self.out_path = self.get_directory_name()
        self.image = Image.open(path)
        self.total_frames = 0
        self.contains_partials = self.is_partial()

    def is_partial(self):
        total_frames = 0
        partial_tile = False
        while True:
            try:
                if self.image.tile:
                    total_frames += 1
                    tile = self.image.tile[0]
                    region_dimensions = tile[2:]
                    if region_dimensions != self.image.size:
                        partial_tile = True
                self.image.seek(self.image.tell() + 1)
            except EOFError:
                break
        self.total_frames = total_frames
        self.image.seek(0)
        return partial_tile

    def get_directory_name(self):
        """construct directory name and create it if it doesn't exist"""
        path = self.in_path.split('.')[0]
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def get_frame_name(self, idx):
        basename = os.path.basename(self.out_path)
        path = 'Frame-{idx:03}-{base}.png'.format(idx=idx, base=basename)
        return os.path.join(self.out_path, path)

    def save_frames(self):
        # extract the palette and process first frame
        p = self.image.getpalette()
        prev = self.image.convert('RGBA')
        try:
            for idx in range(self.total_frames):
                img_path = self.get_frame_name(idx)

                if not self.image.getpalette():
                    self.image.putpalette(p)
                # create a new image to paste into
                current_frame = Image.new('RGBA', self.image.size)
                if self.contains_partials:
                    current_frame.paste(prev)

                current_frame.paste(self.image, (0, 0), self.image.convert('RGBA'))
                current_frame.save(img_path)

                prev = current_frame
                self.image.seek(self.image.tell() + 1)
        except EOFError:
            pass


class GifStitcher(object):
    MAX_SIZE = 1080

    def __init__(self, frame_directory, out_file=None):
        self.frame_directory = frame_directory
        self.out_file = out_file if out_file is not None else prepend_to_path(frame_directory + '.gif', 'new_gif')
        self.resize_frames()

    def resize(self, img):
        max_dim = max(img.size)
        if max_dim > self.MAX_SIZE:
            enlargement = self.MAX_SIZE / max_dim
            h, w = (int(enlargement * dim) for dim in img.size)
            img = img.resize((h, w), Image.ANTIALIAS)
        return img

    def resize_frames(self):
        for fp in fp_list(self.frame_directory):
            img = self.resize(Image.open(fp))
            img.save(fp)

    def make_gif(self, frame_duration=0.3, mode='I'):
        file_names = sorted(fp_list(self.frame_directory))
        with imageio.get_writer(self.out_file, mode=mode, duration=frame_duration) as writer:
            for file_name in file_names:
                image = imageio.imread(file_name)
                writer.append_data(image)
        optimize_gif(self.out_file)
