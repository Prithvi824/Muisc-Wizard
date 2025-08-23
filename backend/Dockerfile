############################################
# STAGE 1: BUILDING THE APPLICATION
############################################

FROM python:3.11.2-slim AS builder

# copy the requirements.txt
COPY requirements.txt /app/

# install the test dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy everything from the current directory to the /app directory
COPY . /app/

############################################
# STAGE 2: BUILDING THE APPLICATION
############################################
FROM gcr.io/distroless/python3

# copy the important directories
COPY --from=builder /app/ /app/

# copy the installed dependencies
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# make sure the directory with deps are used
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

# expose the port
EXPOSE 8000

# set the working directory
WORKDIR /app

# run the entrypoint.sh script
ENTRYPOINT ["python3", "-m", "gunicorn",  "main:APP", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
