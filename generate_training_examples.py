import random
random.seed(1) # Ensure reproducible results

import math
import os
import subprocess

from split_training_and_validation import AUDIO_SEGMENTS_DIR

from utils import make_sure_path_exists

NUM_TRAINING_EXAMPLES = 100000
TRAINING_EXAMPLES_DIR = 'data/nn/v0/train'

categories = sorted(os.listdir(AUDIO_SEGMENTS_DIR))
audio_segments = {category: sorted(os.listdir('{0}/{1}/train'.format(AUDIO_SEGMENTS_DIR, category))) for category in categories}

def make_training_examples():
    for i in xrange(NUM_TRAINING_EXAMPLES):
        print "Training: {0}/{1}".format(i+1, NUM_TRAINING_EXAMPLES)
        category = random.choice(categories)
        audio_segments_dir = '{0}/{1}/train'.format(AUDIO_SEGMENTS_DIR, category)
        segment_wav_file = '{0}/{1}'.format(audio_segments_dir, random.choice(audio_segments[category]))

        example_dir = '{0}/{1}'.format(TRAINING_EXAMPLES_DIR, category)
        make_sure_path_exists(example_dir)
        example_file_prefix = '{0}/{1}'.format(example_dir, i)

        extract_random_augmented_spectrogram(segment_wav_file, example_file_prefix)

def extract_random_augmented_spectrogram(input_wav_file, output_file_prefix):
    spectrogram_png_file = '{0}.spectrogram.png'.format(output_file_prefix)

    # compute all random factors before checking if file already
    # exists, as to ensure reproducible runs
    should_add_noise = random.uniform(0, 1) < 0.4
    noise_factor = random.uniform(0, 0.1)
    start_position_factor = random.uniform(0, 1)
    stretch_factor = math.exp(random.uniform(math.log(0.7), math.log(1.42)))

    if not os.path.isfile(spectrogram_png_file):
        random_segment_file = '{0}.segment.wav'.format(output_file_prefix)
        cut_segment(input_wav_file, start_position_factor, random_segment_file)

        stretched_segment_file = '{0}.stretched.wav'.format(output_file_prefix)
        stretch(random_segment_file, stretch_factor, stretched_segment_file)

        if should_add_noise:
            noise_file = '{0}.noise.wav'.format(output_file_prefix)
            noisy_segment_file = '{0}.noisy.wav'.format(output_file_prefix)
            add_noise(stretched_segment_file, noise_factor, noise_file, noisy_segment_file)
        else:
            noisy_segment_file = stretched_segment_file

        normalized_segment_file = '{0}.normalized.wav'.format(output_file_prefix)
        normalize(noisy_segment_file, normalized_segment_file)

        spectrogram_numpy_file = '{0}.spectrogram.npy'.format(output_file_prefix) # unused
        make_spectrogram(normalized_segment_file, spectrogram_numpy_file, spectrogram_png_file + '.tmp')
        os.rename(spectrogram_png_file + '.tmp', spectrogram_png_file)

def cut_segment(in_wav_file, start_position_factor, out_wav_file):
    # XXX!!! brittle if we change file format
    num_secs = os.path.getsize(in_wav_file) / 11025 / 2
    segment_secs = 2
    start_sec = (num_secs - segment_secs) * start_position_factor
    subprocess.check_call([
        'sox',
        in_wav_file,
        out_wav_file,
        'trim',
        str(start_sec),
        str(segment_secs),
    ])

def stretch(in_wav_file, factor, out_wav_file):
    subprocess.check_call([
        'sox',
        in_wav_file,
        out_wav_file,
        'tempo',
        '-s',
        str(factor),
        'trim',
        '0',
        '1.6',
    ])

def add_noise(in_wav_file, factor, noise_wav_file, out_wav_file):
    subprocess.check_call([
        'sox',
        in_wav_file,
        noise_wav_file,
        'synth',
        'whitenoise',
        'vol',
        str(factor),
    ])
    subprocess.check_call([
        'sox',
        '-m',
        in_wav_file,
        noise_wav_file,
        out_wav_file,
    ])

def normalize(in_wav_file, out_wav_file):
    subprocess.check_call([
        'sox',
        '--norm',
        in_wav_file,
        out_wav_file,
    ])

def make_spectrogram(in_wav_file, out_numpy_file, out_png_file):
    subprocess.check_call([
        'sox',
        in_wav_file,
        '-n',
        'spectrogram',
        '-y', '257', # 257 FFT bins
        '-x', '320', # width
        '-r', # raw spectrogram
        '-o',
        out_png_file,
    ])

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    make_training_examples()

