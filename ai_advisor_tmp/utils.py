from typing import List, Dict, Any, Tuple, Optional
import yaml
import os

cwd = os.getcwd()
os.environ["PYTORCH_TRANSFORMERS_CACHE"] = os.path.join(
    cwd, "huggingface/transformers/"
)
os.environ["TRANSFORMERS_CACHE"] = os.path.join(cwd, "huggingface/transformers/")
os.environ["HF_HOME"] = os.path.join(cwd, "huggingface/")
import logging
import json
from time import sleep, time

import requests
import streamlit as st

from pathlib import Path

from haystack.pipelines.base import Pipeline
from haystack.nodes import EmbeddingRetriever, Shaper
from haystack.document_stores import FAISSDocumentStore, InMemoryDocumentStore
from haystack.errors import PipelineConfigError
# from googletrans import Translator
import openai

try:
    from api import openai as api_key
except ImportError:
    api_key = os.environ["OPENAI_API_KEY"]
    
openai.api_key = api_key

logger = logging.getLogger(__name__)
pipelines = None

system_prompt_template = """You are an US experienced immigration attorney.  Your answer should be in your own words, be detailed and be no longer than 350 words. 
You should ask for more information or clarifications to give a more precise answer for an each client's case. 
Synthesize a comprehensive answer from your knowledge and the following topk most relevant paragraphs and the given question.
Do not tell them to have a consultation with a certified attorney. Clients have been warned that you are our assistant and that's enough. 
Give an answer in the {0} language.
"""
users_prompt_template = """
Paragraphs: {0}

Question: {1}
"""
# Since each instance of FAISSDocumentStore creates an in-memory FAISS index, the Indexing & Query Pipelines would
# end up with different indices. The same applies for InMemoryDocumentStore.
UNSUPPORTED_DOC_STORES = (FAISSDocumentStore, InMemoryDocumentStore)

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000")
STATUS = "initialized"
HS_VERSION = "hs_version"
DOC_REQUEST = "query"
DOC_FEEDBACK = "feedback"
DOC_UPLOAD = "file-upload"

# translator = Translator()


def query(
    pipelines, query, filters={}, language="en", top_k_reader=3, top_k_retriever=5
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Send a query to the REST API and parse the answer.
    Returns both a ready-to-use representation of the results and the raw JSON.
    """
    query_pipeline = pipelines.get("query_pipeline", None)
    start_time = time()

    params = {
        "retriever": {"top_k": top_k_retriever},
    }

    lang = language.lower() or "english"

    response = query_pipeline.run(
        query=query,
        params=params,
    )
    context = ""
    sources = []
    for doc in response["documents"]:
        doc = doc.to_dict()
        doc_name = doc["meta"].get("name")
        doc_url = doc["meta"].get("url")
        source = (
            "https://www.uscis.gov/sites/default/files/document/forms/" + doc_name
            if doc_name
            else doc_url
        )
        if not source.endswith('.txt'):
            sources.append(source)
        if len(context)<top_k_reader:
            context += " " + doc.get("content")
    # Ensure answers and documents exist, even if they're empty lists
    if not "documents" in response:
        response["documents"] = []

    # prepare openAI api call
    messages = []
    system_prompt = system_prompt_template.format(lang)
    user_prompt = users_prompt_template.format(context, response["query"])
    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    bot_response = openai_response["choices"][0]["message"]["content"]
    response["answers"] = [bot_response]
    logger.info(
        json.dumps(
            {
                "request": query,
                "response": response,
                "time": f"{(time() - start_time):.2f}",
            },
            default=str,
        )
    )

    # Format response
    results = []
    answers = response["answers"]
    documents = response["documents"]
    for answer, doc in zip(answers, documents):
        doc = doc.to_dict()
        if answer:
            context = doc.get("content")
            results.append(
                {
                    "context": "..." + context if context else "",
                    "answer": answer,
                    "source": "\n".join(sources),
                    "_raw": answer,
                }
            )
        else:
            results.append({"context": None, "answer": None, "_raw": answer})
    return results, response


def send_feedback(
    query, answer_obj, is_correct_answer, is_correct_document, document
) -> None:
    """
    Send a feedback (label) to the REST API
    """
    url = f"{API_ENDPOINT}/{DOC_FEEDBACK}"
    req = {
        "query": query,
        "document": document,
        "is_correct_answer": is_correct_answer,
        "is_correct_document": is_correct_document,
        "origin": "user-feedback",
        "answer": answer_obj,
    }
    response_raw = requests.post(url, json=req)
    if response_raw.status_code >= 400:
        raise ValueError(
            f"An error was returned [code {response_raw.status_code}]: {response_raw.json()}"
        )


def upload_doc(file):
    url = f"{API_ENDPOINT}/{DOC_UPLOAD}"
    files = [("files", file)]
    response = requests.post(url, files=files).json()
    return response


def get_backlink(result) -> Tuple[Optional[str], Optional[str]]:
    if result.get("document", None):
        doc = result["document"]
        if isinstance(doc, dict):
            if doc.get("meta", None):
                if isinstance(doc["meta"], dict):
                    if doc["meta"].get("url", None) and doc["meta"].get("title", None):
                        return doc["meta"]["url"], doc["meta"]["title"]
    return None, None


def setup_pipelines() -> Dict[str, Any]:
    # Re-import the configuration variables
    import config  # pylint: disable=reimported

    pipelines = {}
    document_store = FAISSDocumentStore(
        faiss_config_path="faiss.json", faiss_index_path="faiss.index"
    )
    retriever = EmbeddingRetriever(
        document_store=document_store,
        batch_size=128,
        embedding_model="ada",
        api_key=api_key,
        max_seq_len=1024,
    )

    shaper = Shaper(
        func="join_documents", inputs={"documents": "documents"}, outputs=["documents"]
    )

    pipe = Pipeline()
    pipe.add_node(component=retriever, name="retriever", inputs=["Query"])

    logging.info(f"Loaded pipeline nodes: {pipe.graph.nodes.keys()}")
    pipelines["query_pipeline"] = pipe

    # Find document store

    logging.info(f"Loaded docstore: {document_store}")
    pipelines["document_store"] = document_store

    indexing_pipeline = None
    # Load indexing pipeline (if available)
    try:
        indexing_pipeline = Pipeline.load_from_yaml(
            Path(config.PIPELINE_YAML_PATH), pipeline_name=config.INDEXING_PIPELINE_NAME
        )
        docstore = indexing_pipeline.get_document_store()
        if isinstance(docstore, UNSUPPORTED_DOC_STORES):
            indexing_pipeline = None
            raise PipelineConfigError(
                "Indexing pipelines with FAISSDocumentStore or InMemoryDocumentStore are not supported by the REST APIs."
            )

    except PipelineConfigError as e:
        indexing_pipeline = None
        logger.error(f"{e.message}\nFile Upload API will not be available.")

    finally:
        pipelines["indexing_pipeline"] = indexing_pipeline

    # Create directory for uploaded files
    os.makedirs(config.FILE_UPLOAD_PATH, exist_ok=True)

    return pipelines


def get_pipelines():
    global pipelines  # pylint: disable=global-statement
    if not pipelines:
        pipelines = setup_pipelines()
    return pipelines
