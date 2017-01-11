#!/usr/bin/env python

import os
import subprocess
from datetime import datetime
import ConfigParser
import logging
import logging.config


def remove_empty_dirs(top_dir_path):  # https://gist.github.com/jacobtomlinson/9031697
    if not os.path.isdir(top_dir_path):
        return

    for entry in os.listdir(top_dir_path):
        path = os.path.join(top_dir_path, entry)
        if os.path.isdir(path):
            remove_empty_dirs(path)

    if len(os.listdir(top_dir_path)) == 0:
        os.rmdir(top_dir_path)
        logging.debug('%s removed', top_dir_path)


def remove_old_metrics(top_dir_path, min_retention):  # http://stackoverflow.com/a/36014898
    for dir_path, _, filenames in os.walk(top_dir_path):
        for filename in filenames:
            try:
                now = datetime.now()
                file_path = os.path.join(dir_path, filename)
                timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
                age = (now - timestamp).total_seconds()
                if age > min_retention:
                    max_retention = int(subprocess.check_output(['whisper-info', file_path, 'maxRetention']))
                    if age > max_retention:
                        os.remove(file_path)
                        logging.debug('%s (%s) removed', file_path, timestamp)
            except Exception as e:
                logging.error('%s', e)
                pass


def main():
    config = ConfigParser.RawConfigParser()
    config.read('application.conf')
    whisper_home = config.get('application', 'whisper_home')
    min_retention = config.get('application', 'min_retention')
    
    logging.config.fileConfig('logging.conf')

    start_time = datetime.now()
    logging.info('Started with whisper_home=%s and min_retention=%s', whisper_home, min_retention)

    if os.path.isdir(whisper_home):
        remove_old_metrics(whisper_home, min_retention)
        remove_empty_dirs(whisper_home)
    else:
        logging.critical("%s does not exists or is not a directory", whisper_home)

    finish_time = datetime.now()
    logging.info('Finished, time consumed: %s', finish_time - start_time)

if __name__ == '__main__':
    main()
