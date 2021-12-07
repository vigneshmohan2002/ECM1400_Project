import time
import json
import sched

UpdateScheduler = sched.scheduler(time.time, time.sleep)


def json_processor(filename) -> dict:
    """
    This function simply accepts the filename as a parameter so it may process
    the json file. This is mainly used for the config.json file.
    It returns a dictionary that is easily read by the other functions.
    """
    with open(filename, 'r') as f:
        file = json.load(f)
    return file


def hours_to_seconds(hours: str) -> int:
    """
    Converts hours to seconds
    :param hours: Number of hours
    :return: Number of seconds in an hour
    """
    return int(hours) * 60 * 60


def minutes_to_seconds(minutes: str) -> int:
    """
    Converts minutes to seconds
    :param minutes: Number of minutes
    :return: Number of minutes in an hour
    """
    return int(minutes) * 60


def hhmmss_to_seconds(hhmmss: str) -> int:
    """
    Converts time in HH:MM:SS format to seconds
    :param hhmmss: Time in HH:MM:SS format
    :return: Number of seconds from 00:00:00 to the time
    """
    time_strings = hhmmss.split(":")
    return (hours_to_seconds(time_strings[0]) +
            minutes_to_seconds(time_strings[1]) +
            int(time_strings[2]))


def current_time_hhmmss() -> str:
    """
    Gives the current time in HH:MM:SS format
    :return: Time in HH:MM:SS format
    """
    return (str(time.gmtime().tm_hour) + ":" + str(time.gmtime().tm_min) + ":" +
                                                  str(time.gmtime().tm_sec))


def required_interval(given_time: str) -> int:
    """
    Calculates the interval between the current time and the time accepted
    as a parameter.
    :param given_time: Time given by user in HH:MM format
    :return: Number of seconds from current time to given time
    """
    scheduled_for = hhmmss_to_seconds(given_time+":00")
    current = hhmmss_to_seconds(current_time_hhmmss())
    if scheduled_for > current:
        return hhmmss_to_seconds(given_time+":00") - \
               hhmmss_to_seconds(current_time_hhmmss())
    else:
        return (hhmmss_to_seconds(given_time+":00") + 24*60*60) -\
               hhmmss_to_seconds(current_time_hhmmss())

