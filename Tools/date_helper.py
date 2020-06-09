# -*- coding: utf-8 -*-
"""
时间日期的转化文件
"""
import time
import math
import pytz
import datetime
from dateutil.rrule import *
from dateutil.parser import parse
from collections import OrderedDict
from itertools import islice
from datetime import timedelta
from dateutil import parser
tz = pytz.timezone(pytz.country_timezones('cn')[0])


def get_date_by_days(days=1, time_type="%Y-%m-%dT H:%M:%S"):
    """
    获取 多少天 之前 的日期
    :param days:
    :param time_type:
    :return:
    """
    # 格式化为 年 月 日
    # return (datetime.date.today() - timedelta(days=days)).strftime(time_type)
    # 格式化为 年 月 日 时 分 秒
    return (datetime.datetime.now() - timedelta(days=days)).strftime(time_type)


def get_current_iso_date():
    now_str = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time()))
    ISODate = parser.parse(now_str)
    return ISODate


# @return: 当前的datetime时间戳
def now_dt():
    return datetime.datetime.now()


# 当前时间
def current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def current_day():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def current_mth():
    return datetime.datetime.now().strftime('%Y-%m')


def current_week_days(return_type="date"):
    """
    根据当前时间，获取当前周的时间列表

    :param return_type:
    :return:
    """
    today_dt = now_dt()
    dates = [today_dt + datetime.timedelta(days=i) for i in range(0 - today_dt.weekday(), 7 - today_dt.weekday())]
    if return_type == "day_str":
        dates = [each_dt.strftime("%Y-%m-%d") for each_dt in dates]
    if return_type == "tsp":
        dates = [dt_to_unix_timestamp(datetime.datetime(year=each_dt.year, month=each_dt.month, day=each_dt.day))
                 for each_dt in dates]

    return dates


def current_timestamp():
    current_timestamp_var = int(time.time()*1000)

    return current_timestamp_var


# @return: 当前的date
def now_date():
    return datetime.datetime.now().date()


# @return: 返回1970.01.01，datetime类型
def null_dt():
    return datetime.datetime(1970, 1, 1)


# @return: 返回1970.01.01，date类型
def null_date():
    return datetime.date(1970, 1, 1)


