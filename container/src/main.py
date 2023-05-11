from typing import Tuple, Any
import os

# import shutil
import json
import numpy as np
import tensorflow as tf
import boto3

BASE_IMAGE = os.environ["base_image"]
BUCKET_NAME = os.environ["bucket"]
REGION_NAME = os.environ["region_name"]
TMP = "/tmp"
FILEPATH_h5 = "/tmp/tmp.h5"
FILEPATH_joblib = "/tmp/tmp.joblib"
FILEPATH_pickle = "/tmp/tmp.pickle"

H5 = "h5"
JOBLIB = "joblib"
PICKLE = "pickle"

SCIKIT_LEARN = "scikit-learn"
TENSORFLOW = "tensorflow"

s3_client = boto3.client("s3")
s3 = boto3.resource("s3")
bucket = s3.Bucket(BUCKET_NAME)


def get_model_h5(model_location: str) -> str:
    model_obj = bucket.Object(model_location)
    try:
        model_file = model_obj.get()["Body"].read()
    except s3_client.exceptions.NoSuchKey as err:
        print(err)

    with open(FILEPATH_h5, "bw") as f:
        f.write(model_file)

    try:
        model = tf.keras.models.load_model(filepath=FILEPATH_h5)
    except Exception as err:
        print(err)
        os.remove(FILEPATH_h5)
        raise Exception("Failed to load model")

    return model


def get_model_joblib(model_location: str) -> str:
    model_obj = bucket.Object(model_location)
    try:
        model_file = model_obj.get()["Body"].read()
    except s3_client.exceptions.NoSuchKey as err:
        print(err)

    with open(FILEPATH_joblib, "bw") as f:
        f.write(model_file)

    try:
        import joblib

        model = joblib.load(FILEPATH_joblib)
    except Exception as err:
        print(err)
        os.remove(FILEPATH_joblib)
        raise Exception("Failed to load model")

    return model


def get_model_pickle(model_location: str) -> str:
    model_obj = bucket.Object(model_location)
    try:
        model_file = model_obj.get()["Body"].read()
    except s3_client.exceptions.NoSuchKey as err:
        print(err)

    with open(FILEPATH_pickle, "bw") as f:
        f.write(model_file)

    try:
        import pickle

        model = pickle.loads(FILEPATH_pickle)
    except Exception as err:
        print(err)
        os.remove(FILEPATH_pickle)
        raise Exception("Failed to load model")

    return model


def tensorflow_handler(
    model_location: str, persistence_type: str, payload: Any
) -> Tuple[bool, Any]:
    x_input = np.array(payload)
    print("x_input: ", x_input)

    # Get model
    if persistence_type == H5:
        model = get_model_h5(model_location=model_location)
    elif persistence_type == JOBLIB:
        model = get_model_joblib(model_location=model_location)
    print("Model summary: ", model.summary())

    # Run model
    try:
        res = model.predict(x_input)
        print("Res: ", res)
        output = res.tolist()
    except ValueError as err:
        print(err)
        return False, str(err)
    except Exception as err:
        print(err)
        return False, str(err)
    # TODO Fix this
    # finally:
    #     os.remove(FILEPATH)
    #     shutil.rmtree(f"{TMP}/__")

    return True, output


def scikit_learn_handler(
    model_location: str, persistence_type: str, payload: Any
) -> Tuple[bool, Any]:
    x_input = np.array(payload)
    print("x_input: ", x_input)

    # Get model
    if persistence_type == H5:
        model = get_model_h5(model_location=model_location)
    elif persistence_type == JOBLIB:
        model = get_model_joblib(model_location=model_location)
    # print("Model summary: ", model.summary())

    # Run model
    try:
        res = model.predict(x_input)
        print("Res: ", res)
        output = res.tolist()
    except ValueError as err:
        print(err)
        return False, str(err)
    except Exception as err:
        print(err)
        return False, str(err)
    # finally:
    #     os.remove(FILEPATH)
    #     shutil.rmtree(f"{TMP}/__")

    return True, output


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

    if model_type == TENSORFLOW:
        success, output = tensorflow_handler(
            model_location=model_location,
            persistence_type=persistence_type,
            payload=payload,
        )
    elif model_type == SCIKIT_LEARN:
        success, output = scikit_learn_handler(
            model_location=model_location,
            persistence_type=persistence_type,
            payload=payload,
        )
    else:
        pass

    # Format result
    if success:
        result = {"success": True, "output": output, "image_hash": BASE_IMAGE}
    else:
        result = {"success": False, "error": output, "image_hash": BASE_IMAGE}

    print("listdir: ", os.listdir(TMP))
    print("Result: ", json.dumps(result))
    return result
