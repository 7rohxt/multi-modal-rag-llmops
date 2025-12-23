# infra/opensearch/client.py

import os
import boto3
from urllib.parse import urlparse
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection


def get_opensearch_client():
    raw_host = os.getenv("OPENSEARCH_HOST")
    if not raw_host:
        raise RuntimeError("OPENSEARCH_HOST not set")

    parsed = urlparse(raw_host if raw_host.startswith("http") else f"https://{raw_host}")
    host = parsed.hostname
    port = parsed.port or 443

    region = os.getenv("AWS_REGION")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not all([region, access_key, secret_key]):
        raise RuntimeError("AWS credentials or region not set in environment variables")

    awsauth = AWS4Auth(access_key, secret_key, region, "es")

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