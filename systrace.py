#!/usr/bin/env python2
"""
Prepares the device, invokes systrace.sh, collects traces, invokes psytrace and
prepares a zip in the right format for

"""

import datetime
import errno
import glob
import logging
import os
import subprocess
import sys
import zipfile
import argparse


SYSTRACE_PERIODIC_SLEEP_SECONDS_OUTSIDE_TRACE = 0
SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE = 1
SYSTRACE_PERIODIC_ITERATIONS = 4
LOG_LEVEL = logging.DEBUG


logger = logging.getLogger(__name__)

def os_remove(filepath):
    try:
        os.remove(filepath)
    except IOError as e:
        if (e.errno != errno.ENOENT):
            raise


def os_system(cmd):
    logger.debug("Running command %s" % repr(cmd))
    os.system(cmd)


def adb_cmd(cmd):
    return os_system("adb %s" % cmd)


def adb_shell(cmd):
    return adb_cmd('shell "%s"' % cmd)


def main():
    print("Running systrace.py with SYSTRACE_PERIODIC_ITERATIONS of {}".format(SYSTRACE_PERIODIC_ITERATIONS))
    print("systrace will last for approximately {} seconds.".format(SYSTRACE_PERIODIC_ITERATIONS*3.45))
    logging_format = "%(asctime).23s %(levelname)s:%(filename)s(%(lineno)d) [%(thread)d]: %(message)s"

    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(logging.Formatter(logging_format))
    logger.addHandler(logger_handler)
    logger.setLevel(LOG_LEVEL)

    logger.info("Waiting for a device")
    adb_cmd("wait-for-device")
    logger.info("Rooting")
    adb_cmd("root")
    logger.info("Waiting for root")
    adb_cmd("wait-for-device")

    logger.info("Creating on-device output directory")
    adb_shell("mkdir -p /data/local/tmp/traces")

    logger.info("Pushing systrace.sh")
    adb_cmd("push systrace.sh /data/local/tmp")
    adb_shell("chmod a+x /data/local/tmp/systrace.sh")

    logger.info("Capturing systrace")
    adb_shell("echo 'source /data/local/tmp/systrace.sh && "
              "SYSTRACE_PERIODIC_SLEEP_SECONDS_OUTSIDE_TRACE=%d "
              "SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE=%d "
              "SYSTRACE_PERIODIC_ITERATIONS=%d periodic_systrace "
              "> /data/local/tmp/traces/trace.log 2>&1' > /data/local/tmp/s.sh" %
              (SYSTRACE_PERIODIC_SLEEP_SECONDS_OUTSIDE_TRACE,
               SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE,
               SYSTRACE_PERIODIC_ITERATIONS))
    adb_shell("chmod a+x /data/local/tmp/s.sh")

    # nohup fails to run on complex command lines with redirection, parameters, etc
    # create an intermediate s.sh script with the complex invocation and run nohup
    # on the simple s.sh
    logger.info(
        "Tracing in background, disconnect device now if doing power measurements")
    adb_shell("cd /data/local/tmp && nohup /data/local/tmp/s.sh")

    logger.info("Waiting for the device to be available")
    adb_cmd("wait-for-device")

    logger.info("Removing existing traces from host")
    for filepath in glob.glob("traces/trace*.*"):
        os_remove(filepath)

    logger.info("Pulling traces from the device")
    adb_cmd("pull /data/local/tmp/traces/")

    logger.info("Invoking psytrace on the pulled traces")
    # On Unix the current directory is normally not part of the path, invoke
    # psytrace with the full path
    PSYTRACE_FILEPATH = os.path.dirname(os.path.realpath(__file__))
    PSYTRACE_FILEPATH = os.path.join(PSYTRACE_FILEPATH, "psytrace.py")
    for filepath in glob.glob("traces/*.txt"):
        os_system("py %s %s %s.out" % (PSYTRACE_FILEPATH, filepath, filepath))

    now = datetime.datetime.now()
    filepath = now.strftime("traces_%Y%m%d-%H%M%S_self_serve.zip")

    # run the parser program to extract desired information from logcat files
    os_system("python parser.py")
    
    logger.info("Creating zip file %s" % filepath)
    f_zip = zipfile.ZipFile(filepath, mode = "w", compression = zipfile.ZIP_DEFLATED)
    for filepath in glob.glob("traces/*.*"):
        f_zip.write(filepath, os.path.basename(filepath))


if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('time', type=int,
                        help='Specify the amount of time (seconds) to run systrace')
    args = parser.parse_args()
    time = args.time
    SYSTRACE_PERIODIC_ITERATIONS = round(time/3.45)
    main()
