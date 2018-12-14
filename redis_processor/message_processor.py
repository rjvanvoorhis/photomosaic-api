import os

from PIL import Image
from accessors.redis_accessor import RedisAccessor
from redis_processor.redis_jobs import make_mosaic, poll_jobs, cleanup
from helpers.gif_processor import GifSplitter
from helpers.file_helpers import prepend_to_path, sorted_ls
from objects.message import Message


class MessageProcessor(object):
    DEFAULT_GIF_FRAMES = 50
    VALID_TILE_DIRECTORIES = [
        'tile_directories/characters'
    ]
    DEFAULT_TIMEOUT = 1000

    def __init__(self):
        self.redis_accessor = RedisAccessor()

    @staticmethod
    def process_gif(path):
        splitter = GifSplitter(path)
        splitter.save_frames()
        original_frames = splitter.out_path
        mosaic_frames = prepend_to_path(original_frames, 'Mosaic_of')
        if not os.path.exists(mosaic_frames):
            os.mkdir(mosaic_frames)
        total_frames = len(os.listdir(original_frames))
        gif_name = prepend_to_path(path, 'Mosaic_of')
        mosaic_path = gif_name
        path_pairs = []
        for fp in sorted_ls(original_frames):
            new_fp = os.path.join(mosaic_frames, os.path.basename(fp))
            path_pairs.append((fp, new_fp))
        return mosaic_path, gif_name, original_frames, mosaic_frames, total_frames, path_pairs

    @staticmethod
    def process_image(path):
        basename = os.path.basename(path).split('.')[0]
        dirname = os.path.dirname(path)
        frame_directory = os.path.join(dirname, basename)
        mosaic_path = prepend_to_path(path, 'Mosaic_of')
        mosaic_frames = prepend_to_path(frame_directory, 'Mosaic_of')
        gif_name = mosaic_frames + '.gif'
        total_frames = MessageProcessor.DEFAULT_GIF_FRAMES
        path_pairs = [(path, mosaic_path)]
        return mosaic_path, gif_name, frame_directory, mosaic_frames, total_frames, path_pairs

    @staticmethod
    def set_tile_directory(tile_directory):
        if tile_directory not in MessageProcessor.VALID_TILE_DIRECTORIES:
            tile_directory = MessageProcessor.VALID_TILE_DIRECTORIES[0]
        return tile_directory

    @staticmethod
    def build_path_pair(path, out_directory):
        basename = os.path.basename(path)
        out_path = os.path.join(out_directory, basename)
        return path, out_path

    def setup_image(self, path, frame_duration, mode, username):
        is_animated = path.lower().endswith('gif')
        method = self.process_gif if is_animated else self.process_image
        mosaic_path, gif_name, frame_directory, mosaic_frames, total_frames, path_pairs = method(path)
        cleanup_kwargs = {
            'mosaic_file': mosaic_path,
            'username': username,
            'frame_directory': frame_directory,
            'output_file': gif_name,
            'frame_duration': frame_duration,
            'mode': mode
        }
        return path_pairs, total_frames, cleanup_kwargs

    def build_jobs(self, path_pairs, tile_directory, kwargs):
        job_list = []
        for in_path, out_path in path_pairs:
            img = Image.open(in_path)
            arg_list = [img, tile_directory, out_path, kwargs]
            job = self.redis_accessor.submit_job(make_mosaic, arg_list)
            job_list.append(job.get_id())
        return job_list

    def create_message(self, username, path, tile_directory=None, enlargement=1, tile_size=8, tile_rescale=1.0,
                       threads=3, img_type='L', max_repeats=0, method='euclid', frame_duration=0.1,
                       mode='I'):
        tile_directory = self.set_tile_directory(tile_directory)
        path_pairs, total_frames, cleanup_kwargs = self.setup_image(path, frame_duration, mode, username)
        save_intermediates = not path.lower().endswith('gif')
        kwargs = {
            'enlargement': enlargement,
            'tile_size': tile_size,
            'tile_rescale': tile_rescale,
            'threads': threads,
            'img_type': img_type,
            'max_repeats': max_repeats,
            'method': method,
            'save_intermediates': save_intermediates
        }
        jobs = self.build_jobs(path_pairs, tile_directory, kwargs)
        poll_args = [cleanup, jobs, cleanup_kwargs, self.DEFAULT_TIMEOUT]
        self. redis_accessor.submit_job(poll_jobs, args=poll_args)
        message = Message(path, total_frames, self.DEFAULT_TIMEOUT)
        return message
