import json
import tensorflow as tf


def handler(event: dict, context):
    print("Event: ", json.dumps(event, default=str))
    print(tf.reduce_sum(tf.random.normal([1000, 1000])))
    print("Tensorflow version: ", tf.__version__)
    return
