#!/usr/bin/python3
"""
This module has the common classes in system shared.
"""

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
#######################         GENERIC IMPORTS          #######################
from threading import Thread, Event
from typing import Any, Iterable, Callable, Mapping
from time import time
#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger

if __name__ == "__main__":
    cycler_logger = SysLogLoggerC()
log: Logger = sys_log_logger_get_module_logger(__name__)
#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################

#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

class SysShdParamsC:
    """
    Class that contains the can parameters in order to create the thread correctly
    """
    def __init__(self, target: Callable[..., object] | None = ...,
        name: str | None = ..., args: Iterable[Any] = ...,
        kwargs: Mapping[str, Any] | None = ..., *, daemon: bool | None = ...):
        self.target = target
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.daemon = daemon

class SysShdNodeC(Thread):
    """Classmethod for creating a system shdNode class .

    Args:
        Thread ([type]): [description]
    """
    def __init__(self, cycle_period: float, working_flag : Event,
                 node_params: SysShdParamsC = SysShdParamsC()) -> None:
        '''
        Initialize the thread node.
        '''
        super().__init__(group = None, target = node_params.target, name = node_params.name,
                         args = node_params.args, kwargs = node_params.kwargs,
                         daemon = node_params.daemon)
        self.working_flag: Event = working_flag
        self.cycle_period: float = cycle_period

    def sync_shd_data(self) -> None:
        """Function to be implemented in the inherited class
        """

    def process_iteration(self) -> None:
        """Function to be implemented in the inherited class
        """

    def stop(self) -> None:
        """
        Stop the node thread .
        """
        log.critical("Stopping node thread.")
        self.join()
        self.working_flag.clear()

    def run(self) -> None:
        '''
        Main method executed by the CAN thread. It receive data from EPCs and PLAKs
        and store it on the corresponding chan.
        '''
        log.info("Start running process")
        while self.working_flag.isSet():
            try:
                tic = time()
                self.process_iteration()
                wait(tic, self.cycle_period)
            except Exception as err: #pylint: disable= broad-exception-caught
                log.error(f"Error  in node {err}")
                raise SysShdErrorC(err) from err
        log.critical("Stop node")
        self.stop()

class SysShdErrorC(Exception):
    """Internal exception handler.

    Args:
        Exception ([type]): [description]
    """
    def __init__(self, message) -> None:
        '''
        Exception raised for errors when a queue is full and data has tried to be put in it.

        Args:
            message (str): explanation of the error
        '''
        super().__init__(message)

#######################            FUNCTIONS             #######################
def wait(tic: float, sleep_time: float) -> None:
    """Wait until the sleep time is reached.

    Args:
        tic ([float]): [description]
        sleep_time ([float]): [Period in seconds]
    """
    while time()-tic <= sleep_time:
        pass
