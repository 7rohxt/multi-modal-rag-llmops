## Create OpenSearch Index for RAG

After creating the OpenSearch domain:

1. Allow your **public IP address** in  
   **Security configuration → Access policy**

2. Open **OpenSearch Dashboards**

3. From the left menu, go to **Dev Tools**

4. Paste and run the following command:

```json
PUT rag-docs
{
  "settings": {
    "index": {
      "knn": true
    }
  },
  "mappings": {
    "properties": {
      "content": {
        "type": "text"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 3072
      },
      "company": {
        "type": "keyword"
      },
      "year": {
        "type": "integer"
      },
      "doctype": {
        "type": "keyword"
      },
      "source": {
        "type": "keyword"
      }
    }
  }
}
