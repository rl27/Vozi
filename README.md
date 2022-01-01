# Vozi
A tool to extract syllables from an audio segment.

To segment vocals:
```
python segment.py audio/my_audio_file_name
```

<hr>

To segment beats:
```
python segment_beats.py audio/my_audio_file_name
```

<hr>

To combine segmented vocals with segmented beats:
```
python combine.py path/to/segmented/vocals path/to/segmented/beats
```

<hr>

For each of the above three commands, use ```--outdir``` to specify the output directory.
```
python segment.py audio/my_audio_file_name --outdir my_out_directory
python segment_beats.py audio/my_audio_file_name --outdir my_out_directory
python combine.py path/to/segmented/vocals path/to/segmented/beats --outdir my_out_directory
```