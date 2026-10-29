# Rebuild regularly for AWS's patched base; package versions and hashes are locked below.
FROM public.ecr.aws/lambda/python:3.12
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN python -m pip install --no-cache-dir --require-hashes -r ${LAMBDA_TASK_ROOT}/requirements.txt --target ${LAMBDA_TASK_ROOT}
COPY common ${LAMBDA_TASK_ROOT}/common
COPY data ${LAMBDA_TASK_ROOT}/data
COPY .env.example ${LAMBDA_TASK_ROOT}/.env.example
ENV PYTHONUTF8=1 OTEL_SDK_DISABLED=true
CMD ["common.production_support.lambda_handler"]
