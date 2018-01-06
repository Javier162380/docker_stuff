FROM python:3.6-alpine
RUN mkdir /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache -r app/requirements.txt
COPY ./twitter.py /app/twitter.py
COPY ./jobmanager.py /app/jobmanager.py
COPY ./mrjob.conf /app/mrjob.conf
COPY ./mrjobplaces.py /app/mrjobplaces.py
COPY ./diccionaries.py /app/diccionaries.py
COPY ./states.py /app/states.py
#twitter enviroment variables
ENV DOWNLOAD_TIME="0.001"
ENV TWEETER_ACCOUNT=""
ENV API_KEY="rfEyBrskP5FHtxBpdVnWfXoT9"
ENV API_SECRET="YhHr20cYWbr0c996aiILnzmM9b0ombCgGOPdnerxuu4RDcWBPG"
ENV API_TOKEN="1451037732-hyu3XFKQWX9hL66hDqm2C3WDLGOUVnyPUkj0CPp"
ENV API_TOKEN_SECRET="TzcvxYXuRVXcA71oVi1x0bEBehseSLW2HcQoJniNvDGva"
#emr enviroment variables
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV INSTANCE_TYPE="c1.medium"
ENV NUM_CORE_INSTANCES="1"
#mongodb enviroment variables
ENV MONGODB_HOST="mongo"
ENV MONGODB_PORT="27017"


CMD ["python" , "/app/jobmanager.py"]


