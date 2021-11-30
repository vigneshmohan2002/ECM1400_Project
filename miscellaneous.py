import time
import json
import sched

UpdateScheduler = sched.scheduler(time.time, time.sleep)


def json_processor(filename):
    with open(filename, 'r') as f:
        file = json.load(f)
    return file


def hours_to_seconds(hours: str):
    """Converts hours to seconds"""
    return int(hours) * 60 * 60


def minutes_to_seconds(minutes: str) -> int:
    """Converts minutes to seconds"""
    return int(minutes) * 60


def hhmm_to_seconds(hhmm: str) -> int:
    return (hours_to_seconds(hhmm.split(':')[0]) +
            minutes_to_seconds(hhmm.split(':')[1]))


def current_time_hhmm():
    return str(time.gmtime().tm_hour) + ":" + str(time.gmtime().tm_min)


def required_interval(given_time):
    return hhmm_to_seconds(current_time_hhmm()) - hhmm_to_seconds(given_time)
