import numpy as np
from utils import save_plot
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
    #filename = librosa.ex('trumpet')
    audio, sample_rate = librosa.load(filename)

    # Get beats
    tempo, beats = librosa.beat.beat_track(audio, sample_rate, units="samples")

    # Divide audio into segments based on beats
    segments = []
    start = 0
    for beat in beats:
        segments.append(audio[start:beat])
        start = beat
    segments.append(audio[start:])

    # Save segments
    outdir = "./splitBeats"
    if args.outdir:
        outdir = args.outdir

    for i, seg in enumerate(segments):
        out_file = "{0}/chunk{1}.wav".format(outdir, str(i).zfill(4))
        print("exporting", out_file)
        sf.write(out_file, seg, sample_rate)
    

if __name__ == "__main__":
    main()