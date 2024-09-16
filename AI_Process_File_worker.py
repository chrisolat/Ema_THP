"""
Ai worker to consume and process tasks from kafka queue
"""

from confluent_kafka import Consumer
WORKER_NAME="AI_Process_File"
conf = {'bootstrap.servers': 'pkc-abcd85.us-west-2.aws.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': '<CLUSTER_API_KEY>',
        'sasl.password': '<CLUSTER_API_SECRET>',
        'group.id': 'foo',
        'auto.offset.reset': 'smallest'}

consumer = Consumer(conf)

running = True

def message_process(message):
    if message.topic != WORKER_NAME:
        return
    # process message
    # connect to db
    # update job status tp job started for data
    # wait 5 mins to mock ema/ai processing
    # update job status to completed
    # insert ai data result into db
    
    


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