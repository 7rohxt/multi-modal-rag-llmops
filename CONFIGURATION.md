# Configuration Guide

This document explains how to configure the RAG application for local development and AWS deployment.

---

## Environment Setup

Create a `.env` file in the project root with the following variables:

---

### OpenAI API

```bash
MY_OPENAI_API_KEY=sk-your-openai-api-key-here
```

**How to obtain:**
- Sign up or log in to [OpenAI Platform](https://platform.openai.com/)
- Navigate to [API Keys](https://platform.openai.com/api-keys)
- Create a new secret key
- Copy and paste into your `.env` file

**Note:** Keep this key secure and never commit it to version control.

---

### AWS Configuration

```bash
AWS_ACCESS_ID=your-aws-access-key-id
AWS_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=ap-south-1
```

**How to obtain:**
1. Log in to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Create a new IAM user or use an existing one
3. Attach policies for:
   - `AmazonS3FullAccess` (for document storage)
   - `AmazonOpenSearchServiceFullAccess` (for vector search)
   - `AmazonElastiCacheFullAccess` (for caching)
4. Generate access keys under "Security credentials"
5. Copy the Access Key ID and Secret Access Key

**Region:** Set to your preferred AWS region (e.g., `us-east-1`, `ap-south-1`, `eu-west-1`)

---

### S3 Bucket

```bash
BUCKET_NAME=your-s3-bucket-name
```

**How to set up:**
1. Create an S3 bucket via [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Choose a globally unique bucket name
3. Select the same region as `AWS_REGION`
4. Use this bucket to store raw document files (PDFs, reports, etc.)

**Example:** `raw-annual-report-docs`

---

### OpenSearch

```bash
OPENSEARCH_HOST=https://your-opensearch-domain.region.es.amazonaws.com
OPENSEARCH_INDEX=rag-docs
```

**How to set up:**
1. Create an OpenSearch domain via [AWS OpenSearch Console](https://console.aws.amazon.com/aos/)
2. Note the domain endpoint (e.g., `https://search-your-domain.region.es.amazonaws.com`)
3. Apply the index mapping from `src/aws_infra/opensearch/index_mapping.json` via OpenSearch Dashboards
4. Set `OPENSEARCH_INDEX` to your index name (default: `rag-docs`)

**Security:** Ensure your IAM user has access to the OpenSearch domain via access policies.

---

### Redis Configuration

#### Local Development (Local Redis)

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
```

**How to set up:**
1. Install Redis locally:
   - **macOS:** `brew install redis`
   - **Linux:** `sudo apt install redis-server`
   - **Windows:** Use [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
2. Start Redis: `redis-server`
3. Verify connection: `redis-cli ping` (should return `PONG`)

---

#### AWS ElastiCache (Production)

```bash
ELASTICACHE_ENDPOINT=your-elasticache-endpoint.cache.amazonaws.com
```

**How to set up:**
1. Create an ElastiCache cluster via [AWS ElastiCache Console](https://console.aws.amazon.com/elasticache/)
2. Choose "Redis" as the engine
3. Select "Serverless" or "Design your own cache" based on your needs
4. Note the primary endpoint (e.g., `your-cache.serverless.region.cache.amazonaws.com`)
5. Ensure your EC2 instance security group allows inbound connections to ElastiCache

**Switching between local and AWS Redis:**
- The application detects the environment automatically
- For local development, ensure `REDIS_HOST` and `REDIS_PORT` are set
- For AWS deployment, ensure `ELASTICACHE_ENDPOINT` is set

---

## Example `.env` File

```bash
# OpenAI API
MY_OPENAI_API_KEY=sk-proj-abc123...

# AWS Configuration
AWS_ACCESS_ID=AKIAIOSFODNN7EXAMPLE
AWS_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=ap-south-1

# S3 Bucket Name
BUCKET_NAME=my-rag-documents

# OpenSearch
OPENSEARCH_HOST=https://search-my-domain.ap-south-1.es.amazonaws.com
OPENSEARCH_INDEX=rag-docs

# Local Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# AWS ElastiCache
ELASTICACHE_ENDPOINT=my-cache.serverless.aps1.cache.amazonaws.com
```

---

## Security Best Practices

- Never commit `.env` to version control (already in `.gitignore`)
- Rotate AWS credentials regularly
- Use IAM roles with least-privilege access
- Enable MFA on your AWS account
- Store production secrets in AWS Secrets Manager or Parameter Store for enhanced security
