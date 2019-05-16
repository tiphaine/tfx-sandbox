FROM python:2.7

ENV AIRFLOW_HOME /root/airflow
ENV DATA_DIR $AIRFLOW_HOME/data
ENV SERVING_DIR $AIRFLOW_HOME/serving
ENV DAGS_DIR $AIRFLOW_HOME/dags
ENV TFX_DIR $AIRFLOW_HOME/tfx
ENV PIPELINE_DIR $TFX_DIR/pipelines
ENV METADATA_DB_DIR $TFX_DIR/metadata
ENV SLUGIFY_USES_TEXT_UNIDECODE yes

WORKDIR /usr/src/app

# Intall protobuf specific version
RUN curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v3.7.0rc2/protoc-3.7.0-rc-2-linux-x86_64.zip
RUN unzip -o protoc-3.7.0-rc-2-linux-x86_64.zip -d /usr/local bin/protoc
RUN rm protoc*

# Python dependencies
RUN pip install httplib2==0.11.3 tensorflow==1.13.1 tfx==0.12.0 google-api-python-client docker papermill matplotlib networkx
RUN pip install --upgrade notebook==5.7.2
RUN jupyter nbextension install --py --symlink --sys-prefix tensorflow_model_analysis
RUN jupyter nbextension enable --py --sys-prefix tensorflow_model_analysis

# Install airflow
RUN pip install apache-airflow
RUN airflow initdb
RUN sed -i'.orig' 's/dag_dir_list_interval = 300/dag_dir_list_interval = 1/g' ${AIRFLOW_HOME}/airflow.cfg
RUN sed -i'.orig' 's/job_heartbeat_sec = 5/job_heartbeat_sec = 1/g' ${AIRFLOW_HOME}/airflow.cfg
RUN sed -i'.orig' 's/scheduler_heartbeat_sec = 5/scheduler_heartbeat_sec = 1/g' ${AIRFLOW_HOME}/airflow.cfg
RUN sed -i'.orig' 's/dag_default_view = tree/dag_default_view = graph/g' ${AIRFLOW_HOME}/airflow.cfg
RUN sed -i'.orig' 's/load_examples = True/load_examples = False/g' ${AIRFLOW_HOME}/airflow.cfg
RUN sed -i'.orig' 's/dagbag_import_timeout = 30/dagbag_import_timeout = 300/g' ${AIRFLOW_HOME}/airflow.cfg

RUN airflow resetdb --yes
RUN airflow initdb

# Create a run script in order to lunch the airflow webserver and jupyter notebook
RUN echo "airflow webserver &" >> ~/run.sh
RUN echo "airflow scheduler &" >> ~/run.sh
RUN echo "cd notebooks & jupyter notebook --ip 0.0.0.0 --port 8081 --no-browser --allow-root" >> ~/run.sh

COPY notebooks .
COPY src .
COPY data ${DATA_DIR}
COPY dags ${DAGS_DIR}

RUN find ${DATA_DIR} -name ".DS_Store" -type f -delete

ENTRYPOINT bash ~/run.sh