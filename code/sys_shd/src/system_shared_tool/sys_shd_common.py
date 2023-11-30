#!/usr/bin/python3
'''
This module has the common classes in system shared.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
#######################         GENERIC IMPORTS          #######################
from threading import Thread, Event
from typing import Any, Iterable, Callable, Mapping
from enum import Enum
from time import time, sleep
#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_config_tool import sys_conf_read_config_params
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger

if __name__ == "__main__":
    cycler_logger = SysLogLoggerC()
log: Logger = sys_log_logger_get_module_logger(__name__)
#######################       THIRD PARTY IMPORTS        #######################
from RPi.GPIO import  setmode, BCM, BOARD, setup, output, HIGH, LOW, OUT #pylint: disable= no-name-in-module

#######################          MODULE IMPORTS          #######################

#######################          PROJECT IMPORTS         #######################

######################             CONSTANTS              ######################
from .context import DEFAULT_GPIO_CONFIG_PATH
gpio_mode = sys_conf_read_config_params(filename=DEFAULT_GPIO_CONFIG_PATH, section= 'GPIO_BOARD')
if gpio_mode == 'BOARD':
    setmode(BOARD)
else:
    setmode(BCM)
_TO_MS = 1000
#######################              ENUMS               #######################
class SysShdNodeStatusE(Enum):
    '''
    Enum class for the node state
    '''
    COMM_ERROR = -1
    OK = 0
    INTERNAL_ERROR = 1
    INIT = 2
    STOP = 3

#######################             CLASSES              #######################
class SysShdNodeParamsC:
    '''
    Class that contains the can parameters in order to create the thread correctly
    '''
    def __init__(self, target: Callable[..., object] | None = ...,
        args: Iterable[Any] = ...,
        kwargs: Mapping[str, Any] | None = ..., *, daemon: bool | None = ...):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.daemon = daemon

class SysShdNodeC(Thread):
    '''
    Classmethod for creating a system shdNode class .

    Args:
        Thread ([type]): [description]
    '''
    def __init__(self,name: str, cycle_period: int, working_flag : Event,
                 node_params: SysShdNodeParamsC = SysShdNodeParamsC()) -> None:
        '''
        Initialize the node.

        Args:
            cycle_period (int): [Period in ms]
            working_flag (Event): [description]
            node_params (SysShdNodeParamsC, optional): .Defaults to SysShdNodeParamsC().
        '''
        port: int = sys_conf_read_config_params(filename=DEFAULT_GPIO_CONFIG_PATH, section= name)
        self.gpio: SysShdPeripheralC = SysShdPeripheralC(port=port)
        super().__init__(group = None, target = node_params.target, name = name,
                         args = node_params.args, kwargs = node_params.kwargs,
                         daemon = node_params.daemon)
        self.working_flag: Event = working_flag
        self.cycle_period: int = cycle_period
        self.status: SysShdNodeStatusE = SysShdNodeStatusE.STOP

    def sync_shd_data(self) -> None:
        '''
        Function to be implemented in the inherited class
        '''
        raise NotImplementedError()

    def process_iteration(self) -> None:
        '''
        Function to be implemented in the inherited class
        '''
        raise NotImplementedError()

    def stop(self) -> None:
        '''
        Function to be implemented in the inherited class,
        it will execute when finishing the thread.
        '''
        raise NotImplementedError()

    def run(self) -> None:
        '''
        Main method executed by the Node thread, it is used as a base class to create a node, that
        execute the process iteration method in a loop.
        '''
        log.info("Start running process")
        self.status = SysShdNodeStatusE.INIT
        while self.working_flag.is_set():
            try:
                next_time = time()+self.cycle_period/_TO_MS
                self.gpio.set_gpio_up()
                self.process_iteration()
                self.gpio.set_gpio_down()
                # Sleep the remaining time
                sleep_time = next_time-int(time())
                # sleep_time is measure in miliseconds
                sleep_time: float = next_time-time()
                if sleep_time < 0.0:
                    log.critical((f"Real time error in {self.name}, "
                            f"cycle time exhausted: {abs(sleep_time)} seconds over period"))
                    sleep_time = 0.0
                # sleep function works in seconds, needed conversion from ms to s
                sleep(sleep_time)

            except Exception as err: #pylint: disable= broad-exception-caught
                log.error(f"Error  in node {err}")
                raise SysShdErrorC(err) from err
        # log.warning(f"Stop node {self.name}")
        self.stop()

class SysShdErrorC(Exception):
    '''
    Internal exception handler.

    Args:
        Exception ([type]): [description]
    '''
    def __init__(self, message) -> None:
        '''
        Exception raised for errors when a queue is full and data has tried to be put in it.

        Args:
            message (str): explanation of the error
        '''
        super().__init__(message)

class SysShdPeripheralC:
    '''
    Class that contains the common methods to toggle gpios.
    '''
    def __init__(self, port: int) -> None:
        self.port: int = port
        setup(port, OUT)
    def set_gpio_up(self) -> None:
        """
        Sets the GPIO pin to a high state.
        """
        log.debug(f"Setting GPIO {self.port} up")
        output(self.port, HIGH)

    def set_gpio_down(self) -> None:
        """
        Sets the GPIO pin to a low state.
        """
        log.debug(f"Setting GPIO {self.port} down")
        output(self.port, LOW)
