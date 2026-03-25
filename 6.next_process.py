import numpy as np
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import requests # as we are going to require create_embeddings() function

df = joblib.load('embeddings.joblib')

#studied in detail in 3.read_chunks.py
def create_embedding(text_list):
    embeddings = []
    for text in text_list:
        if text is None or not str(text).strip():
            text = "empty content"
        r = requests.post("http://localhost:11434/api/embeddings", json={
            "model": "bge-m3",
            "prompt": text
        })
        data = r.json()
        if "embedding" not in data:
            r = requests.post("http://localhost:11434/api/embeddings", json={
                "model": "bge-m3",
                "prompt": "placeholder text"
            })
            data = r.json()
        embeddings.append(data["embedding"])
    return embeddings

#studied in detail in 4.pulling_matching_chunks.py
incoming_query = input("Ask a question:- ")
question_embedding= create_embedding([incoming_query])[0]

similarities = cosine_similarity(np.vstack(df['embedding']),[question_embedding]).flatten()
# print(similarities)
top_results = 3
max_indx = (similarities.argsort()[::-1][:top_results])    
# print(max_indx)      

new_df = df.loc[max_indx]
# print(new_df[["title","number","text"]])


for index, item in new_df.iterrows():
    print(index, item["title"], item["number"], item["text"],item["start"],item["end"])