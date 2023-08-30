#!/usr/bin/python3
"""
This file test sys shd channels.
"""

#######################        MANDATORY IMPORTS         #######################
import os
import sys
import random
from copy import deepcopy
#######################         GENERIC IMPORTS          #######################
from threading import Thread
from multiprocessing import Process
from signal import signal, SIGINT
from time import sleep
from pytest import fixture, mark

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger

main_logger = SysLogLoggerC(file_log_levels="code/sys_shd/tests/log_config.yaml")
log: Logger = sys_log_logger_get_module_logger(name="test_shd")

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/')
from sys_shd.src.system_shared_tool import SysShdIpcChanC, SysShdChanC
#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################
TH1_FAIL = True
TH2_FAIL = True
SIZE_QUEUE_P1 = 50
SIZE_QUEUE_P2 = 51
#######################             CLASSES              #######################
class Dummy:
    """A dummy class .
    """
    def __init__(self, value: int):
        self.value: int = value

    def __str__(self) -> str:
        return str(self.value)

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
        global TH1_FAIL #pylint: disable= global-statement
        global TH2_FAIL #pylint: disable= global-statement
        TH1_FAIL = True
        TH2_FAIL = True
        # Parse params
        inst_a = Dummy(value=request.param[0])
        inst_b = Dummy(value=request.param[1])
        inst_c = Dummy(value=request.param[2])
        test_type = request.param[3]
        log.info(msg=f"Setup environment for {test_type} test")
        if 'thread' in test_type:
            queue1 = SysShdChanC()
            queue2 = SysShdChanC()
            self.th1 = Thread(target = check_1, #pylint: disable= attribute-defined-outside-init
                          args = (inst_a, inst_b, inst_c, [queue1, queue2]))
            self.th2 = Thread(target = check_2, #pylint: disable= attribute-defined-outside-init
                          args = (inst_a, inst_b, inst_c, [queue1, queue2]))
        else:
            queue1 = SysShdIpcChanC(name= "test_ipc_int", max_msg=SIZE_QUEUE_P1)
            queue2 = SysShdIpcChanC(name= "test_ipc_obj", max_msg=SIZE_QUEUE_P2)
            self.th1 = Process(target = check_1, #pylint: disable= attribute-defined-outside-init
                          args = (inst_a, inst_b, inst_c, []))
            self.th2 = Process(target = check_2, #pylint: disable= attribute-defined-outside-init
                          args = (inst_a, inst_b, inst_c, []))
        queue1.delete_until_last()
        queue2.delete_until_last()


        # Initialize threads/process
        self.th1.start()
        self.th2.start()

        yield

        log.info(f"Cleaning environment for {test_type} test")
        self.th1.join()
        self.th2.join()
        if not 'thread' in test_type:
            TH1_FAIL=self.th1.exitcode
            TH2_FAIL = self.th2.exitcode
        log.info(f"{test_type} info, 1: {TH1_FAIL}, 2: {TH2_FAIL}")
        if TH1_FAIL or TH2_FAIL:
            raise AssertionError(f"The test for {test_type} failed 1: {TH1_FAIL} 2: {TH2_FAIL}")
        sleep(1)
        TH1_FAIL = True
        TH2_FAIL = True
        queue1.delete_until_last()
        queue2.delete_until_last()
        if isinstance(queue1,SysShdIpcChanC) and isinstance(queue2,SysShdIpcChanC):
            queue1.unlink() #pylint: disable= no-member
            queue2.unlink() #pylint: disable= no-member
            queue1.close() #pylint: disable= no-member
            queue2.close() #pylint: disable= no-member

    @fixture(scope="function")
    def config(self) -> None:
        """Configure the signal handler to signal when the SIGINT is received .
        """
        signal(SIGINT, self.signal_handler)


    #Test container
    @mark.parametrize("set_environ", [[1, 200, 3000, 'thread'],[2, 300, 4000,\
                'thread'], [1, 200, 3000, 'process'],[2, 300, 4000, 'process']],\
                indirect=["set_environ"])
    def test_normal_op(self, set_environ, config) -> None: #pylint: disable= unused-argument
        """Test the machine status .

        Args:
            set_environ ([type]): [description]
            config ([type]): [description]
        """
        log.debug(msg="1. Test SALG machine status: check machine status normal operation")

