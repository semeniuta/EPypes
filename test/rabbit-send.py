# import pika
#
# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()
#
# channel.queue_declare(queue='hello')
#
# channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')

from epypes.patterns.rabbit import RabbitMQPutQueue

q = RabbitMQPutQueue(host='localhost', exchange='', routing_key='hello')


for i in range(100):
    q.put('Message #{}'.format(i))
