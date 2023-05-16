# Copyright (c) 2018 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

import argparse
from scipy import io
import numpy as np
import sounddevice as sd

# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

# Read from a 16-bit WAV file. Returns the sample rate in
# samples per second, and the samples as a numpy array of
# IEEE 64-bit floats. The array will be 1D for mono data,
# and will be a 2D array of 2-element frames for stereo
# data.
def read_wav(filename):
    rate, data = io.wavfile.read(filename)
    assert data.dtype == np.int16
    data = data.astype(np.float64)
    data /= 32768
    return rate, data

# Write to a 16-bit WAV file. Data is in the same
# format produced by read_wav().
def write_wav(filename, rate, data):
    assert data.dtype == np.float64
    data *= 32767
    data = data.astype(np.int16)
    io.wavfile.write(filename, rate, data)

# Play a tone on the computer. Data is in the same format
# produced by read_wav().
def play(rate, wav):
    # Deal with stereo.
    channels = 1
    if wav.ndim == 2:
        channels = 2

    # Set up and start the stream.
    stream = sd.RawOutputStream(
        samplerate = rate,
        blocksize = BUFFER_SIZE,
        channels = channels,
        dtype = 'float32',
    )

    # Write the samples.
    stream.start()
    # https://stackoverflow.com/a/73368196
    indices = np.arange(BUFFER_SIZE, wav.shape[0], BUFFER_SIZE)
    samples = np.ascontiguousarray(wav, dtype=np.float32)
    for buffer in np.array_split(samples, indices):
        stream.write(buffer)
        # Check if the user pressed 'esc' to end the playback
        if sd.wait() == 'escape':
            break
    print("Playback stopped. Press 'esc' to end.")

    # Tear down the stream.
    stream.stop()
    stream.close()

# Parse command-line arguments. Returns a struct whose
# elements are the arguments passed on the command line.
# See the `argparse` documentation for details.

def tone_args():
    parser = argparse.ArgumentParser(description='Adjust tone and volume of a WAV file.') # The first step in using the argparse is creating an ArgumentParser object. The ArgumentParser object will hold all the information necessary to parse the command line into Python data types.

    # additional arguments for CLI input to take input on the CLI and turn them into objects. This is stored and used when parse_args is called.

    parser.add_argument('wav', type=str, help='Input WAV filename')  # parser.add_argument() attaches individual argument specifications to the parser.
    parser.add_argument('--out', type=str, help='write to WAV file instead of playing')
    parser.add_argument('--volume', type=np.float64, default=9.0, help='volume in 3dB units (default 9 = 0dB, 0 = 0 output)')
    parser.add_argument('--bass', type=np.float64, default=5.0, help='bass emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)')
    parser.add_argument('--mid', type=np.float64, default=5.0, help='mid-range emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)')
    parser.add_argument('--treble', type=np.float64, default=5.0, help='treble emphasis in 3dB units (default 5 = 0dB, 0 = 0 output)')

    return parser.parse_args()
