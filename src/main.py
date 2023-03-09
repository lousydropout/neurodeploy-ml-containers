from typing import Any
import os
import shutil
import json
import numpy as np
import tensorflow as tf
import boto3

BASE_IMAGE = os.environ["base_image"]
BUCKET_NAME = os.environ["bucket"]
REGION_NAME = os.environ["region_name"]
TMP = "/tmp"
FILEPATH = "/tmp/tmp.h5"

s3_client = boto3.client("s3")
s3 = boto3.resource("s3")
bucket = s3.Bucket(BUCKET_NAME)


def get_model(model_location: str) -> str:
    model_obj = bucket.Object(model_location)
    try:
        model_file = model_obj.get()["Body"].read()
    except s3_client.exceptions.NoSuchKey as err:
        print(err)

    with open(FILEPATH, "bw") as f:
        f.write(model_file)

    try:
        model = tf.keras.models.load_model(filepath=FILEPATH)
    except Exception as err:
        print(err)
        os.remove(FILEPATH)
        raise Exception("Failed to load model")

    return model


def tensorflow_h5_handler(model_location: str, payload: Any) -> Any:
    x_input = np.array(payload)
    print("x_input: ", x_input)

    # Get model
    model = get_model(model_location=model_location)
    print("Model summary: ", model.summary())

    # Run model
    try:
        res = model.predict(x_input)
        print("Res: ", res)
        output = res.tolist()
    except ValueError as err:
        print(err)
        return {"success": False, "error": str(err), "input": payload}
    except Exception as err:
        print(err)
        return {"success": False, "error": str(err)}
    finally:
        # remove model
        os.remove(FILEPATH)
        # remove __pycache
        try:
            shutil.rmtree(f"{TMP}/__pycache__")
        except:
            pass
        # remove all other files
        for f in os.listdir(TMP):
            try:
                os.remove(f)
            except:
                pass

    return output


def handler(event, context) -> dict:
    print("Image hash: ", BASE_IMAGE)
    print("Event: ", json.dumps(event, default=str))
    print("listdir: ", os.listdir(TMP))
    print(tf.__version__)

    # Get input/payload
    payload = event["payload"]
    model_location = event["model"]
    model_type = event["model_type"]
    persistence_type = event["persistence_type"]

    if model_type == "tensorflow" and persistence_type == "h5":
        output = tensorflow_h5_handler(model_location=model_location, payload=payload)
    elif model_type == "sckit-learn" and persistence_type == "pickle":
        pass

    # Format result
    result = {"success": True, "output": output, "image_hash": BASE_IMAGE}

    print("listdir: ", os.listdir(TMP))
    print("Result: ", json.dumps(result))
    return result
