from dotenv import load_dotenv
load_dotenv()

import os
from langchain.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

openai_api_key = os.getenv("OPENAI_API_KEY")
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

import pandas as pd
df = pd.read_csv("Data  - Transformed Data.csv")
comments = df["Comment"].dropna().tolist()

vectordb = Chroma.from_texts(
    texts=comments,
    embedding=embedding,
    persist_directory="./chroma_style_db"
)
vectordb.persist()
print("✅ VectorDB created and saved.") 
