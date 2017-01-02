import pika
import threading

def connect_to_rabbitmq(host):
    cp = pika.ConnectionParameters(host)
    return pika.BlockingConnection(cp)

class RabbitMQPutQueue(object):

    def __init__(self, host, exchange, routing_key):

        self._conn = connect_to_rabbitmq(host)
        self._chan = self._conn.channel()
        self._rkey = routing_key
        self._exchange = exchange

        self._chan.queue_declare(queue=self._rkey)

    def put(self, token):
        self._chan.basic_publish(exchange=self._exchange, \
                                 routing_key=self._rkey,  \
                                 body=token)

def rabbitmq_eventloop(callback_node, chan, rkey):
    def rabbitmq_callback(chan, method, properties, body):
        callback_node.run(body)

    chan.basic_consume(rabbitmq_callback, queue=rkey, no_ack=True)
    chan.start_consuming()
    print('Now stopped consuming')

class RabbitMQAcceptLoop(object):

    def __init__(self, host, routing_key, callback_node):

        self._conn = connect_to_rabbitmq(host)
        self._chan = self._conn.channel()
        self._rkey = routing_key

        self._chan.queue_declare(queue=self._rkey)

        t_args = (callback_node, self._chan, self._rkey)
        self._thread = threading.Thread(target=rabbitmq_eventloop, args=t_args)

    def start(self):
        self._thread.start()

    def request_stop(self):
        # doesn't work
        self._chan.stop_consuming()
        self._chan.close()
        self._thread.join()

if __name__ == '__main__':

    from epypes.pipeline import Node

    pn = Node('Printer', print)

    loop = RabbitMQAcceptLoop('localhost', 'hello', pn)
    loop.start()
