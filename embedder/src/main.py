import time
import json
import logging
from langchain_community.document_loaders import ConfluenceLoader
from langchain_community.document_loaders.confluence import ContentFormat
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from atlassian import Confluence

WIKI_URL = "<url to your wiki>"
WIKI_TOKEN = "<your confluence access token"
WIKI_SPACE_NAME ="<your wiki space name>"
COLLECTION_NAME = "<name of the qdrant collection>"
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # from huggingface 
DEVICE = "cuda:1"
QDRANT_CLIENT_URL = "http://<some server's ip>:6333"  # define qdrant endpoint here
MAX_PAGES = 400  # some number that acts as a termination criterium for the page retrival process

def main():

    # get wiki content
    loader = ConfluenceLoader(
        url=WIKI_URL,
        token=WIKI_TOKEN,
        number_of_retries=5,
        min_retry_seconds=5,
        max_retry_seconds=20
        )

    confluence = Confluence(url=WIKI_URL, token=WIKI_TOKEN, cloud=True)

    # wrapping the retrival process into smaller iterations to avoid server errors
    print("> loading pages from wiki")
    all_pages =[]
    sidx = 0
    while True:
        pages = confluence.get_all_pages_from_space(
            space=WIKI_SPACE_NAME,
            start=sidx,
            limit=100,
            expand="body.storage"
            )
        all_pages.extend(pages)
        time.sleep(1)
        print("> finished loading page batch", sidx)
        sidx += 100
        if sidx > MAX_PAGES:
            break

    # process the page content
    print("> len pages:", len(all_pages), "sample:", all_pages[0])
    docs = loader.process_pages(
        pages=all_pages,
        include_restricted_content=True,
        include_attachments=False,
        include_comments=False,
        content_format=ContentFormat.STORAGE
        )

    all_docs = [x for x in docs]
    print("> len docs:", len(all_docs), "sample:", all_docs[0])

    # split the text in smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
        )

    splits = text_splitter.split_documents(all_docs)
    print("> len splits:", len(splits), "sample:", splits[0])

    # create embeddings for chunks
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs={'device': DEVICE})

    # upload as collection
    qdrant = Qdrant.from_documents(
        splits,
        embeddings,
        url=QDRANT_CLIENT_URL,
        prefer_grpc=True,
        collection_name=COLLECTION_NAME,
        force_recreate=True
    )

    print("> sucessfully added collection")

if __name__ == "__main__":
    main()