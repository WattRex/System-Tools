#!/usr/bin/python3
"""
This module has the common classes in system shared.
"""

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
#######################         GENERIC IMPORTS          #######################
from threading import Thread, Event
from typing import Any, Iterable, Callable, Mapping
from time import time, sleep
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

class SysShdNodeParamsC:
    """
    Class that contains the can parameters in order to create the thread correctly
    """
    def __init__(self, target: Callable[..., object] | None = ...,
        args: Iterable[Any] = ...,
        kwargs: Mapping[str, Any] | None = ..., *, daemon: bool | None = ...):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.daemon = daemon

class SysShdNodeC(Thread):
    """Classmethod for creating a system shdNode class .

    Args:
        Thread ([type]): [description]
    """
    def __init__(self,name: str, cycle_period: int, working_flag : Event,
                 node_params: SysShdNodeParamsC = SysShdNodeParamsC()) -> None:
        """Initialize the node .

        Args:
            cycle_period (int): [Period in ms]
            working_flag (Event): [description]
            node_params (SysShdNodeParamsC, optional): .Defaults to SysShdNodeParamsC().
        """
        super().__init__(group = None, target = node_params.target, name = name,
                         args = node_params.args, kwargs = node_params.kwargs,
                         daemon = node_params.daemon)
        self.working_flag: Event = working_flag
        self.cycle_period: float = cycle_period

    def sync_shd_data(self) -> None:
        """Function to be implemented in the inherited class
        """
        raise NotImplementedError()

    def process_iteration(self) -> None:
        """Function to be implemented in the inherited class
        """
        raise NotImplementedError()

    def stop(self) -> None:
        """
        Function to be implemented in the inherited class,
        it will execute when finishing the thread.
        """
        raise NotImplementedError()

    def run(self) -> None:
        '''
        Main method executed by the CAN thread. It receive data from EPCs and PLAKs
        and store it on the corresponding chan.
        '''
        log.info("Start running process")
        while self.working_flag.isSet():
            try:
                next_time = time()+self.cycle_period
                self.process_iteration()
                # 5.0 Sleep the remaining time
                sleep_time = next_time-int(time())
                if sleep_time < 100:
                    log.critical(f"Real time error, cycle time exhausted: {sleep_time}")
                else:
                    sleep(sleep_time/1000)

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
