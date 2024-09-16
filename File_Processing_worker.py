"""
File processing worker to consume and process tasks from kafka queue
"""

from confluent_kafka import Consumer
from transformer import initiate_transformation
WORKER_NAME="File_Processing"
conf = {'bootstrap.servers': 'pkc-abcd85.us-west-2.aws.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': '<CLUSTER_API_KEY>',
        'sasl.password': '<CLUSTER_API_SECRET>',
        'group.id': 'foo',
        'auto.offset.reset': 'smallest'}

consumer = Consumer(conf)

running = True

# Processes message and pushes updates to db and new task to ai worker queue.
def message_process(message):
    if message.topic != WORKER_NAME:
        return
    # process file
    response, status = initiate_transformation(message["file_id"])
    if status != 202:
        return response
    # connect to db
    # update job status to job started for file_id
    # update job status to completed
    # insert transformed data into ai db
    # produce to topic "AI_Process_File worker queue"
    produce_confluent_message("AI_Process_File", "file_id", file_id)


# Consume loop
def basic_consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                message_process(msg)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False