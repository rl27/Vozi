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

    # Load split vocals from directory
    vocals = []
    v_segments = []
    vocal_length = 0
    for _, _, files in os.walk(vocaldir):
        for file in files:
            filepath = os.path.join(vocaldir, file)
            vocal = librosa.load(filepath)[0]
            vocals.append(vocal)
            vocal_length += librosa.get_duration(vocal)
            v_segments.append(vocal_length)
    v_segments = np.array(v_segments) / vocal_length
    print("Vocal length:", vocal_length)

    # Load split beats from directory
    beats = []
    b_segments = []
    beat_length = 0
    for _, _, files in os.walk(beatdir):
        for file in sorted(files):
            filepath = os.path.join(beatdir, file)
            beat = librosa.load(filepath)[0]
            beats.append(beat)
            beat_length += librosa.get_duration(beat)
            b_segments.append(beat_length)
    b_segments = np.array(b_segments) / beat_length
    print("Beat length:", beat_length)


    #for seg in beats:
    #    print(np.max(detect_pitch(seg)))

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


    # Not really sure how to properly match pitch of vocals to pitch of beats.
    # pitch_shift doesn't work as quite as expected when analyzing detect_pitch outputs.
    def pitch_match(v, b):
        v = librosa.effects.pitch_shift(v, 22050, n_steps=0)
        return v


    # Option 1 (easier): match vocals to beats one-to-one --- bad quality
    # combined = np.array([])
    # total = np.min([len(vocals), len(beats)])
    # for i in range(total):
    #     v = vocals[i]
    #     b = beats[i]
        
    #     v = librosa.effects.time_stretch(v, len(v)/len(b))
    #     v = pitch_match(v, b)
    #     combined = np.append(combined, (np.array(v) + np.array(b))/2)


    # Option 2 (harder): try to match lengths by using multiple vocals/beats --- better quality (hopefully)

    combined = np.array([])

    v_indices = []
    for b in b_segments:
        dist = 2
        closest = -1
        for index, v in enumerate(v_segments):
            if np.abs(b - v) < dist:
                dist = np.abs(b - v)
                closest = index
        v_indices.append(closest)

    prev = 0
    for i in range(len(v_indices)):
        b = beats[i]
        v = vocals[prev]
        for v2 in vocals[prev+1 : v_indices[i]]:
            v = np.append(v, v2)
        prev = v_indices[i]
        v = librosa.effects.time_stretch(v, len(v)/len(b))
        v = pitch_match(v, b)
        combined = np.append(combined, (np.array(v) + np.array(b))/2)


    
    # Write the output
    outdir = "./combined"
    if args.outdir:
        outdir = args.outdir

    out_file = "{0}/combined.wav".format(outdir)
    print("exporting", out_file)
    sf.write(out_file, combined, 22050)


if __name__ == "__main__":
    main()