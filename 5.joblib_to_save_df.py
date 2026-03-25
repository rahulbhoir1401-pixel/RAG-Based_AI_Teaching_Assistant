##Version of ollama is imp
#pip install requests
#we use ollama
#install bgem-3 using "ollama pull bge-m3"
#ollama local instance por is 11434

import requests

#in order to read my 2.jsons_chunks
import os
import json
import pandas as pd

#for cosine similarity
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

#for saving data in df
import joblib

#function to give embeddings
def create_embedding(text_list):
    # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-embeddings
    embeddings = []

    for text in text_list:
        # make sure text is always valid
        if text is None or not str(text).strip():
            text = "empty content"

        r = requests.post("http://localhost:11434/api/embeddings", json={
            "model": "bge-m3",
            "prompt": text
        })

        data = r.json()

        # if Ollama fails, retry with guaranteed-safe text
        if "embedding" not in data:
            r = requests.post("http://localhost:11434/api/embeddings", json={
                "model": "bge-m3",
                "prompt": "placeholder text"
            })
            data = r.json()

        embeddings.append(data["embedding"])

    return embeddings


#take an example
# a= create_embedding(["cat sat on the mat", "my name is shreyash"])
# print(a)

jsons = os.listdir("2.jsons_chunks")       #list all the jsons
# print(jsons)

my_dicts = [] #create empty list
chunk_id = 0 #to keep track of chunks

for json_file in jsons:
    with open(f"2.jsons_chunks/{json_file}") as f:
        content = json.load(f)
    print(f"Creating Embeddings for {json_file}")

    embeddings = create_embedding([c['text'] for c in content['chunks']])
       
    for i, chunk in enumerate(content['chunks']):
        chunk['chunk_id'] = chunk_id
        chunk['embedding'] = embeddings[i]
        chunk_id += 1
        my_dicts.append(chunk) 
        
    #     #for taking some line of df as test
    #     if (i==3):
    #         break
    #   break
# print(my_dicts)

df = pd.DataFrame.from_records(my_dicts)
# print(df)

#save this df

joblib.dump(df, 'embeddings.joblib')