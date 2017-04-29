# -*- coding: utf-8 -*-

""" serverlog.
"""

from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime, timedelta
import signal
import argparse
import json


class Job:
    time_offset = timedelta(seconds=1)

    def __init__(self, cycle, job_callback):
        self.cycle= cycle
        self.job_callback = job_callback
        self.next_time = datetime.utcnow()

    def check_and_do_job(self):
        now = datetime.utcnow() + self.time_offset
        if now > self.next_time:
            self.job_callback()
            # subp.call(['zbackup.sh',self.dataset,self.rot])
            self.next_time = ((now - self.next_time)//self.cycle + 1) * self.cycle
        return self.next_time


job_queue = []
def do_jobs():
    sleep_until = min(x.check_and_do_job() for x in job_queue)
    sleep_time_int = int((sleep_until-datetime.utcnow()).total_seconds())
    signal.alarm(max(sleep_time_int,1))

config_file_path = ''
def load_config_file():
    with open(config_file_path) as f:
        config = json.load(f)

    job_queue.clear()
    for job in config.get('jobs', []):
        pass

def set_signal_handler():
    signal.signal(signal.SIGALRM, do_jobs)
    signal.signal(signal.SIGUSR1, load_config_file)

def start_service():
    load_config_file()
    while True:
        signal.pause()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    		description='Server status or service status logging service.')
    parser.add_argument('-d','--deamon',
                        dest='is_deamon',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Run the service in deamon mond.')
    parser.add_argument('-c','--config',
                        dest='config',
                        default='/usr/local/etc/serverlog.conf',
                        help='The path of the configuration file.')
    parser.add_argument('-p','--pid',
                        dest='pidfile',
                        default='/var/run/serverlog.pid',
                        help='The path of the pid file.')

    args = parser.parse_args()
    if args.is_deamon:
        pid = os.fork()
        if pid != 0:
            with open(args.pidfile, 'w') as pidfile:
                pidfile.write('%d' % pid)
            exit(0)
    config_file_path = args.config
    start_service()
