import os
import json
import numpy as np
import tensorflow as tf
import boto3

BASE_IMAGE = os.environ["base_image"]
BUCKET_NAME = os.environ["bucket"]
REGION_NAME = os.environ["region_name"]
FILEPATH = "/tmp/tmp.h5"

s3 = boto3.resource("s3")
bucket = s3.Bucket(BUCKET_NAME)


def get_model(model_location: str) -> str:
    model_obj = bucket.Object(model_location)
    model_file = model_obj.get()["Body"].read()
    with open(FILEPATH, "bw") as f:
        f.write(model_file)

    try:
        model = tf.keras.models.load_model(filepath=FILEPATH)
    except Exception as err:
        print(err)
        os.remove(FILEPATH)
        raise err

    return model


def handler(event, context) -> dict:
    print("Image hash: ", BASE_IMAGE)
    print("Event: ", json.dumps(event, default=str))
    print("listdir: ", os.listdir())
    print(tf.__version__)

    # Get input/payload
    payload = event["payload"]
    x_input = np.array([payload])
    print("x_input: ", x_input)

    # Get model
    model = get_model(model_location=event["model"])
    print("Model summary: ", model.summary())

    # Run model
    try:
        res = model.predict(x_input).tolist()
    except Exception as err:
        print(err)
        raise err
    finally:
        os.remove(FILEPATH)

    # Format result
    result = {"output": res, "image_hash": BASE_IMAGE}

    print("listdir: ", os.listdir())
    print("Result: ", json.dumps(result))
    return result
