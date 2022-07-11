import datetime
import ffmpeg_streaming
import requests
import configparser
import logging
from pathlib import Path
import sys
from ffmpeg_streaming import Formats
import unicodedata
import re


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


l = Path('./runtime.log')

p = Path('./config.ini')
config = configparser.ConfigParser()
config.read(p)

logging.basicConfig(handlers=[logging.FileHandler(filename=l,
                                                 encoding='utf-8', mode='a+')],
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%F %A %T",
                    level=logging.INFO)


def monitor(ffmpeg, duration, time_, time_left, process):
    """
    Handling proccess.

    Examples:
    1. Logging or printing ffmpeg command
    logging.info(ffmpeg) or print(ffmpeg)

    2. Handling Process object
    if "something happened":
        process.terminate()

    3. Email someone to inform about the time of finishing process
    if time_left > 3600 and not already_send:  # if it takes more than one hour and you have not emailed them already
        ready_time = time_left + time.time()
        Email.send(
            email='someone@somedomain.com',
            subject='Your video will be ready by %s' % datetime.timedelta(seconds=ready_time),
            message='Your video takes more than %s hour(s) ...' % round(time_left / 3600)
        )
       already_send = True

    4. Create a socket connection and show a progress bar(or other parameters) to your users
    Socket.broadcast(
        address=127.0.0.1
        port=5050
        data={
            percentage = per,
            time_left = datetime.timedelta(seconds=int(time_left))
        }
    )

    :param ffmpeg: ffmpeg command line
    :param duration: duration of the video
    :param time_: current time of transcoded video
    :param time_left: seconds left to finish the video process
    :param process: subprocess object
    :return: None
    """
    per = round(time_ / duration * 100)
    sys.stdout.write(
        "\rTranscoding...(%s%%) %s left [%s%s]" %
        (per, datetime.timedelta(seconds=int(time_left)), '#' * per, '-' * (100 - per))
    )
    sys.stdout.flush()


def get_info(content_id):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'RNM-Account-Id': '218321',
        'Authorization': config['DEFAULT']['TOKEN'],
        'RNM-Experience-Id': '4',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Origin': 'https://app.rightnowmedia.org',
        'Connection': 'keep-alive',
        'Referer': 'https://app.rightnowmedia.org/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    params = {
        'culture': 'en',
    }

    response = requests.get(f'https://platform.rightnow.org/content/v1/content/{content_id}', params=params, headers=headers)

    return response.json()


def get_stream(content_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'RNM-Account-Id': '218321',
        'Authorization': config['DEFAULT']['TOKEN'],
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Origin': 'https://app.rightnowmedia.org',
        'Connection': 'keep-alive',
        'Referer': 'https://app.rightnowmedia.org/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    params = {
        'encodingType': 'hls',
    }

    response = requests.get(f'https://platform.rightnow.org/content/v1/content/{content_id}/streaming-urls', params=params, headers=headers)

    return response.json()


def save_file(url, filename):
    video = ffmpeg_streaming.input(url)

    stream = video.stream2file(Formats.h264())
    stream.output(filename, monitor=monitor)


def parse_url(url):
    """Takes a content url like https://redacted.com/en/player/video/511886?session=511887
    and returns a video content id which is the session= portion"""
    return url.split('=')[1]


def build_filename(title):
    return f"{slugify(title)}.mp4"


if __name__ == '__main__':
    content_id = parse_url(input("What URL Do you want to save?: "))
    info = get_info(content_id)
    filename = build_filename(info['title'])
    save_file(get_stream(content_id)['videoUrl'], filename)
    print(f"File Saved: {filename}")