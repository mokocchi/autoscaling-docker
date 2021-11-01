class AppErrorBaseClass(Exception):
    pass


class ObjectNotFound(AppErrorBaseClass):
    pass

class DockerError(AppErrorBaseClass):
    pass