Powershell commands to build image -> ecr push -> ecr pull -> update lambda
```
# Set variables
>> $AWS_REGION = "ap-south-2"
>> $AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
>> $REPO_NAME = "document-ingestion-lambda"
>> $FUNCTION_NAME = "rag-s3-opensearch-ingestion-img"
>>
>> # 1. Clean build (no cache)
>> Write-Host "🔨 Building Docker image (this may take a few minutes)..." -ForegroundColor Yellow
>> docker build -t $REPO_NAME . --no-cache
>>
>> # Check if build succeeded
>> if ($LASTEXITCODE -ne 0) {
>>     Write-Host "❌ Docker build failed!" -ForegroundColor Red
>>     exit 1
>> }
>>
>> Write-Host "✅ Build successful!" -ForegroundColor Green
>>
>> # 2. Login to ECR
>> Write-Host "🔐 Logging into ECR..." -ForegroundColor Yellow
>> aws ecr get-login-password --region $AWS_REGION | `
>>   docker login --username AWS --password-stdin `
>>   "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
>>
>> # 3. Tag image
>> Write-Host "🏷️ Tagging image..." -ForegroundColor Yellow
>> docker tag "${REPO_NAME}:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${REPO_NAME}:latest"
>>
>> # 4. Push to ECR
>> Write-Host "⬆️ Pushing to ECR..." -ForegroundColor Yellow
>> docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${REPO_NAME}:latest"
>>
>> if ($LASTEXITCODE -ne 0) {
>>     Write-Host "❌ Push failed!" -ForegroundColor Red
>>     exit 1
>> }
>>
>> Write-Host "✅ Push successful!" -ForegroundColor Green
>>
>> # 5. Update Lambda
>> Write-Host "🔄 Updating Lambda function..." -ForegroundColor Yellow
>> aws lambda update-function-code `
>>   --function-name $FUNCTION_NAME `
>>   --image-uri "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${REPO_NAME}:latest" `
>>   --region $AWS_REGION
>>
>> # 6. Wait for Lambda to finish updating
>> Write-Host "⏳ Waiting for Lambda to update..." -ForegroundColor Yellow
>> aws lambda wait function-updated --function-name $FUNCTION_NAME --region $AWS_REGION
>>
>> Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
>> Write-Host "Function: $FUNCTION_NAME" -ForegroundColor Cyan
```
