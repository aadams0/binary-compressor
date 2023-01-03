from flask import Flask, render_template, request, send_file
import pika
import uuid
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        task_id = str(uuid.uuid4())
        # Save the uploaded file to a temporary location
        file = request.files['file']
        file_name = file.filename
        file_path = f'/tmp/x{task_id}'
        file.save(file_path)
        # Add a task to the task queue to compress the file
        credentials = pika.PlainCredentials('admin', 'mypass')
        parameters = pika.ConnectionParameters('rabbit', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_publish(exchange='',
                              routing_key='task_queue',
                              body=file_path,
                              properties=pika.BasicProperties(
                                  correlation_id=task_id,
                                  delivery_mode=2,
                                  reply_to='response_queue'
                              ))
        # Callback for handling RabbitMQ response queue
        def callback(ch, method, properties, body):
            print(task_id, properties.correlation_id)
            if properties.correlation_id == task_id:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                ch.connection.close()
        # Initialize the response queue after the post request is sent 
        # Awaits the message with appropriate correlation uuid
        channel.queue_declare(queue='response_queue', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='response_queue',
                              on_message_callback=callback)
        channel.start_consuming()
        # When the response is acknowledged, determine the necessary stats
        original_size = round(
            (os.path.getsize(f'/tmp/x{task_id}')) * 10**-6, 5)
        compressed_size = round(
            (os.path.getsize(f'/tmp/{task_id}')) * 10**-6, 5)
        compression_ratio = round(original_size / compressed_size, 5)
        # Render information about the compressed file
        return render_template('upload.html',
                               original_size=original_size,
                               compressed_size=compressed_size,
                               compression_ratio=compression_ratio,
                               task_id=task_id,
                               file_name=file_name)
    else:
        # Splash page
        return render_template('upload.html')


@app.route('/api/download/<task_id>/<file_name>')
def download_file(task_id, file_name):
    # Pull appropriate file based on task_id send to client
    return send_file(f'/tmp/{task_id}', download_name=f'{file_name}.zlib', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
