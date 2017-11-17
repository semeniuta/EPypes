import pika
import threading
import uuid

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
        self._chan.basic_publish(exchange=self._exchange,
                                 routing_key=self._rkey,
                                 body=token)

def rabbitmq_eventloop_func(callback_node, chan, rkey, consumer_tag):
    def rabbitmq_callback(chan, method, properties, body):
        callback_node.run(body)

    chan.basic_consume(rabbitmq_callback, queue=rkey, no_ack=True, consumer_tag=consumer_tag)
    chan.start_consuming()
    print('Now stopped consuming')

class RabbitMQEventLoop(object):

    def __init__(self, host, routing_key, callback_node):

        self._conn = connect_to_rabbitmq(host)
        self._chan = self._conn.channel()
        self._rkey = routing_key
        self._consumer_tag = uuid.uuid1().hex

        self._chan.queue_declare(queue=self._rkey)

        t_args = (callback_node, self._chan, self._rkey, self._consumer_tag)
        self._thread = threading.Thread(target=rabbitmq_eventloop_func, args=t_args)

    def start(self):
        self._thread.start()

    def stop(self):
        # https://gist.github.com/swinton/5438483
        self._chan.basic_cancel(self._consumer_tag)
        print('Cancel OK')
        self._chan.close()
        print('Channel closed')
        self._chan.stop_consuming() # <-not sure if needed
        print('Stopped consuming')
        self._thread.join() # <- doesn't join
        print('Thread joined')

if __name__ == '__main__':

    from epypes.node import Node

    pn = Node('Printer', print)

    loop = RabbitMQEventLoop('localhost', 'hello', pn)
    loop.start()
