from io import BytesIO
from PIL import Image, ImageSequence
from tempfile import TemporaryFile


def thumbnail_generator(frames, size):
    for frame in frames:
        thumbnail = frame.copy()
        thumbnail.thumbnail(size, Image.ANTIALIAS)
        yield thumbnail


def make_image_thumbnail(img, size=None):
    size = size if size is not None else (300, 300)
    new_img = img.copy()
    new_img.format = img.format
    new_img.info = img.info
    new_img.thumbnail(size, Image.ANTIALIAS)
    return new_img


class ImageStreamer(object):
    def __init__(self):
        self.stream = BytesIO()

    def dump_image_data(self, img):
        img.save(self.stream, img.format)
        img_data = self.stream.getvalue()
        self.stream.flush()
        return img_data

    def load_image(self, data):
        self.stream.write(data)
        self.stream.seek(0)
        img = Image.open(self.stream)
        self.stream.flush()
        return img

    def get_image_data(self, path):
        if path.lower().endswith('gif'):
            with open(path, 'rb') as fn:
                img_data = fn.read()
            return img_data
        img = Image.open(path)
        return self.dump_image_data(img)

    @staticmethod
    def make_gif_thumbnail(img, size):
        frames = ImageSequence.Iterator(img)
        frames = thumbnail_generator(frames, size)
        om = next(frames)
        om.info = img.info
        temp = TemporaryFile()
        om.save(temp, loop=0, format='gif', save_all=True, append_images=list(frames))
        temp.seek(0)
        img_data = temp.read()
        temp.close()
        return img_data

    def make_image_thumbnail(self, img, size):
        thumbnail = make_image_thumbnail(img, size)
        return self.dump_image_data(thumbnail)

    def dump_thumbnail_data(self, img, size=None):
        size = size if size is not None else (300, 300)
        if img.format is not None and img.format.lower() == 'gif':
            method = self.make_gif_thumbnail
        else:
            method = self.make_image_thumbnail
        return method(img, size)

    def get_image_thumbnail_data(self, path, size=None):
        img = Image.open(path)
        return self.dump_thumbnail_data(img, size)