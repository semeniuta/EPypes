# import pika
#
# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()
#
# channel.queue_declare(queue='hello')
#
# channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')

from epypes.rabbit import RabbitMQPutQueue

q = RabbitMQPutQueue(host='localhost', exchange='', routing_key='hello')
q.put('My name is Alex')