#######################            FUNCTIONS             #######################

def check_1(__a: Dummy, __b: Dummy, __c: Dummy, test_type: list) -> bool:
    """Runs the test thread 1

    Args:
        __a (Dummy): [description]
        __b (Dummy): [description]
        __c (Dummy): [description]
    """
    global TH1_FAIL #pylint: disable= global-statement
    th1_status = True
    log.debug(f"Test for thread 1: {__a}, {__b}, {__c}")
    if len(test_type)<2:
        queue1 = SysShdIpcChanC(name= 'test_ipc_int')
        queue2 = SysShdIpcChanC(name= 'test_ipc_obj')
    else:
        queue1: SysShdChanC = test_type[0]
        queue2: SysShdChanC = test_type[1]
    queue1.send_data(str(__a))
    sleep(random.uniform(0.5, 1))
    aux2: Dummy = queue2.receive_data()
    sleep(random.uniform(0.5, 1))
    aux1: str = queue1.receive_data()
    log.debug(f'R: {aux1} Exp: {__a.value +1}')
    log.debug(f'R: {aux2.value} Exp: {__b.value}')
    if (int(aux1) == __a.value + 1) and aux2.value == __b.value:
        aux2.value = aux2.value*10
        sleep(random.uniform(0, 0.5))
        queue2.send_data(aux2)
        sleep(random.uniform(3.5, 4))
        aux2 = queue2.receive_data()
        log.debug(f'R: {aux2.value} Exp: {__c.value}')
        if aux2.value != __c.value:
            log.critical(f"The values not what expected, received: {aux2.value} and {__c.value}")
            raise AssertionError((f"The values not what expected, received: {aux2.value} "
                                  f"and {__c.value}"))
        th1_status = False
        log.critical("TEST THREAD 1 DONE CORRECTLY")
    else:
        log.critical((f"The values not what expected, a2: {int(aux1)} expected {__a.value + 1} "
                      f"and b2: {aux2.value} expected {__b.value}"))
        raise AssertionError((f"The values not what expected, a2: {int(aux1)} "
                f" expected {__a.value + 1} and b2: {aux2.value} expected {__b.value}"))
    TH1_FAIL = th1_status
    if len(test_type)<2:
        queue1.close()
        queue2.close()
    return th1_status

def check_2(__a: Dummy, __b: Dummy, __c: Dummy, test_type: list) -> bool:
    """Runs the test thread 2.

    Args:
        __a (Dummy): [description]
        __b (Dummy): [description]
        __c (Dummy): [description]
    """
    global TH2_FAIL #pylint: disable= global-statement
    th2_status = True
    log.debug(f"Test for thread 2: {__a}, {__b}, {__c}")
    if len(test_type)<2:
        queue1 = SysShdIpcChanC(name= 'test_ipc_int')
        queue2 = SysShdIpcChanC(name= 'test_ipc_obj')
    else:
        queue1 = test_type[0]
        queue2 = test_type[1]
    queue2.send_data(deepcopy(__b))
    sleep(random.uniform(0, 0.5))
    aux: str = queue1.receive_data()
    if int(aux) == __a.value:
        log.debug(f'R: {aux} Exp: {__a.value}')
        aux = str(int(aux)+1)
        sleep(random.uniform(0, 0.5))
        queue1.send_data(aux)
        sleep(random.uniform(2.5, 3))
        aux: Dummy = queue2.receive_data()
        sleep(random.uniform(0, .5))
        queue2.send_data(deepcopy(__c))
        log.debug(f'R: {aux.value} Exp: {__b.value*10}')
        if aux.value != __b.value*10:
            log.critical(f"The values not what expected, get: {aux.value} expect: {__b.value*10}")
            raise AssertionError((f"The values not what expected, get: {aux.value} "
                                  f"expect: {__c.value}"))
        th2_status = False
        log.critical("TEST THREAD 2 DONE CORRECTLY")
    else:
        log.critical(f"The values not what expected, a1: {int(aux)} expected {__a.value}")
        raise AssertionError(f"The values not what expected, a1: {int(aux)} expected {__a.value}")
    TH2_FAIL = th2_status
    if len(test_type)<2:
        queue1.close()
        queue2.close()
    return th2_status
