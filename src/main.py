import os
import json
import numpy as np
import tensorflow as tf
import boto3


s3 = boto3.resource("s3")
BUCKET_NAME = os.environ["bucket"]
bucket = s3.Bucket(BUCKET_NAME)


def get_model(model_location: str) -> str:
    model_obj = bucket.Object(model_location)
    model = model_obj.get()["Body"].read().decode()
    model = tf.keras.models.load_model(filepath=model)

    return model


def handler(event, context):
    print("Event: ", json.dumps(event, default=str))
    print(tf.__version__)

    model = get_model(model_location=event["model"])
    payload = event["payload"]

    x_input = np.array([payload])
    res = model.predict(x_input).tolist()
    # Transform predictions to JSON
    result = {"output": res}
    return result
