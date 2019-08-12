##
# ZMQ-based application apis
# @author Patrick Kage

import zmq
import functools
import sys


# something happened on the remote
class RemoteError(Exception):
    pass

# client class to proxy a remote object
class Client:
    remote = ""
    listing = []
    timeout = None
    __socket = None
    __context = None
    __should_destroy_context = False

    # set up the object
    def __init__(self, remote, context=None, timeout=None):
        """
        Initialize the client object, connecting immediately.

        :param remote: remote bind URI
        :param context: pyzmq.Context to use (optional, one will be created otherwise)
        :param timeout: timeout (int milliseconds)
        """
        self.remote = remote
        self.timeout = timeout

        # if we don't have a zmq context, create a new one
        if context is None:
            self.__context = zmq.Context()
            self.__should_destroy_context = True
        else:
            self.__should_destroy_context = False
            self.__context = context

        # create a socket
        self.__socket = self.__context.socket(zmq.REQ)
        if timeout is not None:
            self.__socket.setsockopt(zmq.LINGER, timeout)
        self.__socket.connect(remote)

        # connect to the remote
        self.__refresh_remote()

    def __del__(self):
        # clean up the context so we don't fill the rest of the context
        if self.__should_destroy_context:
            self.__context.destroy()
        self.__socket.close()

    # make a remote function call
    def __call(self, func, *args, **kwargs):
        # construct the function call
        payload = {'func': func}
        if args is not None:
            payload['args'] = args
        if kwargs is not None:
            payload['kwargs'] = kwargs

        # send off
        self.__socket.send_pyobj(payload)

        msg = {}
        if self.timeout is None:
            # wait back from the server
            msg = self.__socket.recv_pyobj()
        else:
            poller = zmq.Poller()
            poller.register(self.__socket, zmq.POLLIN)
            if poller.poll(self.timeout):
                msg = self.__socket.recv_pyobj()
            else:
                raise IOError('Connection to wirepickle server dropped')

        if msg['success']:
            if 'stdout' in msg:
                sys.stdout.write(msg['stdout'])
                sys.stdout.flush()
            return msg['return']
        else:
            raise RemoteError(msg['error'])

    # get the remote listing
    def __refresh_remote(self):
        self.listing = self.__call('#listing')

    # wait for the remote to come online
    def __ping(self):
        return self.__call('#ping')

    def _shutdown(self):
        return self.__call('#shutdown')

    # make this more easily debuggable
    def __repr__(self):
        return '<wirepickle client object @ {}>'.format(self.remote)

    def __getattr__(self, name):
        for fn in self.listing:
            if fn['name'] == name:
                return functools.partial(self.__call, name)
        raise AttributeError(name)
