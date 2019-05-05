from datetime import datetime

class Tag(object):
    TAG_API_URL = ""

    def __init__(self, **kwargs):
        self.__id = kwargs.get('id')
        self.__name = kwargs.get('name')
        self.__workspace_id = kwargs.get('workspace_id')
        self.__created, = datetime.strptime(kwargs.get('created'),
                                           '%Y-%m-%dT%H:%M:%S%z'),

        self.__workspace_ref = None

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id

    @property
    def workspace_id(self):
        return self.__workspace_id

    @property
    def created(self):
        return self.__created

    @property
    def workspace(self):
        return self.__workspace_ref

    @workspace.setter
    def workspace(self, workspace):
        self.__workspace_ref = workspace
