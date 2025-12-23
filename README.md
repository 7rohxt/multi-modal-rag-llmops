# Annual Report RAG Chatbot 
An end-to-end Retrieval-Augmented Generation (RAG) system for answering analytical questions over company annual reports.


## Architecture Overview 
- Frontend: Static UI hosted on S3, delivered via CloudFront  
- Backend: FastAPI + Gunicorn API behind Application Load Balancer (ALB)  
- Retrieval: OpenSearch (BM25 + dense vectors)  
- Reranking: Cross-encoder–based reranker (top-k refinement)  
- Caching: ElastiCache Redis (LLM response & routing cache)  
- Infra / Ops: Docker, AWS EC2, CloudFront, ALB  


## Architecture Diagram 
<img src="assets/architecture.png" width="100%" />


## Output Images 

## AWS CloudFront Deployment

<img src="assets/cloudfront_deployfinal.png" width="100%" />

#### Lambda Ingestion: S3 → OpenSearch

<p align="center">
  <img src="assets/ingestion_cloudwatch_cropped.png" width="49%" height="460" />
  <img src="assets/ingestion_cloudwatch2_cropped.png" width="49%" height="460" />
</p>

### Guardrails 

**Off-topic guardrail**  
<img src="assets/off_topic_guardrail.png" width="100%" />

**Token-level redaction**  
<img src="assets/token_level_redaction.png" width="70%" />

#### Cache Hit (AWS ElastiCache)
<img src="assets/cache_hit.png" width="35%" />

## How to Run & Deploy

This project is designed to run as a containerized backend on AWS, with a static frontend served via CloudFront.

**Prerequisites:** AWS account, Docker, OpenSearch knowledge

### Data Ingestion Pipeline (One-time Setup)

1. **Lambda Function Deployment**
   - Build the Lambda Docker image from `src/aws_infra/lambda_ingestion/`
   - Push the image to **Amazon ECR**
   - Create a Lambda function using the ECR image
   - Configure environment variables (OpenSearch host, index name, OpenAI API key)

2. **S3 Trigger Configuration**
   - Create an S3 bucket for raw documents (PDFs)
   - Add an S3 event trigger: `s3:ObjectCreated:*` → Lambda function
   - Upload PDFs with naming format: `CompanyName-Year-DocType.pdf` (e.g., `Microsoft-2024-Annual-Report.pdf`)

3. **Verification**
   - Check CloudWatch Logs for ingestion progress
   - Verify chunks are indexed in OpenSearch via Dashboards

### Backend (RAG API)

1. **Provision & Configure Infrastructure**
   - Create an **OpenSearch domain**
   - Apply the index mapping from `src/aws_infra/opensearch/index_mapping.json` via OpenSearch Dashboards
   - Set up **ElastiCache (Redis)** for caching
   - Create an **ECR repository** for the backend image
   - Create a `.env` file with required credentials (see `CONFIGURATION.md`)

2. **Container Build & Deployment**
   - Build the backend Docker image locally
   - Push the image to **Amazon ECR**
   - Launch an **EC2 instance**, install Docker, and pull the image from ECR
   - Run the container exposing the FastAPI service on port `8000`

3. **Public Access**
   - Create an **Application Load Balancer (ALB)** pointing to the EC2 instance
   - Verify the backend is reachable via the ALB DNS endpoint


### Frontend (Static UI)

1. Upload `index.html` to an **S3 bucket**
2. Create a **CloudFront distribution** with S3 as the origin
3. Update the frontend to call the backend **CloudFront API endpoint**
4. Access the application via the frontend CloudFront URL


### Traffic Flow (High Level)

```
Browser → CloudFront (Frontend) → S3 (index.html)
        ↓
Browser → CloudFront (Backend API) → ALB → EC2 (FastAPI + Gunicorn)

```


## Folder Structure

```text
.
├── assets/                    # Architecture diagrams & output screenshots
│
├── backend_server/            # FastAPI backend
│   └── app.py                
│
├── front_end/                 # Static frontend
│   └── index.html             
│
├── notebooks/                 # Development & experimentation notebooks
│
├── src/                       # Core RAG logic
│   ├── aws_infra/             # AWS-related components
│   │   ├── lambda_ingestion/  # S3 → OpenSearch ingestion
│   │   │    └── ingestion.py
│   │   └── opensearch/        # OpenSearch client & helpers
│   │        ├── client.py
│   │        └── index_mapping.json 
│   ├── caching.py            
│   ├── generation.py         
│   ├── guardrails.py          
│   ├── memory.py              
│   ├── prompts.py            
│   ├── rerankers.py           
│   ├── retrieval.py           
│   └── router.py              
│
├── .dockerignore
├── .gitignore
├── Dockerfile                 # Backend container image
├── README.md                  # Project documentation
├── main.py                    # RAG pipeline entry point (router → retrieval → rerank → generate)
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables (not committed)
```
## Acknowledgments

This project leverages the following tools and platforms:

- **FastAPI** for building the backend API  
- **Gunicorn** for production-grade ASGI serving  
- **OpenSearch** for hybrid retrieval (BM25 + vector search)  
- **Redis (ElastiCache)** for caching LLM responses and routing decisions  
- **Docker** for containerization  
- **AWS EC2** for backend hosting  
- **Application Load Balancer (ALB)** for traffic management  
- **Amazon S3** for static frontend hosting  
- **Amazon CloudFront** for CDN and secure content delivery  


## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome — please open an issue or submit a pull request with a clear description of your changes.