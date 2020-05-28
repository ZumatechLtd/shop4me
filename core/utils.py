import pytz
import time
from datetime import datetime

default_date_format = '%Y/%m/%d'


def epoch_timestamp_from_date(date):
    return int(time.mktime(date.timetuple()))


def datetime_from_date_string(date_string, date_format=default_date_format):
    return datetime.strptime(date_string, date_format)


def date_string_from_datetime_object(datetime_obj, date_format=default_date_format):
    return datetime_obj.strftime(date_format)


def epoch_timestamp_from_date_string(date_string, date_format=default_date_format):
    return datetime_from_date_string(date_string, date_format).timestamp()


def datetime_string_from_epoch_timestamp(epoch_timestamp, date_format=default_date_format):
    return datetime.strftime(datetime_from_epoch_timestamp(epoch_timestamp), date_format)


def datetime_from_epoch_timestamp(epoch_timestamp):
    return datetime.fromtimestamp(epoch_timestamp)


def localized_datetime_from_epoch_timestamp(epoch_timestamp, timezone='Europe/London'):
    bst = pytz.timezone(timezone)
    naive_datetime = datetime_from_epoch_timestamp(epoch_timestamp)
    return pytz.utc.localize(naive_datetime).astimezone(bst)
