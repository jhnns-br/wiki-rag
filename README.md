# Wiki RAG ...

... or how we built a chatbot for our confluence wiki system. 

## Overview 

The system follows the basic RAG (retrival augmented generation) approach to let users 
query information from an atlassian confluence wiki system using a LLM. The implementation
is based on [LangChain](https://www.langchain.com/), [Ollama](https://github.com/ollama/ollama), [Qdrant](https://qdrant.tech/), and (obviously) [Docker](https://www.docker.com/). We used [FastAPI](https://fastapi.tiangolo.com/) for seeting up interfaces and 
[Streamlit](https://streamlit.io/) to build a small GUI. 

Currently, the system architecture looks like follows:

![System architecture](https://github.com/jhnns-br/wiki-rag/blob/main/images/system%20architecture.drawio.png)

The *embedder* module may be run sporadically to access the wiki's content, split it 
into chunks, embedde these chunks using an embedding model, and store chunks and 
cooresponding embeddings in a Qdrant vector store. 

The *chatter* retrives similar chunks of text from the store for a given query (question)
and gives these chunks, togehter with the question and some more context, to *Ollama*, which then
generates an answer. These functions are offerred via REST API. 

The *frontend* simply offers a streamlit-built GUI for the user, which looks like this:

![Sneak peak](https://github.com/jhnns-br/wiki-rag/blob/main/images/sneak%20peak.png))
 
## Setup
### Indexing with the embedder module
1. If not already running, start qdrant using 
`docker run -p 6333:6333 -p 6334:6334 -v 
$(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
`.

2. Run the code in *embedder/src/main.py* to load the wiki, index it, and add the collection to qdrant. 
This may be done using VS Code's devcontainers tool, see also *embedder/.devcontainer/devcontainer.json*. 

### Query and answer with the chatter module 

1. the chatter requires a running ollama docker container, start it via `
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama`
and run mistral (or any other model) via `docker exec -it ollama ollama run mistral`.
Note, that it may be necessary to include the `--privileged` flag. 

2. Run the container in chatter to retrive matching documents from a collection in the qdrant store and
hand it to the LLM, either via devcontainers or by building the image via (while in dir chatter)`
docker build -t wikibot/chatter:0.1.0 .`
and then running it via `
docker run -d --gpus=all --privileged -p 8000:8000 wikibot/chatter:0.1.0 fastapi dev /app/src/main.py --host 0.0.0.0 --port 8000
`. 
If you ran it in devcontainers, start the server via fastapi, using `
fastapi dev src/main.py --host 0.0.0.0 --port 8000 
`
This API offers two methods accessible via  *10.157.82.23:8000/chunks/{question}* or 
*...8000/answers/{question}*. They retrun a *str* containing the top-k matches and their similarity score 
or an answer from the LLM, respectively.  

### Host the user frontend with the frontend module 

Start the frontend like done with the chatter, either as a devcontainer or first building it via 
`
docker build -t wikibot/frontend:0.1.0 .
` and then (making sure you are in the desired directory, because of the volume mounting) running it via
`
docker run -d -p 8501:8501 -v $(pwd)/feedback:/app/feedback wikibot/frontend:0.1.0 streamlit run /app/src/main.py
`.

## Notes and further improvement potentials  

**Improving the retrival process and the prompt**
- Removing irrelevant context by, e.g., setting a threshold on the similarities, see: https://python.langchain.com/docs/modules/data_connection/retrievers/contextual_compression/
- Including metadata in the context or choosing context based on metadata 
- Further investigation of the LLM; Accumulation of old representations in the model's latent space should be
avoided. 

**Application/deployment-related**
- Move variables like IP addersses etc. to a shared config
- Use runner to automatically create embeddigs

