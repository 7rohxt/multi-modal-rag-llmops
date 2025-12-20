import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()


def parse_metadata_from_filename(filename):
    # Example: "Microsoft-2024-Annual-Report.pdf"
    name = filename.replace(".pdf", "")
    parts = name.split("-")

    company = parts[0]                # Microsoft
    year = int(parts[1])              # 2024
    doctype = "-".join(parts[2:])     # Annual-Report

    return company, year, doctype


def load_all_pdfs(folder="../knowledge_base"):
    all_docs = []

    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(folder, file)
            print("Loading:", pdf_path)

            # Extract structured metadata from filename
            company, year, doctype = parse_metadata_from_filename(file)

            # Load PDF pages as documents
            loader = PyMuPDFLoader(pdf_path)
            docs = loader.load()

            for d in docs:
                # ❗ ERASE ANY EXISTING METADATA
                d.metadata = {}

                # Inject your clean, structured metadata
                d.metadata["source"] = file
                d.metadata["company"] = company
                d.metadata["year"] = year
                d.metadata["doctype"] = doctype
                d.metadata["page"] = d.metadata.get("page", None)   # preserve original page if needed

            all_docs.extend(docs)

    return all_docs


def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )


def chunk_docs(docs, splitter):
    return splitter.split_documents(docs)


def get_embedding_model():
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.getenv("MY_OPENAI_API_KEY")
    )


def build_faiss(chunks, embedding, save_dir="faiss_index"):
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embedding
    )
    vectorstore.save_local(save_dir)
    print("FAISS index saved at:", save_dir)
    return vectorstore



if __name__ == "__main__":

    docs = load_all_pdfs("../knowledge_base")
    splitter = get_text_splitter()
    chunks = chunk_docs(docs, splitter)
    embedding = get_embedding_model()
    vectorstore = build_faiss(chunks, embedding, "../faiss_index")
    print("Ingestion complete. Chunks:", len(chunks))