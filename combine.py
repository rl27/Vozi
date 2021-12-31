import numpy as np
from utils import detect_nonsilent, gaussian_derivative, save_plot
import librosa
import soundfile as sf
import aubio
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

            pitches, magnitudes = librosa.piptrack(S=np.abs(librosa.stft(beat)), threshold=1, ref=np.mean)
            print(np.mean(pitches))
    print("Beat length:", beat_length)

    outdir = "./combined"
    if args.outdir:
        outdir = args.outdir


    # for _, _, files in os.walk(beatdir):
    #     for file in files:
    #         filepath = os.path.join(beatdir, file)
    #         win_s = 4096
    #         hop_s = 512 

    #         s = aubio.source(filepath, 22050, hop_s)
    #         samplerate = s.samplerate

    #         tolerance = 0.8

    #         pitch_o = aubio.pitch("yin", win_s, hop_s, samplerate)
    #         pitch_o.set_unit("midi")
    #         pitch_o.set_tolerance(tolerance)

    #         pitches = []
    #         confidences = []

    #         total_frames = 0
    #         while True:
    #             samples, read = s()
    #             pitch = pitch_o(samples)[0]
    #             pitches += [pitch]
    #             confidence = pitch_o.get_confidence()
    #             confidences += [confidence]
    #             total_frames += read
    #             if read < hop_s: break

    #         print(np.mean(pitches))


    # Change pitch and speed of vocals to match beat

    # Option 1 (easier): match beats one-to-one


    # Option 2 (harder): try to match lengths





    # segments = detect_nonsilent(conv, 200, 0.0045)
    # ratio = 1000 * librosa.get_duration(audio) / len(conv) # values in audio array per millisecond
    # count = 0
    # for i, seg in enumerate(segments):
    #     if seg[1] * ratio - seg[0] * ratio < 50: # skip if less than 50 milliseconds
    #         continue
    #     sliced = audio[seg[0] : seg[1]]
    #     out_file = "{0}/chunk{1}.wav".format(outdir, i)
    #     print("exporting", out_file, seg[1] * ratio - seg[0] * ratio)
    #     count += 1
    #     sf.write(out_file, sliced, sample_rate)
    # print("\nAccepted segments:", count)


    # # All non-silent segments combined
    # keep = 0
    # combined = audio[segments[0][0] : segments[0][1] + keep]
    # for i in range(1,len(segments)):
    #     combined = np.append(combined, audio[segments[i][0] : segments[i][1] + keep])
    # sf.write("{0}/combined{1}.wav".format(outdir, keep), combined, sample_rate)
    

if __name__ == "__main__":
    main()