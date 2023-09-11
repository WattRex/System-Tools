#!/usr/bin/python3
"""
This file test sys shd node.
"""

#######################        MANDATORY IMPORTS         #######################
import os
import sys
#######################         GENERIC IMPORTS          #######################
from threading import Event
from signal import signal, SIGINT
from time import sleep
from pytest import fixture, mark

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger

main_logger = SysLogLoggerC(file_log_levels="code/sys_shd/tests/log_config.yaml")
log: Logger = sys_log_logger_get_module_logger(name="test_shd_node")

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/')
from sys_shd.src.system_shared_tool import SysShdNodeC, SysShdNodeParamsC
#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################
class DummyNode(SysShdNodeC):
    """A dummy class .
    """
    def __init__(self,name: int, cycle_period: int, working_flag : Event,
                 meas_params: SysShdNodeParamsC= SysShdNodeParamsC()) -> None:
        '''
        Initialize the thread node used to update measurements from devices.
        '''
        super().__init__(name, cycle_period, working_flag, meas_params)
        self.working_flag = working_flag
        self.value = 0

    def process_iteration(self) -> None:
        """Update the value of the loop iteration .
        """
        self.value += 1
        log.info(msg=f"DummyNode value: {self.value}")

class TestChannels:
    """A test that tests the channels in pytest.
    """
    MAX_PERIOD = 120


    def signal_handler(self, sig, frame) -> None: #pylint: disable= unused-argument
        """Called when the user presses Ctrl + C to stop test.

        Args:
            sig ([type]): [description]
            frame ([type]): [description]
        """
        log.critical(msg='You pressed Ctrl+C! Stopping test...')

    @fixture(scope="function", autouse=False)
    def set_environ(self, request):
        """Setup the environment variables and start the process .

        Args:
            request ([type]): [description]

        Yields:
            [type]: [description]
        """
        log.info(msg=f"Setting up the environment Node test period {request.param[0]}ms")
        __working_node = Event()
        node = DummyNode(name= 'dummyNode', cycle_period=request.param[0],
                         working_flag= __working_node)
        __working_node.set()
        node.start()
        while node.value < 10:
            sleep(0.5)
        __working_node.clear()
        node.join()

    @fixture(scope="function")
    def config(self) -> None:
        """Configure the signal handler to signal when the SIGINT is received .
        """
        signal(SIGINT, self.signal_handler)


    #Test container
    @mark.parametrize("set_environ", [[750],
                                      [500]],\
                indirect=["set_environ"])
    def test_normal_op(self, set_environ, config) -> None: #pylint: disable= unused-argument
        """Test the machine status .

        Args:
            set_environ ([type]): [description]
            config ([type]): [description]
        """
        log.debug(msg="1. Test SALG machine status: check machine status normal operation")

#######################            FUNCTIONS             #######################
