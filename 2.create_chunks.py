import whisper
#type "pip install git+https://github.com/openai/whisper.git"
import json
import os

model = whisper.load_model("large-v2")

audios = os.listdir("1.converted_audios")

for audio in audios:
    # print(audio)
    if ("_" in audio):
        number = audio.split("_")[0]
        title = "_".join(audio.split("_")[1:])[:-4]
        print(number , title)
        
        result = model.transcribe(audio = f"1.converted_audios/{audio}", 
        #result = model.transcribe(audio = f"1.converted_audios/7_test-audio-short-file.mp3",  #as computing for all videos will take lot of time
                          language="en",#use "hi"hindi
                          task="transcribe" ,#use "translate" for hindi
                          word_timestamps = False)
        
        #for extracting chunks
        chunks_for_videos=[]
        for segment in result["segments"]:
            #extract necessary info from chunks_for_videos and append it to a json file
            chunks_for_videos.append({"number":number,    "title":title,   "start":segment["start"],    "end":segment["end"],   "text":segment["text"]})

        #for also storing actual text from videos
        chunks_with_metadata = {"chunks":chunks_for_videos , "text":result["text"]}

        with open(f"2.jsons_chunks/{audio}.json","w") as f:
            json.dump(chunks_with_metadata,f)