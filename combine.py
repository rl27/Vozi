import numpy as np
from utils import detect_nonsilent, gaussian_derivative, detect_pitch, smooth, save_plot
import librosa
import soundfile as sf
import aubio
import wave
import argparse
import os

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("vocals", help="Directory of the split vocals")
    parser.add_argument("beats", help="Directory to the split beats")
    parser.add_argument("--outdir", help="Directory to output the combined audio file")
    args = parser.parse_args()

    vocaldir = args.vocals
    beatdir = args.beats

    # Load vocals
    vocals = []
    vocal_length = 0
    for _, _, files in os.walk(vocaldir):
        for file in files:
            filepath = os.path.join(vocaldir, file)
            vocal = librosa.load(filepath)[0]
            vocals.append(vocal)
            vocal_length += librosa.get_duration(vocal)
    print("Vocal length:", vocal_length)

    # Load beats
    beats = []
    beat_length = 0
    for _, _, files in os.walk(beatdir):
        for file in files:
            filepath = os.path.join(beatdir, file)
            beat = librosa.load(filepath)[0]
            beats.append(beat)
            beat_length += librosa.get_duration(beat)
    print("Beat length:", beat_length)

    outdir = "./combined"
    if args.outdir:
        outdir = args.outdir


    
    



    for seg in beats:
        print(detect_pitch(seg))

    # print(detect_pitch(librosa.load("audio/gtasa.wav")[0]))


    '''
    Change pitch and speed of vocals to match beat
    https://librosa.org/doc/main/generated/librosa.effects.pitch_shift.html
    https://librosa.org/doc/main/generated/librosa.effects.time_stretch.html
    '''
    # audio, sr = librosa.load("audio/super_idol.wav")
    # audio = librosa.effects.pitch_shift(audio, sr, n_steps=-1)
    # audio = librosa.effects.time_stretch(audio, 1.5)
    # sf.write("test.wav", audio, sr)


    # Option 1 (easier): match beats one-to-one


    # Option 2 (harder): try to match lengths

    

if __name__ == "__main__":
    main()