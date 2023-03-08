# subtitles

A public repo of up to date sub files for Chiki Chiki Tube videos, some of which have been machine generated

If you'd like to update an existing sub file, or take a machine generated subfile and turn it into a proper manual sub yourself, raise an issue with the episode name for tracking purposes

### Roadmap
- Develop a way to tag machine subs as such so they can be used in chikichiki.tube without confusing user

### subtitles
Subs extracted from The Silent Library versions of videos

### subtitles_machine
SRT sub files transcribed/translated using [OpenAI Whisper](https://github.com/openai/whisper)

**Structure**
- File names are showname_airdate_episodenumber_videolanguage_subtitlelanguage

#### General issues
1. Translation
	- If there's a lot of noise or people talking at once the AI has a hard time picking out words and the translation becomes nonsense
	- Even with perfectly clear audio the translator can't accurately use pronouns, or always correctly identify names
	- This is all done through audio, so no on screen text is translated (this can be done manually with [Yandex OCR](https://translate.yandex.com/ocr))
2. Timings
	- Whisper only times to the nearest second, so subs can be as much as 0.5 seconds off
	- Sometimes the subs start to drift; sometimes it gets corrected in a few seconds, sometimes the drift persists throughout the rest of the video
	- Long run on sentences are usually cut up pretty badly
	- The AI always seems to want text on screen, so if there's a long pause in people talking the last subbed line will linger way too long

### Steps
1. You will need a folder of your videos and a csv called `sourcepath.csv` with a `filepath` (where the video file is) column and a `newpath` column (which is where the sub file goes)
2. Install WhisperAI (instructions for AMD linux below)
3. Run the whisperai python script to generate the sub files
4. After you're done translating everything open [Aegisub](https://github.com/wangqr/Aegisub/releases), drag/drop the video file and the srt into it, and then export it: File > Export Subtitles > Export > save it as an .ass file
5. Then you can copy paste the styles from existing subs, open it back up in Aegisub, and get started cleaning it up.


### Running Whisper AI on an AMD Navi 21 GPU (debian/ubuntu)
```bash
# get docker image for Pytorch for AMD Navi 21 GPUs
docker pull rocm/pytorch:rocm5.2_ubuntu20.04_py3.7_pytorch_1.11.0_navi21

# create drun alias with correct options
alias drun='sudo docker run -it --name autosub --network=host --device=/dev/kfd --device=/dev/dri --group-add=video --ipc=host --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -v $HOME/dockerx:/dockerx -v /mnt/yourfolder'

# initial drun and creation of container
drun rocm/pytorch:rocm5.2_ubuntu20.04_py3.7_pytorch_1.11.0_navi21

# start and exec container
docker container start autosub && docker exec -it autosub bash

# install software dependencies
sudo apt update && sudo apt -y install ffmpeg
pip3 install git+https://github.com/openai/whisper.git 
pip3 install more-itertools pyyaml pandas
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/rocm5.1.1

# run the whisperai python script
python3 whisperai.py
```

### whisperai.py python script 
```python
from ast import Index
import ffmpeg
import torch
import whisper
from whisper.utils import write_srt
import sys
import pandas as pd
import os
import time

def _decode_audio(in_filename, **input_kwargs):
    '''Decodes audio using ffmpeg and places in a temp.mp3 file'''
    try:
        out, err = (ffmpeg
                    .input(in_filename, **input_kwargs)
                    .output('temp.mp3', acodec='libmp3lame', ac=1, ar='16k')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True))
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    return out


def autosubber(sourcepath: str, newpath: str, translate, transcribe):
    '''Transcribes or translates a file from sourcepath and outputs an srt file in sourcepath'''
    outpath = '/chikichiki.tube/autosub/srt/' + newpath[:-4]
    print('Output Path will be: '+ outpath)

    if os.path.exists(outpath+"_en.srt") & os.path.exists(outpath+"_ja.srt"):
        print('Found EN, JA, skipping...')
        pass
    elif (translate & (os.path.exists(outpath+"_en.srt") == False)) | (transcribe & (os.path.exists(outpath+"_ja.srt") == False)):
        print('extracting audio to temp.mp3...')
        _decode_audio(sourcepath)
        print('audio extracted to temp.mp3')
        model = whisper.load_model("large")

    # en
    if os.path.exists(outpath+"_en.srt"):
        print('Found EN, skipping...')
        pass
    elif translate:
        decode_options_en = {'language': 'japanese', 'task': 'translate'}
        result_en = model.transcribe('temp.mp3', verbose=True, condition_on_previous_text=False, compression_ratio_threshold=1.9, **decode_options_en)
        with open(outpath+"_en.srt", "w", encoding="utf-8") as srt:
            write_srt(result_en["segments"], file=srt)
        print('English translation saved in ' + outpath + "_en.srt")

    # ja
    if os.path.exists(outpath+"_ja.srt"):
        print('Found JA, skipping...')
        pass
    elif transcribe:
        decode_options_ja={'language':'japanese','task':'transcribe'}
        result_ja = model.transcribe('temp.mp3', verbose=True, condition_on_previous_text=False, compression_ratio_threshold=1.9, **decode_options_ja)
        with open(outpath+"_ja.srt", "w", encoding="utf-8") as srt:
            write_srt(result_ja["segments"], file=srt)
        print('Japanese transcription saved in ' + outpath + "_ja.srt")

torch.device('cuda')
print('Cuda status: ' + str(torch.cuda.is_available()))

sourcepathlist = pd.read_csv('pathlist.csv')

for sourcepath in sourcepathlist.itertuples():
   print(sourcepath.filepath)
   autosubber(sourcepath=sourcepath.filepath, newpath=sourcepath.newpath, translate=True, transcribe=False)

```
