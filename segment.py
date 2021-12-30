import numpy as np
from pydub import AudioSegment, effects
from pydub.silence import split_on_silence
from utils import detect_nonsilent, gaussian_derivative, save_plot
import argparse
import os

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the audio file")
    parser.add_argument("--outdir", help="Directory to output segments")
    args = parser.parse_args()

    try:
        filename = args.path
        _, ext = os.path.splitext(filename)
        #sound_file = AudioSegment.from_ogg("hours.ogg")
        sound_file = AudioSegment.from_file(filename, ext)
        norm = effects.normalize(sound_file)    # https://github.com/jiaaro/pydub/blob/master/pydub/effects.py#L36
        # print(sound_file.max)
        # print(sound_file.max_possible_amplitude)
        # print(norm.max)
        # print(norm.max_possible_amplitude)

        # Create numpy array from AudioSegment
        audio = np.array(norm.get_array_of_samples())
        print("Audio length: {0} seconds".format(len(norm)/1000))
        print("Array length:", len(audio))
        print("Vals per ms:", len(audio) / len(norm))
        # print(np.mean(audio))
        # print(np.std(audio))
        # print(np.min(audio))
        # print(np.max(audio))

        # Get smoothed derivative of normalized audio
        conv = gaussian_derivative(audio, sigma=1.0)
        # save_plot(conv, "conv{0}.png".format(1.0))
        # save_plot(audio, "audio.png")
        # save_plot(convolve_median(audio, 5), "median{0}.png".format(1.0))

        # split_on_silence
        # https://github.com/jiaaro/pydub/blob/master/pydub/silence.py#L112

        outdir = "./splitAudio"
        if args.outdir:
            outdir = args.outdir

        segments = detect_nonsilent(conv, 1000, 50)
        ratio = len(norm) / len(conv)
        count = 0
        for i, seg in enumerate(segments):
            if seg[1]*ratio - seg[0]*ratio < 50: # skip if less than 50 milliseconds
                continue
            sliced = norm[seg[0] * ratio : seg[1] * ratio]
            out_file = "{0}/chunk{1}.wav".format(outdir, i)
            print("exporting", out_file, seg[1]*ratio - seg[0]*ratio)
            count += 1
            sliced.export(out_file, format="wav")
        print("\nAccepted segments:", count)


        # All non-silent segments combined
        keep = 0
        combined = norm[segments[0][0]*ratio:segments[0][1]*ratio + keep]
        for i in range(1,len(segments)):
            combined += norm[segments[i][0]*ratio:segments[i][1]*ratio + keep]
        combined.export("{0}/combined{1}.wav".format(outdir, keep), format="wav")


    except Exception as e:
        print(e)
    

if __name__ == "__main__":
    main()