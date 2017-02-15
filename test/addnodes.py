from epypes.pipeline import Pipeline
from epypes.node import Node

nodes1 = [Node('myname{}'.format(i), lambda x: x) for i in range(5)]
nodes2 = [Node('myname', lambda x: x) for i in range(5)]

pipe1 = Pipeline('P1', nodes1)

try:
    pipe2 = Pipeline('P2', nodes2)
except Exception as e:
    print('A pipeline was not created because of exception:', str(e))




