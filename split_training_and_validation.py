import math
import os
import subprocess

from download_videos import read_videos_dict
from download_videos import AUDIO_DIR

from utils import make_sure_path_exists

AUDIO_SEGMENTS_DIR = 'data/audio-segments/v0'

def split(videos_dict):
    """For each video in each category, split its audio file into minute
    segments. For each minute segment, extract the first 50 seconds
    into an audio file to be used for training data, and the last 10
    seconds into an audio file to be used for validation data.

    """
    for category in videos_dict:
        for url in videos_dict[category]:
            video_id = url
            video_wav_file = '{0}/{1}/{2}/audio.wav'.format(AUDIO_DIR, category, video_id)

            train_segments_dir = '{0}/{1}/train'.format(AUDIO_SEGMENTS_DIR, category)
            val_segments_dir = '{0}/{1}/val'.format(AUDIO_SEGMENTS_DIR, category)
            make_sure_path_exists(train_segments_dir)
            make_sure_path_exists(val_segments_dir)

            split_segments(video_wav_file, video_id, train_segments_dir, val_segments_dir)

def split_segments(wav_file, video_id, train_segments_dir, val_segments_dir):
    """Take a wave file and split its audio file into 50s segments for
    training and 10s segments for validation, as described in the
    'split' function.

    Only extract segments that are at least 5 seconds long.

    """
    # XXX!!! brittle if we change file format
    num_secs = os.path.getsize(wav_file) / 11025 / 2
    for start_min in xrange(int(math.ceil(num_secs / 60.0))):
        start_sec = start_min * 60
        if num_secs - start_sec > 5:
            train_segment_file = '{0}/{1}-{2}.wav'.format(train_segments_dir, video_id, start_min)
            extract_segment(wav_file, start_sec, 50, train_segment_file)
        if num_secs - (start_sec + 50) > 5:
            val_segment_file = '{0}/{1}-{2}.wav'.format(val_segments_dir, video_id, start_min)
            extract_segment(wav_file, start_sec + 50, 10, val_segment_file)

def extract_segment(input_wav_file, start_sec, num_secs, output_wav_file):
    """Extract a segment from a wave file"""
    if not os.path.isfile(output_wav_file):
        subprocess.check_call([
            'sox',
            input_wav_file,
            output_wav_file + '-tmp.wav',
            'trim',
            str(start_sec),
            str(num_secs)
        ])
        os.rename(output_wav_file + '-tmp.wav', output_wav_file)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    videos_dict = read_videos_dict()
    videos_dict = {
        'english-avital': videos_dict['english-avital'],
        'hebrew-avital': videos_dict['hebrew-avital']
    }
    split(videos_dict)
