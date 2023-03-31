# subtitles

A public repo of up to date sub files for Chiki Chiki Tube videos, some of which have been machine generated

If you'd like to update an existing sub file, or take a machine generated subfile and turn it into a proper manual sub yourself, raise an issue with the episode name for tracking purposes

## Contents 
**File Name Format**
 `showname_airdate_episodenumber_videolanguage_subtitlelanguage`

### Autosub
Installation script and python script (for Ubuntu)

### subtitles_original
Subs extracted from The Silent Library versions of videos

### subtitles_machine
SRT sub files for unsubbed videos that have been transcribed/translated using [OpenAI Whisper](https://github.com/openai/whisper)

### subtitles_conformed
The original subtitle files mass edited to only have 10 common fonts to increase compatibility

### subtitles_conform.ipynb
Jupyter notebook for the conforming process

## Autosub - Machine learning transcription and translation

### Steps
1. You will need a folder of your videos and a csv called `sourcepath.csv` with a `filepath` (where the video file is) column and a `newpath` column (which is where the sub file goes)
2. Install WhisperAI (AMD/Linux script: [autosub.sh](autosub/autosub.sh))
3. Run the whisperai python script [autosub.py](autosub/autosub.py)
4. You will recieve SRT format subtitles files as output

### Issues
1. Translation
	- If there's a lot of noise or people talking at once the AI has a hard time picking out words and the translation becomes nonsense
	- Even with perfectly clear audio the translator can't accurately use pronouns, or always correctly identify names
	- This is all done through audio, so no on screen text is translated (this can be done manually with [Yandex OCR](https://translate.yandex.com/ocr))
2. Timings
	- Whisper only times to the nearest second, so subs can be as much as 0.5 seconds off
	- Sometimes the subs start to drift; sometimes it gets corrected in a few seconds, sometimes the drift persists throughout the rest of the video
	- Long run on sentences are usually cut up pretty badly
	- The AI always seems to want text on screen, so if there's a long pause in people talking the last subbed line will linger way too long
