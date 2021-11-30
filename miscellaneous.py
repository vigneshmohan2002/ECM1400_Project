import time
import json
import sched

UpdateScheduler = sched.scheduler(time.time, time.sleep)


def json_processor(filename):
    """
    This function simply accepts the filename as a parameter so it may process
    the json file. This is mainly used for the config.json file.
    It returns a dictionary that is easily read by the other functions.
    """
    with open(filename, 'r') as f:
        file = json.load(f)
    return file


def hours_to_seconds(hours: str):
    """
    Converts hours to seconds
    """
    return int(hours) * 60 * 60


def minutes_to_seconds(minutes: str) -> int:
    """
    Converts minutes to seconds
    """
    return int(minutes) * 60


def hhmm_to_seconds(hhmm: str) -> int:
    """
    Converts time in HH:MM format to seconds
    """
    return (hours_to_seconds(hhmm.split(':')[0]) +
            minutes_to_seconds(hhmm.split(':')[1]))


def current_time_hhmm():
    """
    Gives the current time in HH:MM format
    """
    return str(time.gmtime().tm_hour) + ":" + str(time.gmtime().tm_min)


def required_interval(given_time):
    """
    Calculates the interval between the current time and the time accepted
    as a parameter.
    """
    return hhmm_to_seconds(current_time_hhmm()) - hhmm_to_seconds(given_time)
