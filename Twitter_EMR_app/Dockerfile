FROM python:3.6-alpine
RUN mkdir /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache -r app/requirements.txt
COPY ./twitter.py /app/twitter.py
COPY ./jobmanager.py /app/job.py
COPY ./mrjob.conf /app/mrjob.conf
COPY ./mrjobplaces.py /app/mrjobplaces.py
COPY ./diccionaries.py /app/diccionaries.py
COPY ./states.py /app/states.py
#twitter enviroment variables
ENV DOWNLOAD_TIME="0.001"
ENV TWEETER_ACCOUNT=""
ENV API_KEY=""
ENV API_SECRET=""
ENV API_TOKEN=""
ENV API_TOKEN_SECRET=""
#emr enviroment variables
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV INSTANCE_TYPE="c1.medium"
ENV NUM_CORE_INSTANCES="1"
#mongodb enviroment variables
ENV MONGODB_HOST="mongo"
ENV MONGODB_PORT="27017"


CMD ["python" , "/app/jobmanager.py"]


