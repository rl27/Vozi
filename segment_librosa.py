import numpy as np
from utils import detect_nonsilent, gaussian_derivative, save_plot
import librosa
import soundfile as sf
import argparse
import os

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the audio file")
    parser.add_argument("--outdir", help="Directory to output segments")
    args = parser.parse_args()

    filename = args.path
    audio, sample_rate = librosa.load(filename)
    audio = np.array(audio)

    # Get smoothed derivative of audio
    conv = gaussian_derivative(audio, sigma=1.0)

    outdir = "./splitAudio"
    if args.outdir:
        outdir = args.outdir

    segments = detect_nonsilent(conv, 200, 0.0045)
    ratio = 1000 * librosa.get_duration(audio) / len(conv) # values in audio array per millisecond
    count = 0
    for i, seg in enumerate(segments):
        if seg[1] * ratio - seg[0] * ratio < 50: # skip if less than 50 milliseconds
            continue
        sliced = audio[seg[0] : seg[1]]
        out_file = "{0}/chunk{1}.wav".format(outdir, i)
        print("exporting", out_file, seg[1] * ratio - seg[0] * ratio)
        count += 1
        sf.write(out_file, sliced, sample_rate)
    print("\nAccepted segments:", count)


    # All non-silent segments combined
    keep = 0
    combined = audio[segments[0][0] : segments[0][1] + keep]
    for i in range(1,len(segments)):
        combined = np.append(combined, audio[segments[i][0] : segments[i][1] + keep])
    sf.write("{0}/combined{1}.wav".format(outdir, keep), combined, sample_rate)
    

if __name__ == "__main__":
    main()