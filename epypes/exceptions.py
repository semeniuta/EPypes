class IncorrectArgKeyException(Exception):
    def __repr__(self):
        return 'Incorrect argument key provided to the node'

class TimeRequestBeforeRunException(Exception):
    def __repr__(self):
        return 'The node has not yet ran, but time requested'

class NodeCannotBeRunException(Exception):
    def __repr__(self):
        return 'The node is already running'
