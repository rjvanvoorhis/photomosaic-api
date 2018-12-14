import time
import uuid
import os
from helpers.file_helpers import sorted_ls, prepend_to_path


class Message(object):
    def __init__(self, path, total_frames, timeout=1000):
        self.original_file = path
        self.frame_directory = self.set_frame_directory()
        self.output_file = self.set_output_file()
        self.gif_name = self.set_gif_name()
        self.current = path
        self.is_animated = path.lower().endswith('gif')
        self.status = 'queued'
        self.expire_at = time.time() + timeout + 120
        self.message_id = str(uuid.uuid4())
        self.total_frames = max(total_frames, 1)
        self.progress = 0

    def set_frame_directory(self):
        basename = self.original_file.split('.')[0]
        return prepend_to_path(basename, 'Mosaic_of')

    def set_output_file(self):
        return prepend_to_path(self.original_file, 'Mosaic_of')

    def set_gif_name(self):
        return self.frame_directory + '.gif'

    def set_status(self):
        if self.status == 'finished':
            return
        if os.path.exists(self.output_file):
            self.status = 'finished'
        elif time.time() > self.expire_at:
            self.status = 'failed'
        elif os.path.exists(self.frame_directory):
            self.status = 'running'
        elif self.status != 'queued':
            self.status = 'failed'

    def get_current(self):
        self.set_status()
        if self.status == 'finished':
            self.current = self.output_file
            self.progress = 1
        elif os.path.exists(self.frame_directory) and os.listdir(self.frame_directory):
            sorted_fps = sorted_ls(self.frame_directory)
            self.progress = len(sorted_fps) / self.total_frames
            self.current = os.path.join(self.frame_directory, sorted_fps[-1])

    def jsonify(self):
        return self.__dict__

    @classmethod
    def load_from_document(cls, message_json):
        if '_id' in message_json:
            del message_json['_id']
        rv = cls(message_json['original_file'], message_json['total_frames'])
        rv.expire_at = message_json['expire_at']
        rv.status = message_json['status']
        rv.get_current()
        return rv
