import os
from enum import Enum

PipelineStep = Enum("PipelineStep", "DATA_VALIDATION PREPROCESSING MODELING DEPLOY")


def create_pipeline_file(step, project, train_steps=1000, eval_steps=500, columns_for_slicing=None):
    
    base_file = """
import os
import logging
import datetime

from tfx.orchestration.airflow.airflow_runner import AirflowDAGRunner
from tfx.orchestration.pipeline import PipelineDecorator
from tfx.utils.dsl_utils import csv_input
from tfx.proto import trainer_pb2, evaluator_pb2, pusher_pb2

from tfx.components.example_gen.csv_example_gen.component import CsvExampleGen
from tfx.components.statistics_gen.component import StatisticsGen
from tfx.components.schema_gen.component import SchemaGen
from tfx.components.example_validator.component import ExampleValidator
from tfx.components.transform.component import Transform
from tfx.components.trainer.component import Trainer
from tfx.components.evaluator.component import Evaluator
from tfx.components.model_validator.component import ModelValidator
from tfx.components.pusher.component import Pusher


data_dir = os.path.join(os.environ['DATA_DIR'], '{project}')
log_dir = os.path.join(os.environ['TFX_DIR'], 'logs')
serving_model_dir = os.path.join(os.environ['SERVING_DIR'], 'serving_model', '{project}')
project_preprocessing_file = os.path.join(os.environ['DAGS_DIR'], '{project}_preprocessing.py')
project_training_file = os.path.join(os.environ['DAGS_DIR'], '{project}_modeling.py')

logger_overrides = dict([
    ('log_root', log_dir),
    ('log_level', logging.INFO)
])

airflow_config = dict([
    ('schedule_interval', None),
    ('start_date', datetime.datetime(2019, 1, 1))
])

@PipelineDecorator(
    pipeline_name='{project}',
    enable_cache=True,
    metadata_db_root=os.environ['METADATA_DB_DIR'],
    additional_pipeline_args=dict([('logger_args', logger_overrides)]),
    pipeline_root=os.environ['PIPELINE_DIR']
)
def create_pipeline():
    
    pipeline = []
    
    {components}
    
    return pipeline

pipeline = AirflowDAGRunner(airflow_config).run(create_pipeline())
"""
    
    pipeline_file = None

    if step == PipelineStep.DATA_VALIDATION:
    
        pipeline_file = base_file.format(
            project=project,
            components="""     
    examples = csv_input(data_dir)

    # Brings data into the pipeline
    example_gen = CsvExampleGen(input_base=examples)
    pipeline.append(example_gen)
    
    # Computes statistics over data for visualization and example validation.
    statistics_gen = StatisticsGen(input_data=example_gen.outputs.examples)
    pipeline.append(statistics_gen)

    # Generates schema based on statistics files.
    infer_schema = SchemaGen(stats=statistics_gen.outputs.output)
    pipeline.append(infer_schema)

    # Performs anomaly detection based on statistics and data schema.
    validate_stats = ExampleValidator(
        stats=statistics_gen.outputs.output,
        schema=infer_schema.outputs.output
    )
    pipeline.append(validate_stats)
    """
        )

    elif step == PipelineStep.PREPROCESSING:
    
        pipeline_file = base_file.format(
            project=project,
            components="""     
    examples = csv_input(data_dir)

    # Brings data into the pipeline
    example_gen = CsvExampleGen(input_base=examples)
    pipeline.append(example_gen)
    
    # Computes statistics over data for visualization and example validation.
    statistics_gen = StatisticsGen(input_data=example_gen.outputs.examples)
    pipeline.append(statistics_gen)

    # Generates schema based on statistics files.
    infer_schema = SchemaGen(stats=statistics_gen.outputs.output)
    pipeline.append(infer_schema)

    # Performs anomaly detection based on statistics and data schema.
    validate_stats = ExampleValidator(
        stats=statistics_gen.outputs.output,
        schema=infer_schema.outputs.output
    )
    pipeline.append(validate_stats)

    # Performs transformations and feature engineering in training and serving.
    transform = Transform(
        input_data=example_gen.outputs.examples,
        schema=infer_schema.outputs.output,
        module_file=project_preprocessing_file
    )
    pipeline.append(transform)
    """
        )

    elif step == PipelineStep.MODELING:
    
        pipeline_file = base_file.format(
            project=project,
            components="""     
    examples = csv_input(data_dir)

    # Brings data into the pipeline
    example_gen = CsvExampleGen(input_base=examples)
    pipeline.append(example_gen)
    
    # Computes statistics over data for visualization and example validation.
    statistics_gen = StatisticsGen(input_data=example_gen.outputs.examples)
    pipeline.append(statistics_gen)

    # Generates schema based on statistics files.
    infer_schema = SchemaGen(stats=statistics_gen.outputs.output)
    pipeline.append(infer_schema)

    # Performs anomaly detection based on statistics and data schema.
    validate_stats = ExampleValidator(
        stats=statistics_gen.outputs.output,
        schema=infer_schema.outputs.output
    )
    pipeline.append(validate_stats)

    # Performs transformations and feature engineering in training and serving.
    transform = Transform(
        input_data=example_gen.outputs.examples,
        schema=infer_schema.outputs.output,
        module_file=project_preprocessing_file
    )
    pipeline.append(transform)

    # Uses user-provided Python function that implements a model.
    trainer = Trainer(
        module_file=project_training_file,
        transformed_examples=transform.outputs.transformed_examples,
        schema=infer_schema.outputs.output,
        transform_output=transform.outputs.transform_output,
        train_args=trainer_pb2.TrainArgs(num_steps={train_steps}),
        eval_args=trainer_pb2.EvalArgs(num_steps={eval_steps})
    )
    pipeline.append(trainer)

    # Uses TFMA to compute a evaluation statistics over features of a model.
    model_analyzer = Evaluator(
        examples=example_gen.outputs.examples,
        model_exports=trainer.outputs.output,
        feature_slicing_spec=evaluator_pb2.FeatureSlicingSpec(specs=[{specs}])
    )
    pipeline.append(model_analyzer)
    """.format(
            train_steps=train_steps,
            eval_steps=eval_steps,
            specs=",".join(["evaluator_pb2.SingleSlicingSpec(column_for_slicing=['%s'])" % col for col in columns_for_slicing])
        ))

    elif step == PipelineStep.DEPLOY:
    
        pipeline_file = base_file.format(
            project=project,
            components="""     
    examples = csv_input(data_dir)

    # Brings data into the pipeline
    example_gen = CsvExampleGen(input_base=examples)
    pipeline.append(example_gen)
    
    # Computes statistics over data for visualization and example validation.
    statistics_gen = StatisticsGen(input_data=example_gen.outputs.examples)
    pipeline.append(statistics_gen)

    # Generates schema based on statistics files.
    infer_schema = SchemaGen(stats=statistics_gen.outputs.output)
    pipeline.append(infer_schema)

    # Performs anomaly detection based on statistics and data schema.
    validate_stats = ExampleValidator(
        stats=statistics_gen.outputs.output,
        schema=infer_schema.outputs.output
    )
    pipeline.append(validate_stats)

    # Performs transformations and feature engineering in training and serving.
    transform = Transform(
        input_data=example_gen.outputs.examples,
        schema=infer_schema.outputs.output,
        module_file=project_preprocessing_file
    )
    pipeline.append(transform)

    # Uses user-provided Python function that implements a model.
    trainer = Trainer(
        module_file=project_training_file,
        transformed_examples=transform.outputs.transformed_examples,
        schema=infer_schema.outputs.output,
        transform_output=transform.outputs.transform_output,
        train_args=trainer_pb2.TrainArgs(num_steps={train_steps}),
        eval_args=trainer_pb2.EvalArgs(num_steps={eval_steps})
    )
    pipeline.append(trainer)

    # Uses TFMA to compute a evaluation statistics over features of a model.
    model_analyzer = Evaluator(
        examples=example_gen.outputs.examples,
        model_exports=trainer.outputs.output,
        feature_slicing_spec=evaluator_pb2.FeatureSlicingSpec(specs=[{specs}])
    )
    pipeline.append(model_analyzer)

    # Performs quality validation of a candidate model (compared to a baseline).
    model_validator = ModelValidator(
        examples=example_gen.outputs.examples, model=trainer.outputs.output
    )
    pipeline.append(model_validator)

    # Checks whether the model passed the validation steps and pushes the model to a file destination if check passed.
    pusher = Pusher(
        model_export=trainer.outputs.output,
        model_blessing=model_validator.outputs.blessing,
        push_destination=pusher_pb2.PushDestination(
            filesystem=pusher_pb2.PushDestination.Filesystem(base_directory=serving_model_dir)
        )
    )
    pipeline.append(pusher)

    """.format(
            train_steps=train_steps,
            eval_steps=eval_steps,
            specs=",".join(["evaluator_pb2.SingleSlicingSpec(column_for_slicing=['%s'])" % col for col in columns_for_slicing])
        ))

        
        
    return pipeline_file

    

def write_pipeline_to_dags(pipeline_file, name):
    with open(os.path.join(os.environ['DAGS_DIR'], name + ".py"), "w") as f:
        f.write(pipeline_file)
    