# @param: 输入日期格式，
# @return: datetime类型
def get_dt(dt_str="1970-01-01 00:00:00", dt_format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(dt_str, dt_format)


# @param: 输入日期格式，
# @return: date类型
def get_date(date_str="1970-01-01", dt_format='%Y-%m-%d'):
    return get_dt(date_str, dt_format).date()


def get_dt_day(dt, dt_format='%Y-%m-%d'):
    return dt.strftime(dt_format)


# @param: datetime
# @return: string类型
def get_dt_mth(dt, dt_format='%Y-%m'):
    return dt.strftime(dt_format)


# @param: datetime
# @return: string类型
def get_dt_str(dt, dt_format="%Y-%m-%d %H:%M:%S"):
    return dt.strftime(dt_format)


def timestamp_tran_date_str(timestamp):
    """
    时间戳转化成字符型日期格式
    :return: 字符型日期格式
    """
    return time.strftime('%Y-%m-%d', time.localtime(timestamp/1000))


def date_str_tran(date_str):
    """
    将字符串格式时间转成 timestamp 13位格式
    :param date_str: 需要转换的时间
    :return: datetime
    """
    try:
        date_tuple = time.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        timestamp = int(time.mktime(date_tuple)*1000)
    except Exception as e:
        print(e)
        timestamp = None
    return timestamp


def timestamp_str_tran(timestamp):
    """
    将字符串格式的时间戳 转成 日期格式
    :param timestamp:
    :return:
    """
    if timestamp:
        try:
            time_array = time.localtime(int(timestamp) / 1000)
            date = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        except Exception as e:
            print(e)
    else:
        date = "None"
    return date


def date_str_transfer_timestamp(date_str):
    tstamp = None
    if date_str:
        tstamp = int(time.mktime(time.strptime(date_str, '%Y-%m-%d'))*1000)

    return tstamp


def time_str_transter_timestamp(date_str, time_format='%Y-%m-%d %H:%M:%S'):
    tstamp = None
    if date_str:
        tstamp = int(time.mktime(time.strptime(date_str, time_format)) * 1000)

    return tstamp


# 时间区间列表
# 参数目前mins_delta 默认间隔60分钟
# 00:00:00-01:00:00 含义为在区间00:00:00<=x< 01:00:00
def create_time_zone_range(mins_delta=60):
    time_list = list(rrule(MINUTELY, interval=mins_delta, dtstart=parse('1970-01-01'), until=parse('1970-01-02')))
    time_str_list = [tl.strftime("%H:%M:%S") for tl in time_list]

    time_period_list = []
    for i in range(0, len(time_str_list)):
        for j in range(i+1, len(time_str_list)):
            time_period = time_str_list[i]+'-'+time_str_list[j]
            time_period_list.append(time_period)
            break

    return time_period_list


# 返回时间所属区间段, 区间段可自行设置时间间隔, 默认区间为60
# 如'2013-04-18 7:20:00' -> 7:00:00-8:00:00
def get_time_period(date_time, mins_delta=60):
    time_period_list = create_time_zone_range(mins_delta)
    time_str = date_time.split(' ')[1]
    period_return = ''
    for index, time_period in enumerate(time_period_list):
        st_time = time_period.split('-')[0]
        et_time = time_period.split('-')[1]
        lower_bound = time_to_sec(time_str)-time_to_sec(st_time)
        upper_bound = time_to_sec(et_time)-time_to_sec(time_str)

        if lower_bound >= 0 and upper_bound > 0:
            period_return = time_period_list[index]
        elif (lower_bound >= 0) and (upper_bound < 0):
            period_return = time_period_list[index]

    return period_return


def date_time_to_sec(date_time):
    date_time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    init_date = datetime.date(1970, 1, 1)
    each_date = datetime.date(date_time.year, date_time.month, date_time.day)
    delta_days = each_date-init_date
    date_time_sec = datetime.timedelta(delta_days.days,
                                       hours=date_time.hour,
                                       minutes=date_time.minute,
                                       seconds=date_time.second).total_seconds()
    return date_time_sec


def date_to_sec(date_time):
    date_time = datetime.datetime.strptime(date_time, '%Y-%m-%d')
    init_date = datetime.date(1970, 1, 1)
    each_date = datetime.date(date_time.year, date_time.month, date_time.day)
    delta_days = each_date-init_date
    date_time_sec = datetime.timedelta(delta_days.days).total_seconds()
    return date_time_sec


def sec_to_date(sec, format='%Y-%m-%d'):
    return datetime.datetime.fromtimestamp(float(sec)).strftime(format)


def mth_time_to_sec(date_time):
    date_time = datetime.datetime.strptime(date_time, '%Y-%m')
    init_date = datetime.date(1970, 1, 1)
    each_date = datetime.date(date_time.year, date_time.month, date_time.day)
    delta_days = each_date-init_date
    date_time_sec = datetime.timedelta(delta_days.days).total_seconds()
    return date_time_sec


def time_to_sec(time_str):
    hms = datetime.datetime.strptime(time_str, '%H:%M:%S')
    hms_sec = datetime.timedelta(hours=hms.hour, minutes=hms.minute, seconds=hms.second).total_seconds()
    return hms_sec


# 两个时间相减得到的秒数
def date_time_span(date_time_1, date_time_2):
    spac_sec = date_time_to_sec(date_time_1) - date_time_to_sec(date_time_2)
    return spac_sec


# 两个时间相减得到的天数
def day_used(date_time_1, date_time_2):
    day_span_days = 0
    if date_time_1 and date_time_2:
        day_span_days = date_time_span(date_time_1, date_time_2)/float(3600*24)
        day_span_days = math.ceil(day_span_days)
        if day_span_days == 0:
            day_span_days = 1
    return int(day_span_days)


# 输出按照顺序的set
def ordered_set_list(need_list):
    d = OrderedDict()
    for x in need_list:
        d[x] = True
    ordered_list = [i for i in d]
    return ordered_list


# unix timestamp转datetime
def unix_timestamp_to_dt(ts, div=1000):
    m = time.localtime(1.0 * ts / div)
    ms = "%s-%s-%s %s:%s:%s" % (m.tm_year, m.tm_mon, m.tm_mday, m.tm_hour, m.tm_min, m.tm_sec)
    return get_dt(ms)


def unix_timestamp_to_date(ts, div=1000):
    m = time.localtime(1.0 * ts / div)
    ms = "%s-%s-%s" % (m.tm_year, m.tm_mon, m.tm_mday)
    return ms


def utc_dt():
    x = datetime.datetime.now(tz=pytz.UTC)
    return x


# datetime转unix timestamp
def dt_to_unix_timestamp(dt):
    return int(time.mktime(dt.timetuple())*1000)


# @return: 当前的datetime时间戳
def now_utc():
    return datetime.datetime.now(tz)


def mth_between(st_mth, et_mth):
    mth_format = "%Y-%m"
    st_mth_dt = datetime.datetime.strptime(st_mth, mth_format)
    et_mth_dt = datetime.datetime.strptime(et_mth, mth_format)
    tgt_list = list(rrule(MONTHLY, dtstart=st_mth_dt).between(st_mth_dt, et_mth_dt, inc=True))
    full_mth_list = [mth_dt.strftime(mth_format) for mth_dt in tgt_list]
    return full_mth_list


def day_between(st_day, et_day):
    day_format = "%Y-%m-%d"
    st_dy_dt = datetime.datetime.strptime(st_day, day_format)
    et_dy_dt = datetime.datetime.strptime(et_day, day_format)

    tgt_list = list(rrule(DAILY, dtstart=st_dy_dt).between(st_dy_dt, et_dy_dt, inc=True))
    full_day_list = [dy_dt.strftime(day_format) for dy_dt in tgt_list]

    return full_day_list


def day_pair(st, et):
    def n_grams(a, n):
        z = (islice(a, i, None) for i in range(n))

        return zip(*z)

    tars_gz = []
    if st and et:
        day_list = day_between(st_day=st, et_day=et)
        tar_dates = n_grams(a=day_list, n=2)

        tars_gz = [each_pair for each_pair in tar_dates]

    return tars_gz


def local2utc(local_st):
    """
    本地时间转UTC时间（-8:00）
    :param local_st: 本地时间， str类型
    :return: UTC时间， str类型
    """
    time_struct = time.mktime(datetime.datetime.strptime(local_st, "%Y-%m-%d %H:%M:%S").timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st.strftime("%Y-%m-%d %H:%M:%S")


def get_updt(utc_timestamp, div=1):
    """
    把utc timestamp 转换成UTC datetime

    :param utc_timestamp:
    :param div
    :return: UTC datetime
    """
    _utc_dt = ""
    if utc_timestamp:
        _utc_dt = unix_timestamp_to_dt(utc_timestamp, div=div)

    return _utc_dt


def utc_dt_to_local_str(dt_utc):
    """
    UTC datetime转成本地时间

    :param dt_utc: UTC datetime类型
    :return: local datatime string
    """
    dt_str = ""
    if dt_utc:
        _tz = pytz.timezone(pytz.country_timezones('cn')[0])
        dt_tz = datetime.datetime(year=dt_utc.year, month=dt_utc.month, day=dt_utc.day, hour=dt_utc.hour,
                                  minute=dt_utc.minute, second=dt_utc.second, tzinfo=pytz.utc).astimezone(_tz)

        dt_str = dt_tz.strftime('%Y-%m-%d %H:%M:%S')

    return dt_str


def validate_time_format(date_text, format='%Y-%m-%d'):
    try:
        datetime.datetime.strptime(date_text, format)
        return True
    except:
        # raise ValueError("Incorrect data format, should be %s" % format)
        print("Incorrect data format, should be %s" % format)
        return False


def unix_timestamp_to_dt_str(ts, div=1000):
    m = time.localtime(1.0 * ts / div)
    ms = "%s-%s-%s %s:%s:%s" % (m.tm_year, m.tm_mon, m.tm_mday, m.tm_hour, m.tm_min, m.tm_sec)
    return ms


def date_num_str_tra_timestamp(date_num_str):
    date_stamp = ""
    if date_num_str and len(date_num_str) == 8:
        date_str = "%s-%s-%s" % (date_num_str[:4], date_num_str[4:6], date_num_str[6:8])
        date_time = time.strptime(date_str, "%Y-%m-%d")
        date_stamp = int(time.mktime(date_time)*1000)
    return date_stamp


def now_timestamp():
    return int(time.time()*1000)


def timestamp_tran_datetime_str(timestamp):
    """
    时间戳转化成字符型日期格式
    :return: 字符型日期格式
    """
    return time.strftime('%m-%d %H:%M:%S', time.localtime(timestamp/1000))


def timestamp_tran_time_str(timestamp):
    """
    时间戳转化成字符型时间格式
    :return: 字符型日期格式
    """
    return time.strftime('%H:%M:%S', time.localtime(timestamp/1000))


def timestamp_tran_minute_str(timestamp):
    """
    时间戳转化成字符型时间格式
    :return: 字符型日期格式
    """

    return time.strftime('%H:%M', time.localtime(timestamp/1000))


if __name__ == "__main__":
    # print date_time_to_sec("2015-01-01 10:20:20")
    # print date_to_sec("2015-01-01")
    # print mth_time_to_sec("2015-01")
    # print time_to_sec("10:20:20")
    # print mth_between("2014-12", "2015-02")
    # print find_span_trans_date([])
    # print validate_time_format("2015-01-01 10")
    # print mth_used("", "")
    # print current_week_days(return_type="tsp")
    # print date_num_str_tra_timestamp("20160214")
    import tushare as ts
    print(ts.get_hist_data("600759"))
