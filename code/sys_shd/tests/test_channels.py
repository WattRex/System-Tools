#!/usr/bin/python3
"""
This file test sys shd channels.
"""

#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################
from signal import signal, SIGINT
from time import sleep
from pytest import fixture, mark
from threading import Thread, Event
from typing import Generator, Any, Tuple

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger

main_logger = SysLogLoggerC(file_log_levels="code/log_config.yaml")
log: Logger = sys_log_logger_get_module_logger(name="test_shd")

#######################       THIRD PARTY IMPORTS        #######################
import posix_ipc as ipc
#######################          MODULE IMPORTS          #######################

#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################
class Dummy:

    def __init__(self, value: int):
        self.value: int = value

    def __str__(self) -> str:
        return str(self.value)

#######################            FUNCTIONS             #######################

class My_Thread(Thread):

    def __init__(self, ) -> None:
        super().__init__()


    def check_1(self, __a: Dummy, __b: Dummy, __c: Dummy) -> None:
        log.debug(f"Test for thread 1: {__a}, {__b}, {__c}")

    def check_2(self, __a: Dummy, __b: Dummy, __c: Dummy) -> None:
        log.debug(f"Test for thread 2: {__a}, {__b}, {__c}")

class TestChannels:
    MAX_PERIOD = 120


    def signal_handler(self, sig, frame) -> None:
        log.critical(msg='You pressed Ctrl+C! Stopping test...')
        self.finish = True

    @fixture(scope="function", autouse=False)
    def set_environ(self, request):
        log.error(msg="Setup environment")

        # Parse params
        inst_a = Dummy(value=request.param[0])
        inst_b = Dummy(value=request.param[1])
        inst_c = Dummy(value=request.param[2])

        # Initialize threads
        self.th1 = My_Thread()
        self.th1.start()
        self.th1.check_1(inst_a, inst_b, inst_c)

        self.th2 = My_Thread()
        self.th2.start()
        self.th2.check_2(inst_a, inst_b, inst_c)
        yield self.th1, self.th2
        log.error("Cleaning environment")
        self.th1.join()
        self.th2.join()


    @fixture(scope="function")
    def config(self) -> None:
        signal(SIGINT, self.signal_handler)


    #Test container
    @mark.parametrize("set_environ", [[1, 100, 1000]], indirect=["set_environ"])
    def test_normal_op(self, set_environ, config) -> None:
        log.debug(msg=f"1. Test SALG machine statuts: check machine status normal operation")