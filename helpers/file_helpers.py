import os
import random
from werkzeug.utils import secure_filename
MEDIA_FOLDER = 'samples'


def optimize_gif(path):
    cmd = f'gifsicle_compression/gifsicle-static -O3 -b {path}'
    os.system(cmd)


def prepend_to_path(path, modifier):
    """
    create a modified filename like: path/to/filename.png > path/to/modified_filename.png
    :param path: original filepath
    :param modifier: modifier to add to begining of path
    :return: modified path
    """
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    return os.path.join(dirname, '{}_{}'.format(modifier, basename))


def fp_list(path):
    """
    Get a list of absolute filepaths
    :param path: path to directory
    :return: list of absolute filepaths
    """
    return [os.path.join(path, fp) for fp in os.listdir(path)]


def make_safe(path):
    random_head = str(random.random())[2:8]
    basename = '{}_{}'.format(random_head, secure_filename(path))
    fp = os.path.join(MEDIA_FOLDER, basename)
    if os.path.exists(fp):
        return make_safe(path)
    else:
        return fp


def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    fps = list(sorted(os.listdir(path), key=mtime))
    return [os.path.join(path, fp) for fp in fps]