#converts the videos to mp3
#we can do this process of converting mp4 to mp3 or any format to mp3 using ffmpeg
#just type in terminal say for video1.mp4 type "ffmpeg -i video1.mp4 -q:a 0 -map a output.mp3"
#we have to do simplar process in code format

import os
import subprocess

files=os.listdir("Videos_test")

ffmpeg_path = "ffmpeg"
if os.path.exists("./ffmpeg.exe"):
    ffmpeg_path = "./ffmpeg.exe"
elif os.path.exists("ffmpeg.exe"):
    ffmpeg_path = "ffmpeg.exe"

for file in files:
    if not file.endswith(".mp4"):
        continue

    #for name in format <......................anything.......... tutoril 2.mp4>
    name_no_ext = file.split(".mp4")[0]
    if " tutorial " in name_no_ext:
        tutorial_number = name_no_ext.split(" tutorial ")[1]
        tutorial_name = name_no_ext.split(" tutorial ")[0]
    else:
        tutorial_number = "1"
        tutorial_name = name_no_ext
        
    print(tutorial_number , tutorial_name)
    
    #convert it to format "ffmpeg -i video1.mp4 -q:a 0 -map a output.mp3"
    try:
        # added -y to overwrite if exists, preventing ffmpeg from prompting Y/N
        subprocess.run([ffmpeg_path,"-y","-i",f"Videos_test/{file}","-q:a","0","-map","a",f"1.converted_audios/{tutorial_number}_{tutorial_name}.mp3"], check=True)
    except FileNotFoundError:
        print("ERROR: ffmpeg is not installed on this system. It is required to extract audio from video.")
        raise
    except Exception as e:
        print(f"Error during ffmpeg processing: {e}")
        raise