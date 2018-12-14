from redis import Redis
from rq import Queue
import os


class RedisAccessor(object):
    REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')

    def __init__(self, queue_name='default', connection=None):
        connection = connection if connection is not None else Redis(self.REDIS_HOST)
        self.q = Queue(queue_name, connection=connection)

    def submit_job(self, func, args, kwargs=None, timeout='10m', job_id=None):
        job = self.q.enqueue_call(func=func, args=args, kwargs=kwargs, timeout=timeout,
                                  job_id=job_id)
        return job

    def get_job(self, job_id):
        job = self.q.fetch_job(job_id)
        return job

    def get_jobs(self, job_ids):
        jobs = [self.get_job(job_id) for job_id in job_ids]
        return [job for job in jobs if job is not None]
