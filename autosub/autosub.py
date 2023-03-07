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

sourcepathlist = pd.read_csv('/chikichiki.tube/etl/metadata_lincoln.csv')
sourcepathlist = sourcepathlist.loc[(sourcepathlist['language'] == 'ja')&(sourcepathlist['episode'] != 1348)]
sourcepathlist['filepath'] = '/chikichikitube/' + sourcepathlist['path']
print(str(len(sourcepathlist))+' videos')

for sourcepath in sourcepathlist.itertuples():
   print(sourcepath.filepath)
   autosubber(sourcepath=sourcepath.filepath, newpath=sourcepath.newpath, translate=True, transcribe=False)

# custom ones (could make it a smart lookup (i.e. episode name or peertube id))
#autosubber('/chikichikitube/raw/gakinotsukai/episode/#0751 (2005.04.03) - Cosplay Tour Bus 6.avi', 'gakinotsukai_20050403_751_0_ja.avi')