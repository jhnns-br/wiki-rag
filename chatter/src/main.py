from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain import hub
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers import ContextualCompressionRetriever

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # must match model in embedder
COLLECTION_NAME = "wiki-splits_MiniLM-L12-v2_1000-200"  # your collection's name
DEVICE = "cuda:1"
LLM_BASE_URL = "http://<some server's ip>:11434"  # define llm endpoint here
QDRANT_CLIENT_URL = "http://<some server's ip>:6333"  # define qdrant endpoint here

# set up necessary stuff
# embedding model
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={'device': DEVICE}
)

# llm 
llm = Ollama(model="mistral")
llm.base_url=LLM_BASE_URL

# connect to vector store
qdrant = Qdrant(
    client=QdrantClient(url=QDRANT_CLIENT_URL),
    collection_name=COLLECTION_NAME,
    embeddings=embeddings
)

# build retriver 
retriever = qdrant.as_retriever(search_type="similarity", search_kwargs={"k":5})

# now definig the template; Since the wiki used in our example is mainly in German langugage the prompt is as well
template = """Beantworte die Frage am Ende des Textes anhand der folgenden Informationen. 
Wenn die Antwort nicht in den Informationen enthalten ist, sage, dass du es nicht weißt, versuche nicht, eine Antwort zu erfinden.
Verwende ca. 3 Sätze und fasse dich kurz. 

<insert some more helpful context, like commonly used abbreviations, here>

{context}

Frage: {question}
"""

prompt = PromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# set up fastapi
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/answer/{question}")
def read_answer_question(question: str):
    answer = rag_chain.invoke(question)
    return {"answer": answer}

@app.get("/chunks/{question}")
def read_wiki_chunks(question: str):
    chunks = qdrant.similarity_search_with_score(question, k=5)
    ret = [f"{s} || {d.metadata['title']} || {d.metadata['source']}" for d,s in chunks] 
    return {"chunks": ret}
