import os
import boto3
from io import BytesIO
from pypdf import PdfReader
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from urllib.parse import urlparse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


# ------------------------
# AWS Clients
# ------------------------
s3 = boto3.client("s3")


# ------------------------
# Helpers
# ------------------------
def parse_metadata_from_filename(filename: str) -> dict:
    """
    Expected format: Microsoft-2024-Annual-Report.pdf
    """
    name = filename.replace(".pdf", "")
    parts = name.split("-")

    if len(parts) < 3:
        raise ValueError(f"Invalid filename format: {filename}")

    return {
        "company": parts[0],
        "year": int(parts[1]),
        "doctype": "-".join(parts[2:]),
        "source": filename,
    }


def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )


def chunk_text(text: str, metadata: dict):
    splitter = get_text_splitter()
    doc = Document(page_content=text, metadata=metadata)
    return splitter.split_documents([doc])


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Safe PDF text extraction using pypdf
    """
    reader = PdfReader(BytesIO(pdf_bytes))
    texts = []

    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            texts.append(page_text)

    return "\n".join(texts)


def get_embedding_model():
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=15,
        max_retries=2
    )


def get_opensearch_client():
    raw_host = os.getenv("OPENSEARCH_HOST")
    if not raw_host:
        raise ValueError("OPENSEARCH_HOST env var not set")

    # Normalize host (strip https:// safely)
    parsed = urlparse(raw_host if raw_host.startswith("http") else f"https://{raw_host}")
    host = parsed.hostname
    port = parsed.port or 443

    region = os.getenv("AWS_REGION", "ap-south-2")

    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        "es",
        session_token=credentials.token,
    )

    return OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30,
        max_retries=3,
        retry_on_timeout=True,
    )


# ------------------------
# Lambda Handler
# ------------------------
def handler(event, context):
    print("🔥 Lambda handler started")
    print("Event received")

    try:
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"📄 Processing file: s3://{bucket}/{key}")

        # 1️⃣ Download PDF
        response = s3.get_object(Bucket=bucket, Key=key)
        pdf_bytes = response["Body"].read()
        print(f"⬇️ PDF downloaded ({len(pdf_bytes)} bytes)")

        # 2️⃣ Extract text
        text = extract_text_from_pdf(pdf_bytes)
        if not text.strip():
            raise ValueError("No text extracted from PDF")

        print(f"📝 Extracted text length: {len(text)}")

        # 3️⃣ Metadata + chunking
        metadata = parse_metadata_from_filename(os.path.basename(key))
        chunks = chunk_text(text, metadata)
        print(f"✂️ Created {len(chunks)} chunks")

        # 4️⃣ Clients (created INSIDE handler)
        embedder = get_embedding_model()
        opensearch = get_opensearch_client()
        index_name = os.getenv("OPENSEARCH_INDEX")

        if not index_name:
            raise ValueError("OPENSEARCH_INDEX env var not set")

        # 5️⃣ Embed + index
        for i, chunk in enumerate(chunks):
            print(f"🔢 Embedding chunk {i + 1}/{len(chunks)}")

            vector = embedder.embed_query(chunk.page_content)

            document = {
                "content": chunk.page_content,
                "embedding": vector,
                **chunk.metadata,
            }

            opensearch.index(
                index=index_name,
                body=document,
            )

        print("✅ Ingestion completed successfully")

        return {
            "status": "success",
            "file": key,
            "chunks_indexed": len(chunks),
        }

    except Exception as e:
        print("❌ ERROR during ingestion")
        print(str(e))
        raise