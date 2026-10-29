FROM public.ecr.aws/docker/library/python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.txt
COPY common common
COPY data data
COPY .env.example .env.example
ENV PYTHONUTF8=1 OTEL_SDK_DISABLED=true HOME=/tmp
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "common.deployment_apps", "fargate", "--host", "0.0.0.0", "--port", "8080"]
