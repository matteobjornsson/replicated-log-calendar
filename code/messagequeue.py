import pika

def send():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='',
                        routing_key='hello',
                        body='Hello World!')
    print(" [x] Sent 'Hello World!'")
    connection.close()

def receive():
    channel.queue_declare(queue='hello')
    channel.basic_consume(queue='hello',
                      auto_ack=True,
                      on_message_callback=callback)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)