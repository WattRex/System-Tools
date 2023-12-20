#!/usr/bin/python3
"""
This module will manage the shared objects.
It will lock the shared object in order to change it savely,
for each channel.
"""

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
#######################         GENERIC IMPORTS          #######################
from queue import Queue, Empty, Full
from pickle import dumps, loads, HIGHEST_PROTOCOL


#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger

if __name__ == "__main__":
    cycler_logger = SysLogLoggerC()
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################
import posix_ipc as ipc

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################
from .sys_shd_common import SysShdErrorC

#######################              ENUMS               #######################

######################             CONSTANTS              ######################
from .context import DEFAULT_CHAN_NUM_MSG, DEFAULT_IPC_MSG_SIZE, DEFAULT_CHAN_TIMEOUT

#######################             CLASSES              #######################


class SysShdChanC(Queue):
    """A subclass of the SHDChannel class .

    Args:
        Queue ([type]): [description]
    """

    def __init__(self, maxsize: int = DEFAULT_CHAN_NUM_MSG) -> None:
        '''
        Initialize the python Queue subclass used to intercommunicate threads.

        Args:
            maxsize (int, optional): Queue max size. Defaults to 100
        '''
        super().__init__(maxsize = maxsize)

    def delete_until_last(self) -> None:
        '''
        Delete all items from the queue, except the last one.
        '''
        while self.qsize() > 1:
            self.get()

    def receive_data(self) -> object:
        '''
        Pop the first element from the queue and return it. If queue is empty,
        wait until a new element is pushed to the queue.

        Returns:
            object: The first element of the queue.
        '''
        return self.get()

    def receive_data_unblocking(self) -> object:
        '''
        Receive data from the queue in unblocking mode.

        Returns:
            object: Return the first element from the queue if it is not empty.
            Return None otherwise.
        '''
        data = None
        if not self.is_empty():
            try:
                data = self.get_nowait()
            except Empty:
                log.warning("Error receiving data from channel")
        return data

    def send_data(self, data) -> None:
        '''
        Push data to the queue .

        Args:
            data (object): Data to be pushed to the queue.

        Raises:
            SysShdErrorC: Throw an exception if the queue is full.
        '''
        try:
            self.put_nowait(data)
        except Full as err:
            log.error(err)
            raise SysShdErrorC(message=f"Data can't be put in queue because it's full\
                                    with error {err}") from err

    def is_empty(self) -> bool:
        '''
        Check if the queue is empty.

        Returns:
            bool: True if the queue is empty, False otherwise.
        '''
        return self.empty()

class SysShdIpcChanC(ipc.MessageQueue): #pylint: disable= c-extension-no-member
    """A subclass of the SHDChannel class  using posix-ipc.
    Which will use system queues

    Args:
        Queue ([type]): [description]
    """
    def __init__(self, name: str= "ipc_queue", max_msg: int = DEFAULT_CHAN_NUM_MSG,\
                max_message_size = DEFAULT_IPC_MSG_SIZE) -> None:
        '''
        Initialize the python Queue subclass used to intercommunicate threads.

        Args:
            maxsize (int, optional): Queue max size. Defaults to 100
        '''
        log.debug(f"Creating IPC queue with name {name}")
        # Flag O_CREAT-> Open or create a MessageQueue object
        # O_CREAT | O_EXCL (or O_CREX) -> the module creates a new object identified by name.
        # If an object with that name already exists, the call raises an ExistentialError
        q_name: str = '/'+ name
        super().__init__(name=q_name, flags=ipc.O_CREAT, #pylint: disable= c-extension-no-member
                         max_messages = max_msg, max_message_size=max_message_size)
        self.block = True

    def delete_until_last(self) -> None:
        '''
        Delete all items from the queue, except the last one.
        '''
        while self.current_messages > 0:
            self.receive(timeout = 0)

    def receive_data(self, timeout: int|None = DEFAULT_CHAN_TIMEOUT) -> object:
        '''
        Pop the first element from the queue and return it. If queue is empty,
        wait until a new element is pushed to the queue.

        Returns:
            object: The first element of the queue.
        '''
        msg_decoded = None
        self.block = True
        try:
            message, _ = self.receive(timeout = timeout)
            log.debug(f"Receive data: {len(message)} - {type(message)} - {message}")
            msg_decoded = loads(message, encoding='utf-8')
        except Exception as err:
            log.error(f"Impossible to receive message with error: {err}")
            raise err
        self.block = False
        return msg_decoded

    def receive_data_unblocking(self) -> object:
        '''
        Receive data from the queue in unblocking mode.
        Returns:
            object: Return the first element from the queue if it is not empty.
            Return None otherwise.
        '''
        msg_decoded = None
        if not self.is_empty():
            self.block = False
            try:
                message, _ = self.receive()
                log.debug(f"Send data: {len(message)} - {type(message)} - {message}")
                msg_decoded = loads(message, encoding='utf-8')
            except Exception as err:
                log.error(f"Impossible to receive message with error {err}")
                raise err
            self.block = True
        return msg_decoded


    def send_data(self, data) -> None:
        '''
        Push data to the queue .

        Args:
            data (object): Data to be pushed to the queue.

        Raises:
            SysShdErrorC: Throw an exception if the queue is full.
        '''
        try:
            encoded_data: bytes = dumps(obj=data, protocol=HIGHEST_PROTOCOL)
            log.debug(f"Send data: {len(encoded_data)} - {type(encoded_data)} - {encoded_data}")
            self.send(encoded_data)
        except Full as err:
            log.error(err)
            raise SysShdErrorC(message=("Data can't be put in queue because it's full "
                                    f" with error {err}")) from err

    def is_empty(self) -> bool:
        '''
        Check if the queue is empty.

        Returns:
            bool: True if the queue is empty, False otherwise.
        '''
        return self.current_messages == 0

    def terminate(self) -> None:
        """Terminate the queue.
        """
        try:
            self.close()
            self.unlink()
        except ipc.ExistentialError as err: #pylint: disable= c-extension-no-member
            log.error(f"Trying to close/unlink queue {self.name} with error {err}")
