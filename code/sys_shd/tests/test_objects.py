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
from threading import Event
from signal import signal, SIGINT
from time import sleep
from pytest import fixture, mark

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger

main_logger = SysLogLoggerC(file_log_levels="code/sys_shd/tests/log_config.yaml")
log: Logger = sys_log_logger_get_module_logger(name="test_shd_chanel")

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/')
from sys_shd.src.system_shared_tool import SysShdSharedObjC, SysShdNodeC
#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################
#######################             CLASSES              #######################
class DummyHolaC:
    """A dummy class .
    """
    def __init__(self):
        self.adios: str = "adios"
        self.mundo: str = "mundo"

class DummyTardesC:
    """A dummy class .
    """
    def __init__(self):
        self.marius: str = "marius"
        self.javi: str = "javi"
        self.roberto: str = "roberto"

class DummyBuenosC:
    """A dummy class .
    """
    def __init__(self):
        self.dias: str = "dias"
        self.tardes: DummyTardesC = DummyTardesC()

class DummyMariusC:
    """A dummy class .
    """
    def __init__(self):
        self.hola: DummyHolaC = DummyHolaC()
        self.buenos: DummyBuenosC = DummyBuenosC()

class DummyObject:
    """A dummy class .
    """
    def __init__(self, value_a: int, value_b: int):
        self.value_a: int = value_a
        self.value_b: int = value_b

    def __str__(self) -> str:
        return str(self.value_a)+' '+str(self.value_b)
class DummyNode(SysShdNodeC):
    """ Dummy node that contains a shared object and a thread that modifies it."""
    def __init__(self, shd_obj: SysShdSharedObjC, thread_1: bool, working_flag: Event, period: int):
        log.info(msg=f"Creating DummyNode_{int(thread_1)}")
        super().__init__(name= f"DummyNode_{int(thread_1)}", cycle_period= period,
                         working_flag= working_flag)
        self.shd_obj = shd_obj
        self.__local_obj: DummyObject
        self.__thread_1 = thread_1
        if self.__thread_1:
            ## Node 1
            self.__local_obj= DummyObject(0,-10)
            self.__local_obj.value_c = -500
        else:
            ## Node 0
            self.__local_obj= DummyObject(-200,1000)
            self.__local_obj.value_d = 500

    def sync_shd_data(self) -> None:
            """
            Synchronize the local object with the shared object 
            by either merging included tags or excluding tags.

            If the thread is running, merge the included tags 'value_a' and 'value_c' 
            from the shared object into the local object.
            Otherwise, merge the excluded tag 'value_a' from
            the shared object into the local object.

            Returns:
                None
            """
            if self.__thread_1:
                ## Node 1
                self.__local_obj = self.shd_obj.merge_included_tags(new_obj= self.__local_obj,
                                                included_tags= ['value_a', 'value_c'])
            else:
                ## Node 0
                self.__local_obj = self.shd_obj.merge_exclude_tags(new_obj= self.__local_obj,
                                                included_tags= ['value_a'])
            log.info(msg=f"DummyNode_{int(self.__thread_1)}: {self.__local_obj.__dict__}")

    def process_iteration(self) -> None:
            """
            Actualiza los datos de shd y modifica los valores
            de los objetos locales según el hilo activo.
            """
            self.sync_shd_data()
            if self.__thread_1:
                ## Node 1
                self.__local_obj.value_a += 1
                self.__local_obj.value_c += 1
            else:
                ## Node 0
                self.__local_obj.value_b -= 1
                self.__local_obj.value_d -= 1
    
    def stop(self) -> None:
        """Stop the node.
        """
        log.info(msg=f"Stopping DummyNode_{int(self.__thread_1)}")
        self.working_flag.clear()

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
        self.working_flag_0.clear()
        self.working_flag_1.clear()
        exit(0)

    @fixture(scope="function", autouse=False)
    def set_environ(self, request):
        """Setup the environment variables and start the process .

        Args:
            request ([type]): [description]

        Yields:
            [type]: [description]
        """
        # Shared object between threads
        test_obj = SysShdSharedObjC(DummyObject(0, 0))
        # Create nodes
        self.working_flag_0 = Event()
        self.working_flag_1 = Event()
        self.working_flag_0.set()
        self.working_flag_1.set()
        node_1 = DummyNode(shd_obj= test_obj, thread_1= False,
                           working_flag= self.working_flag_0, period= 100)
        node_2 = DummyNode(shd_obj= test_obj, thread_1= True,
                           working_flag= self.working_flag_1, period= 100)
        sleep(1)

        # Initialize threads/process
        node_1.start()
        node_2.start()
        sleep(0.5)
        i = 0
        check_objt: DummyObject = test_obj.read()
        log.info(f"Values of shared object: {check_objt.__dict__}")
        while (check_objt.value_a < 1000 and check_objt.value_b > 0 and
               check_objt.value_c < 1000 and check_objt.value_d > 0):
            if i > 500:
                raise AssertionError("The threads are not sharing as expected")
            # log.info(f"Values of shared object: {check_objt.__dict__}")
            i = i+1
            sleep(0.5)
            check_objt = test_obj.read()
        #######################          TEARDOWN              #######################
        self.working_flag_1.clear()
        self.working_flag_0.clear()
        sleep(1)

    @fixture(scope="function")
    def config(self) -> None:
        """Configure the signal handler to signal when the SIGINT is received .
        """
        signal(SIGINT, self.signal_handler)


    #Test container
    @mark.parametrize("set_environ", [['Shared object test']], indirect=["set_environ"])
    def test_normal_op(self, set_environ, config) -> None: #pylint: disable= unused-argument
        """Test the machine status .

        Args:
            set_environ ([type]): [description]
            config ([type]): [description]
        """
        log.debug(msg="1. Test SALG machine status: check machine status normal operation")

#######################            FUNCTIONS             #######################
