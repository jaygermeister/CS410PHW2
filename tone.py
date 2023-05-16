#-------------------------------------------------------------------------------
# Name: EQ HW2 CS410P PSU Spring Term
# Purpose: This is a command line volume and tone control application that will read a WAV file and play it with adjusted volume &| tone, or write a new WAV file with the adjusted tone and volume
#
# Requirements:
# --volume setting, a non-negative float in the range 0.0-10.0. Each full volume step is 3 dB with 0dB being teh default volume setting of 9.0. A volume setting of less than 0.1 is treated as "0 volume i.e. no sound at all"

# --bass, --mid, --treble; Tone setting, a non-negative float in the range 0.0-10.0. Each full step is 3 dB, with 0dB being default volume setting of 5.0. A tone setting of less than 0.1 is treated as no tone.

# --out; name of an output WAV file. This will suppress playback and write the output into the given WAV file in the same format as the input

# This program must take a provisional argument naming the input WAV file

# The program must use the library routine supplied in the class materials in hw-tone-resources to read and write wav files, play wav files and process the CLI arguments
#
# Author:      Jay Best
#
# Created:     13/05/2023
# Copyright:   (c) Jayger 2023
#-------------------------------------------------------------------------------

import argparse
import numpy as np
import libtone
from libtone import read_wav
from libtone import tone_args
from scipy.signal import butter, lfilter

# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

"""     Adjusts the volume of the audio data.
    Args:
        data (ndarray): This will be the audio data read into a numpy array.
        volume (float): Volume multiplier (0.0 - 10.0)
    Returns:
        ndarray: Adjusted audio data as a numpy array
    """
def apply_volume(data, volume):
    """Adjust the volume of the input signal."""
    if volume < 0.1:
        # Treat volume settings less than 0.1 as "0 volume"
        return np.zeros_like(data)
    else:
        # Set the maximum volume to 25
        max_volume = 25.0
        volume = min(volume, max_volume)  # this sets maximum to 25, and will choose the smaller value between volume and max_volume. If volume is greater than 25, then it becomes 25
        # Compute the scaling factor from the volume setting (in dB)
        scale = 10 ** (volume / 10)
        # Apply the scaling factor to the input signal
        return scale * data


def apply_tone(data, rate, bass_gain, mid_gain, treble_gain):


    """    Applies tone adjustments to the audio data in the frequency ranges, which can be set in filter cuttof frequencies section.

    Args:
        data (ndarray): Audio data as a numpy array. (ndarray = N-dimensional array)
        rate (int): Sampling rate of the audio data.
        bass_gain (float): Bass gain multiplier (0.0 - 10.0).
        mid_gain (float): Mid gain multiplier (0.0 - 10.0).
        treble_gain (float): Treble gain multiplier (0.0 - 10.0).
    Returns:
        ndarray: Adjusted audio data as a numpy array.
    """
    # Filter cutoff frequencies (Hz)
    bass_cutoff = 300     # Low
    mid_cutoff = 2000     # Mid
    treble_cutoff = 4000  # High

    # Filter order
    filter_order = 2

    # Normalize gain values to a maximum of 10. This might not be working right now
    gain_norm = 10.0 / max(bass_gain, mid_gain, treble_gain)
    bass_gain *= gain_norm
    mid_gain *= gain_norm
    treble_gain *= gain_norm

    # Calculate filter coefficients
    """
        The butterworth (butter()) function from the scipy.signal module create the filter coefficients for LP, BP, and HP filters.
            Args:
                filter_order = biquad, 2nd order filter.
                bass_cuttoff = cuttoff freq in Hz
                b   ass_cuttoff/(rate/2) calculates the cuttoff frequency in normalized units. Normalizing the gain values to a maximum of 10 ensures that the maximum gain across all frequency bands is not greater than 10
                rate = sampling rate of the audio file in Hz
    """
    b_bass, a_bass = butter(filter_order, bass_cutoff / (rate / 2), 'low')  # The butter function returns two arrays, 'a' and 'b' which are the numerator and denominator coefficients of the transfer function for this filter.
    b_mid, a_mid = butter(filter_order, [bass_cutoff / (rate / 2), mid_cutoff / (rate / 2)], 'band')
    b_treble, a_treble = butter(filter_order, treble_cutoff / (rate / 2), 'high')

    # These values are used with lfilter here:
    # Apply filters to the data
    data = lfilter(b_bass * bass_gain, a_bass, data)
    data = lfilter(b_mid * mid_gain, a_mid, data)
    data = lfilter(b_treble * treble_gain, a_treble, data)

    # Clip the output to prevent distortion
    """
        np.clip()
            Args:
                data = the audio data itself,
                -1 = lower limit
                1 = upper limit
        Clipping applied to limit the values of the audio signal within the range of -1 to 1.
        This function ensures that no value in the signal exceeds 1 or -1, which prevents distortion and clipping of the audio signal.
    """
    data = np.clip(data, -1, 1)

    return data   # return the process audio data back to main for file operations


# Argprse module support for CLI is built around instance of argparse.ArgumentParser. It's a container for argument specifications and has options thawt apply the parser as whole
def main():

    args = tone_args()  # this will inspect the CLI, convert each argument to the appropriate type, and invoke the appropriate action.

    input_filename = args.wav
    output_filename = args.out

    # Read the input WAV file
    rate, data = libtone.read_wav(input_filename)

    # A fun line that lets you know the original sampling rate

    print("Sampling rate:", rate)

    # Apply the tone and volume adjustments
    data = apply_volume(data, args.volume)
    print("Volume:",args.volume)
    print("bass:",args.bass)
    print("mid:", args.mid)
    print("treble:", args.treble)
    data = apply_tone(data, rate, args.bass, args.mid, args.treble)

    # Write the output WAV file, if requested
    if output_filename:
        libtone.write_wav(output_filename, rate, data)
    else:
        # Play the output audio in real time if output isn't specified. You'll have to CTRL+C to bail on playback.
        libtone.play(rate, data)


if __name__ == '__main__':
    main()
