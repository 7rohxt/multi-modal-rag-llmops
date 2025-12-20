# infra/opensearch/client.py

import os
import boto3
from urllib.parse import urlparse
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection


def get_opensearch_client():
    raw_host = os.getenv("OPENSEARCH_HOST")
    if not raw_host:
        raise ValueError("OPENSEARCH_HOST not set")

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
        timeout=60,
        max_retries=3,
        retry_on_timeout=True,
    )
