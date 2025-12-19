FROM public.ecr.aws/lambda/python:3.10

# Install Rust (needed for tiktoken)
RUN yum install -y gcc && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    source $HOME/.cargo/env

ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

# Copy function code
COPY ingestion.py ${LAMBDA_TASK_ROOT}/

# Set handler
CMD ["ingestion.handler"]