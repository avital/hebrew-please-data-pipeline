import random
random.seed(1) # Ensure reproducible results

import math
import os
import subprocess

from generate_training_examples import cut_segment, normalize, make_spectrogram

from split_training_and_validation import AUDIO_SEGMENTS_DIR

from utils import make_sure_path_exists

NUM_VALIDATION_EXAMPLES = 4000
VALIDATION_EXAMPLES_DIR = 'data/validation/v0'

categories = sorted(os.listdir(AUDIO_SEGMENTS_DIR))
audio_segments = {category: sorted(os.listdir('{0}/{1}/val'.format(AUDIO_SEGMENTS_DIR, category))) for category in categories}

def make_validation_examples():
    for i in xrange(NUM_VALIDATION_EXAMPLES):
        print "Validation: {0}/{1}".format(i+1, NUM_VALIDATION_EXAMPLES)
        category = random.choice(categories)
        audio_segments_dir = '{0}/{1}/val'.format(AUDIO_SEGMENTS_DIR, category)
        segment_wav_file = '{0}/{1}'.format(audio_segments_dir, random.choice(audio_segments[category]))

        example_dir = '{0}/{1}'.format(VALIDATION_EXAMPLES_DIR, category)
        make_sure_path_exists(example_dir)
        example_file_prefix = '{0}/{1}'.format(example_dir, i)

        extract_random_spectrogram(segment_wav_file, example_file_prefix)

def extract_random_spectrogram(input_wav_file, output_file_prefix):
    spectrogram_png_file = '{0}.spectrogram.png'.format(output_file_prefix)

    # compute all random factors before checking if file already
    # exists, as to ensure reproducible runs
    start_position_factor = random.uniform(0, 1)

    if not os.path.isfile(spectrogram_png_file):
        random_segment_file = '{0}.segment.wav'.format(output_file_prefix)
        cut_segment(input_wav_file, start_position_factor, random_segment_file)

        normalized_segment_file = '{0}.normalized.wav'.format(output_file_prefix)
        normalize(random_segment_file, normalized_segment_file)

        spectrogram_numpy_file = '{0}.spectrogram.npy'.format(output_file_prefix) # unused
        make_spectrogram(normalized_segment_file, spectrogram_numpy_file, spectrogram_png_file + '.tmp')
        os.rename(spectrogram_png_file + '.tmp', spectrogram_png_file)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    make_validation_examples()

