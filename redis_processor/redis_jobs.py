import os
import time
import shutil

from accessors.redis_accessor import RedisAccessor
from accessors.user_accessor import UserAccessor
from helpers.gif_processor import GifStitcher
from helpers.file_helpers import prepend_to_path
from photo_mosaic.photo_mosaic import PhotoMosaic


def make_mosaic(img, tile_directory, output_file, kwargs):
    print(kwargs)
    PhotoMosaic(img, tile_directory=tile_directory, output_file=output_file, **kwargs).save()
    return output_file


def poll_jobs(func, job_ids, kwargs, timeout=600):
    accessor = RedisAccessor()
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print('Timed out')
            return
        jobs = accessor.get_jobs(job_ids)
        still_running = [job for job in jobs if job.status != 'finished']
        if not still_running:
            func(**kwargs)
            print('Done.')
            return


def cleanup(username=None, mosaic_file=None, frame_directory=None, output_file=None, is_animated=True, frame_duration=0.1, mode='I'):
    if username is None:
        return
    if is_animated:
        mosaic_frames = prepend_to_path(frame_directory, 'Mosaic_of')
        stitcher = GifStitcher(mosaic_frames, output_file)
        stitcher.make_gif(frame_duration, mode)
        print('cleaning up directories with')
        for directory in [mosaic_frames, frame_directory]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
        print(output_file)
        UserAccessor().create_gallery_item(username, mosaic_file)
        print('done')
