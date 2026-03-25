import numpy as np
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import requests 

#setting up llm model
def inference(prompt):
    r = requests.post("http://localhost:11434/api/generate", json={
        # "model": "deepseek-r1",
        "model": "llama3.2",
        "prompt": prompt,
        "stream" : False
    })
    response = r.json()
    print(response)
    return response

df = joblib.load('embeddings.joblib')

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

incoming_query = input("Ask a question:- ")
question_embedding= create_embedding([incoming_query])[0]

similarities = cosine_similarity(np.vstack(df['embedding']),[question_embedding]).flatten()

top_results = 5
max_indx = (similarities.argsort()[::-1][:top_results])    

new_df = df.loc[max_indx]
#our answer to our question is:
#print(new_df[["title","number","text"]])


#prompt for RAG based system (orient="records" basically gives list of dictionaries)
prompt = f'''I am teaching basics of AI cource. Here are video subtitle chunks containing video title, video number, start time in seconds, end time in seconds, the text at that time:

{new_df[["title","number","start","end","text"]].to_json(orient="records")}
-------------------------
"{incoming_query}"
the user asked this question related to the video chunks, you have to answer in a human way(dont mention the above format, its just for you) where and how much content is taught in which video (in which video and what timestamp) and guide guide the user to go to that particular video. If user asks unrelated question, tell him that you can only ask questions related to the cource .
'''

with open("prompt.txt" , "w") as f:
    f.write(prompt)

response = inference(prompt)["response"]
print(response)

with open("response.txt" , "w") as f:
    f.write(response)

# for index, item in new_df.iterrows():
#     print(index, item["title"], item["number"], item["text"],item["start"],item["end"])

#our response.txt contain our answer