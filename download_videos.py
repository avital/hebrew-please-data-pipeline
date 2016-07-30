from __future__ import unicode_literals

import errno
import os
import shutil
import subprocess
import yaml
import youtube_dl

VIDEO_LIST_DIR = 'data/videos-list/v0'
AUDIO_DIR = 'data/audio/v0'

def read_videos_dict():
    """Read a YAML list of links to YouTube videos, encoded in YAML.
    Returns a dict, e.g. {'hebrew': [url1, url2, ...], 'music': [url1,
    url2, ...]}

    """
    with open('{0}/videos.yaml'.format(VIDEO_LIST_DIR)) as f:
        return yaml.load(f)

def download_videos(videos_dict):
    """Download videos based on a dictionary mapping categories to a list
    of YouTube URLs into a data directory of audio files.

    Don't download a video if it's already been downloaded. If the
    format of the downloaded video changed, bump the version number in
    'AUDIO_DIR'.

    """
    for category in videos_dict:
        for url in videos_dict[category]:
            video_id = url[-11:]
            processed_base_dir = os.path.abspath('{0}/{1}/{2}'.format(AUDIO_DIR, category, video_id))
            if not os.path.isdir(processed_base_dir):
                if os.path.isdir(processed_base_dir + '-tmp'):
                    shutil.rmtree(processed_base_dir + '-tmp')
                os.makedirs(processed_base_dir + '-tmp')

                downloaded_audio_file = '{0}-tmp/audio.unknown'.format(processed_base_dir)
                converted_audio_file = '{0}-tmp/audio.wav'.format(processed_base_dir)
                download_audio_from_youtube(url, downloaded_audio_file)
                convert_audio_to_wav(downloaded_audio_file, converted_audio_file)
                os.rename(processed_base_dir + '-tmp', processed_base_dir)

def download_audio_from_youtube(url, downloaded_audio_file):
    """Download a single YouTube video into an audio file"""
    print()
    print('Downloading audio from video ({0})...'.format(downloaded_audio_file))
    ydl = youtube_dl.YoutubeDL({
        'format': 'bestaudio',
        'outtmpl': downloaded_audio_file,
        'quiet': True,
        'writeinfojson': True
    })
    ydl.download([url])
    print('DONE.')

def convert_audio_to_wav(downloaded_audio_file, converted_audio_file):
    """Convert an audio file in any format into a 11KHz 16-bit mono WAV file"""
    print()
    print('Converting to WAV ({0})...'.format(converted_audio_file))
    subprocess.check_call(["ffmpeg", "-y", "-i", downloaded_audio_file, "-ar", \
                           "11025", "-ac", "1", "-acodec", "pcm_s16le", converted_audio_file])
    print('DONE.')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    videos_dict = read_videos_dict()
    download_videos(videos_dict)


