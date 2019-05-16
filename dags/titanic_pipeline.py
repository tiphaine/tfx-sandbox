
import os
import logging
import datetime

from tfx.components.example_gen.csv_example_gen.component import CsvExampleGen
from tfx.orchestration.airflow.airflow_runner import AirflowDAGRunner
from tfx.orchestration.pipeline import PipelineDecorator
from tfx.utils.dsl_utils import csv_input


data_dir = os.path.join(os.environ['DATA_DIR'], 'titanic')
log_dir = os.path.join(os.environ['TFX_DIR'], 'logs')

logger_overrides = {
    'log_root': log_dir,
    'log_level': logging.INFO
}

airflow_config = {
    'schedule_interval': None,
    'start_date': datetime.datetime(2019, 1, 1),
}

@PipelineDecorator(
    pipeline_name='titanic',
    enable_cache=True,
    metadata_db_root=os.environ['METADATA_DB_DIR'],
    additional_pipeline_args={'logger_args': logger_overrides},
    pipeline_root=os.environ['PIPELINE_DIR']
)
def create_pipeline():
    """Implements the titanic taxi pipeline with TFX."""

    examples = csv_input(data_dir)

    # Brings data into the pipeline
    example_gen = CsvExampleGen(input_base=examples)

    return [example_gen]


pipeline = AirflowDAGRunner(airflow_config).run(create_pipeline())
