class GenericObject(object):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __repr__(self):
        class_name = self.__class__.__name__
        object_name = self.name
        return '{0}["{1}"]'.format(class_name, object_name)
