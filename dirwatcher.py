#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = "Alex Mourtos"

import sys
import logging
import time
import signal
import argparse
import os
from datetime import datetime

# +++ Setting up logger +++
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()


# +++ ------------------------------------------------------------------- +++
# functions to set banners and timers for uptime
def start_banner():
    file = __file__.split("/")[-1]
    start_time = datetime.now()
    start_banner = (
        "\n" +
        "-" * 80 +
        f"\n\tRunning {file}" +
        f"\n\tStarted on {start_time.isoformat()}\n" +
        "-" * 80
    )
    logger.info(start_banner)
    return start_time


def end_banner(start_time):
    file = __file__.split("/")[-1]
    up_time = datetime.now() - start_time
    end_banner = (
        "\n" +
        "-" * 80 +
        f"\n\tStopping {file}" +
        f"\n\tUptime was {up_time}\n" +
        "-" * 80
    )
    logger.info(end_banner)
    return

# +++ ------------------------------------------------------------------- +++


exit_flag = False
store = dict()


def initial_fill(directory):
    """Fill the storage with all current files in directory"""
    try:
        for file in os.listdir(directory):
            store[file] = 0
    except OSError:
        logger.error(f"{directory} not found.")
    return


def detect_removed_files(directory):
    """Detection for removed files in the directory"""
    for file in list(store):
        if file not in os.listdir(directory):
            logger.info(f"{file} was removed from the directory")
            store.pop(file)
    return


def detect_added_files(directory):
    """Detection for additional files in the directory"""
    for file in os.listdir(directory):
        if file not in store.keys():
            logger.info(f"{file} was added to the directory")
            store[file] = 0


def search_for_magic(filename, start_line, magic_string):
    """Search files in directory for specified text"""
    # Your code here
    with open(filename, 'r') as file:
        content = file.readlines()
        for i, line in enumerate(content):
            if i >= start_line:
                if magic_string in line:
                    text_file = filename.split("/")[-1]
                    logger.info(
                        f"{magic_string} found on line {i+1} of {text_file}")
                    store[text_file] = i+1
    return


def watch_directory(path, magic_string, extension, interval):
    """Specifies the directory to watch"""
    # Your code here
    detect_added_files(path)
    detect_removed_files(path)
    for file in os.listdir(path):
        if extension is not None:
            if file.endswith(extension):
                search_for_magic(path+'/'+file, store.get(file), magic_string)
    return


def create_parser():
    """Creating parser arguments for command line"""
    # Your code here
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="Directory path to oversee")
    parser.add_argument('string', help="String to search for")
    parser.add_argument('--ext', default=".txt", nargs="?",
                        help="Text file extension to search")
    parser.add_argument('-i', default=1.0, type=float,
                        nargs="?", help="Set the time interval")
    return parser


def signal_handler(sig_num, frame):
    global exit_flag
    """Determines received signals for exiting program"""
    # Your code here
    logger.info('Received ' + signal.Signals(sig_num).name)
    if sig_num == 2:
        logger.info("User terminated program.")
        exit_flag = True
    if sig_num == 15:
        exit_flag = True
    return


def main(args):
    """Main function to run the program"""
    # Your code here
    start = start_banner()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = create_parser()
    ns = parser.parse_args(args)
    # +++ fill the store +++
    initial_fill(ns.path)
    # +++ check if input interval is invalid. If true, reassign to default +++
    polling_interval = ns.i
    if polling_interval < 0:
        logger.info("interval must be positive")
        logger.info("Interval changed to default of 1")
        polling_interval = 1.0

    while not exit_flag:
        time.sleep(polling_interval)
        try:
            watch_directory(ns.path, ns.string, ns.ext, ns.i)
        except KeyboardInterrupt:
            logger.warning('User is killing the program. Shutting down.')
        except ValueError as e:
            logger.warning(f'value Error found: {e}')
            pass
        except OSError:
            logger.warning(f"{ns.path} does not exist")
            pass
        except Exception as e:
            logger.error(f"Something went wrong: {e}")
            time.sleep(polling_interval)
    end_banner(start)
    return


if __name__ == '__main__':
    main(sys.argv[1:])
