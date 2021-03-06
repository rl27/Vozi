import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import librosa
# import cv2

# https://github.com/jiaaro/pydub/blob/7b0d27a4eb7246324601ff1a120397eeddfa3ee5/pydub/silence.py#L9
def detect_silence(audio_segment, min_silence_len=1000, silence_thresh=50, seek_step=1):
    """
    Returns a list of all silent sections [start, end] of audio_segment.
    audio_segment - numpy array of the segment to find silence in
    min_silence_len - the minimum length for any silent section
    silence_thresh - the upper bound for how quiet is silent
    seek_step - step size for interating over the segment
    """
    seg_len = len(audio_segment)

    # you can't have a silent portion of a sound that is longer than the sound
    if seg_len < min_silence_len:
        return []

    # convert silence threshold to a float value (so we can compare it to rms)
    # silence_thresh = db_to_float(silence_thresh) * audio_segment.max_possible_amplitude

    # find silence and add start and end indices to the to_cut list
    silence_starts = []

    # check successive (1 sec by default) chunk of sound for silence
    # try a chunk at every "seek step" (or every chunk for a seek step == 1)
    last_slice_start = seg_len - min_silence_len
    slice_starts = range(0, last_slice_start + 1, seek_step)

    squared = audio_segment**2
    squared = np.append(squared, [0])
    s = np.sum(squared[:min_silence_len])
    for i in slice_starts:
        if np.sqrt(np.abs(s)/min_silence_len) <= silence_thresh: # rms
            silence_starts.append(i)
        s = s + squared[i + min_silence_len] - squared[i]

    # exit when there is no silence
    if not silence_starts:
        return []

    # combine the silence we detected into ranges (start ms - end ms)
    silent_ranges = []

    prev_i = silence_starts.pop(0)
    current_range_start = prev_i

    for silence_start_i in silence_starts:
        continuous = (silence_start_i == prev_i + seek_step)

        # sometimes two small blips are enough for one particular slice to be
        # non-silent, despite the silence all running together. Just combine
        # the two overlapping silent ranges.
        silence_has_gap = silence_start_i > (prev_i + min_silence_len)

        if not continuous and silence_has_gap:
            silent_ranges.append([current_range_start,
                                  prev_i + min_silence_len])
            current_range_start = silence_start_i
        prev_i = silence_start_i

    silent_ranges.append([current_range_start,
                          prev_i + min_silence_len])

    return silent_ranges

# https://github.com/jiaaro/pydub/blob/7b0d27a4eb7246324601ff1a120397eeddfa3ee5/pydub/silence.py#L76
def detect_nonsilent(audio_segment, min_silence_len=1000, silence_thresh=50, seek_step=1):
    """
    Returns a list of all nonsilent sections [start, end] of audio_segment.
    Inverse of detect_silent()
    audio_segment - the segment to find silence in
    min_silence_len - the minimum length for any silent section
    silence_thresh - the upper bound for how quiet is silent
    seek_step - step size for interating over the segment
    """
    silent_ranges = detect_silence(audio_segment, min_silence_len, silence_thresh, seek_step)
    len_seg = len(audio_segment)

    # if there is no silence, the whole thing is nonsilent
    if not silent_ranges:
        return [[0, len_seg]]

    # exit when the whole audio segment is silent
    if silent_ranges[0][0] == 0 and silent_ranges[0][1] == len_seg:
        return []

    prev_end_i = 0
    nonsilent_ranges = []
    for start_i, end_i in silent_ranges:
        nonsilent_ranges.append([prev_end_i, start_i])
        prev_end_i = end_i

    if end_i != len_seg:
        nonsilent_ranges.append([prev_end_i, len_seg])

    if nonsilent_ranges[0] == [0, 0]:
        nonsilent_ranges.pop(0)

    return nonsilent_ranges


def gaussian_derivative(audio, sigma=1.0):
    '''
    Takes in audio as an array, and sigma. Returns smoothed derivative of audio.
    '''
    # sigma controls the amount of smoothing
    sigma = 1
    # filter half-width should be at least 3*sigma
    half_width = int(3 * sigma)

    # Get 1D gaussian derivative filter
    # px = np.arange(-half_width + 1, half_width)
    px = np.arange(-half_width, half_width + 1)
    G = 1 / (np.sqrt(2*np.pi)*sigma) * np.exp(-(px**2)/(2 * sigma**2))
    dG = -(px) / (np.sqrt(2*np.pi)*sigma**3) * np.exp(-(px**2)/(2 * sigma**2))

    return np.convolve(audio, dG)


def convolve_median(audio, size=5):
    '''
    Takes in audio as an array, and size of median filter. Returns convolved median of audio.
    '''
    return ndimage.median_filter(audio, size=size)


def detect_pitch(audio):
    '''
    https://stackoverflow.com/a/44009768
    https://librosa.org/doc/main/generated/librosa.piptrack.html
    Takes in the audio loaded via librosa.load and returns the pitch.
    '''
    pitches, magnitudes = librosa.piptrack(audio, threshold=1, ref=np.mean)
    p2 = []
    for i in range(magnitudes.shape[1]):
        p2.append(pitches[np.argmax(magnitudes[:,i]),i])

    #new_pitches = []
    #new_magnitudes = []
    p2 = []
    for i in range(magnitudes.shape[1]):
        p2.append(pitches[np.argmax(magnitudes[:,i]),i])
        #new_pitches.append(np.max(pitches[:,i]))
        #new_magnitudes.append(np.max(magnitudes[:,i]))

    # pitches = smooth(new_pitches)
    # p2 = smooth(p2)
    # save_plot(pitches, "test0.png")
    # save_plot(p2, "test1.png")

    return np.mean(smooth(p2))


def smooth(x, window_len=11, window='hanning'):
    if window_len < 3:
        return x
    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window must be one of of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[2*x[0] - x[window_len-1::-1], x, 2*x[-1]-x[-1:-window_len:-1]]

    if window == 'flat': # moving average
        w = np.ones(window_len,'d')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / np.sum(w), s, mode='same')
    return y[window_len:-window_len+1]


def save_plot(vals, name):
    plt.figure(figsize=(30,8))
    plt.plot(vals)
    plt.savefig("plots/{0}".format(name))
    plt.close()
