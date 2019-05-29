import moviepy.editor as mp
clip = mp.VideoFileClip("video.mp4")
clip.audio.write_audiofile("theaudio.mp3")

import pydub
sound = pydub.AudioSegment.from_mp3("theaudio.mp3")
sound = sound.set_channels(1)
sound = sound.set_sample_width(2)
sound = sound.set_frame_rate(16000)
sound.export("english.wav", format="wav")
