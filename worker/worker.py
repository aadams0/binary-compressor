import pika
import zlib


def compress_file(file_path, task_id):
    # Open the file and compress its contents
    with open(file_path, 'rb') as f:
        file_contents = f.read()
    compressed_contents = zlib.compress(file_contents)
    # Save the compressed file to a new location
    with open(f'/tmp/{task_id}', 'wb') as f:
        f.write(compressed_contents)


def callback(ch, method, properties, body):
    file_path = body.decode()
    # Compress the file and update the task status
    compress_file(file_path, properties.correlation_id)
    # Publish data to general response channel
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=properties.correlation_id),
                     body='/tmp/data.bin')
    # Acknowledge consumption of message
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Initialize connection to RabbitMQ and initialize the task queue
def run_worker():
    credentials = pika.PlainCredentials('admin', 'mypass')
    parameters = pika.ConnectionParameters('rabbit', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue',
                          on_message_callback=callback)
    # print('Waiting for tasks...')
    channel.start_consuming()


run_worker()
