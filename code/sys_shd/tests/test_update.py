#!/usr/bin/python3
#pylint: disable= duplicate-code
"""
This file test sys shd channels.
"""

#######################        MANDATORY IMPORTS         #######################
import os
import sys
#######################         GENERIC IMPORTS          #######################
from signal import signal, SIGINT
from pytest import fixture, mark

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger

main_logger = SysLogLoggerC(file_log_levels="code/sys_shd/tests/log_config.yaml")
log: Logger = sys_log_logger_get_module_logger(name="test_shd_chanel")

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/')
from sys_shd.src.system_shared_tool import SysShdSharedObjC
#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

class DummyObject:
    """A dummy class .
    """
    def __init__(self, value_a: int, value_b: int):
        self.value_a: int = value_a
        self.value_b: int = value_b

    def __str__(self) -> str:
        return str(self.value_a)+' '+str(self.value_b)

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
        sys.exit(0)

    @fixture(scope="function", autouse=False)
    def set_environ(self, request): #pylint: disable= too-many-statements
        """Setup the environment variables and start the process .

        Args:
            request ([type]): [description]

        Yields:
            [type]: [description]
        """
        log.info(msg= f"Test case: {request.param[0]}")
        ################################# INCLUDED CASES  #################################
        src_obj = DummyObject(0, 0)
        test_obj = SysShdSharedObjC(src_obj)
        cases = ['Include case 0', 'Include case 1', 'Include case 2', 'Include case 3',
                'Include case 4', 'Exclude case 0', 'Exclude case 1', 'Exclude case 2',
                'Exclude case 3', 'Exclude case 4']
        log.info(msg= f"Test case: {cases[0]}, normal op")
        src_obj.value_a = 10
        src_obj.value_b = 20
        src_obj = test_obj.update_including_tags(new_obj= src_obj, included_tags= ['value_a'])
        if src_obj.value_a != 10 and src_obj.value_b != 0:
            raise AssertionError("The included tags are not working as expected in Included case 0")
        log.info(msg= f"Test case: {cases[1]}, an attribute not included doesn't exist in src_obj")
        dst_obj = DummyObject(0, 0)
        dst_obj.value_c= 5 #pylint: disable= attribute-defined-outside-init
        test_obj = SysShdSharedObjC(dst_obj)
        src_obj = DummyObject(0, 0)
        src_obj.value_a = 20
        src_obj.value_b = 30
        src_obj = test_obj.update_including_tags(new_obj= src_obj, included_tags= ['value_a'])
        if src_obj.value_a != 20 and src_obj.value_b != 0 and not hasattr(src_obj, 'value_c'):
            raise AssertionError("The included tags are not working as expected in Included case 1")
        log.info(msg= f"Test case: {cases[2]}, an attribute not included doesn't exist in dst_obj")
        dst_obj = DummyObject(0, 0)
        test_obj = SysShdSharedObjC(dst_obj)
        src_obj = DummyObject(0, 0)
        src_obj.value_a = 30
        src_obj.value_b = 40
        src_obj.value_c = 50 #pylint: disable= attribute-defined-outside-init
        src_obj = test_obj.update_including_tags(new_obj= src_obj, included_tags= ['value_a'])
        if src_obj.value_a != 30 and src_obj.value_b != 0 and hasattr(src_obj, 'value_c'):
            raise AssertionError("The included tags are not working as expected in Included case 2")
        log.info(msg= f"Test case: {cases[3]}, an attribute included doesn't exist in src_obj")
        dst_obj = DummyObject(0, 0)
        dst_obj.value_c= 5 #pylint: disable= attribute-defined-outside-init
        test_obj = SysShdSharedObjC(dst_obj)
        src_obj = DummyObject(0, 0)
        src_obj.value_a = 40
        src_obj.value_b = 50
        src_obj = test_obj.update_including_tags(new_obj= src_obj,
                                                included_tags= ['value_a', 'value_c'])
        if src_obj.value_a != 40 and src_obj.value_b != 0 and not hasattr(src_obj, 'value_c'):
            raise AssertionError("The included tags are not working as expected in Included case 3")
        log.info(msg= f"Test case: {cases[4]}, an attribute included doesn't exist in dst_obj")
        dst_obj = DummyObject(0, 0)
        test_obj = SysShdSharedObjC(dst_obj)
        src_obj = DummyObject(0, 0)
        src_obj.value_a = 50
        src_obj.value_b = 60
        src_obj.value_c = 70 #pylint: disable= attribute-defined-outside-init
        src_obj = test_obj.update_including_tags(new_obj= src_obj,
                                                included_tags= ['value_a', 'value_c'])
        if src_obj.value_a != 50 and src_obj.value_b != 0 and not hasattr(src_obj, 'value_c'):
            raise AssertionError("The included tags are not working as expected in Included case 4")
        ################################# EXCLUDED CASES  #################################
        log.info(msg= f"Test case: {cases[5]}, normal op")
        src_obj = DummyObject(0, 0)
        test_obj = SysShdSharedObjC(src_obj)
        src_obj.value_a = 10
        src_obj.value_b = 20
        src_obj = test_obj.update_excluding_tags(new_obj= src_obj, excluded_tags= ['value_a'])
        if src_obj.value_b != 20 and src_obj.value_a != 0:
            raise AssertionError("The excluded tags are not working as expected in Excluded case 0")
        log.info(msg= f"Test case: {cases[1]}, an attribute not excluded doesn't exist in src_obj")
        dst_obj = DummyObject(0, 0)
        dst_obj.value_c= 5 #pylint: disable= attribute-defined-outside-init
        test_obj = SysShdSharedObjC(dst_obj)
        src_obj = DummyObject(0, 0)
        src_obj.value_a = 20
        src_obj.value_b = 30
        src_obj = test_obj.update_excluding_tags(new_obj= src_obj, excluded_tags= ['value_a'])
        if src_obj.value_a != 0 and src_obj.value_b != 30 and hasattr(src_obj, 'value_c'):
            raise AssertionError("The excluded tags are not working as expected in Excluded case 1")
        log.info(msg= f"Test case: {cases[2]}, an attribute not excluded doesn't exist in dst_obj")
        dst_obj = DummyObject(0, 0)
        test_obj = SysShdSharedObjC(dst_obj)
        src_obj = DummyObject(0, 0)
        src_obj.value_a = 30
        src_obj.value_b = 40
        src_obj.value_c = 50 #pylint: disable= attribute-defined-outside-init
        src_obj = test_obj.update_excluding_tags(new_obj= src_obj, excluded_tags= ['value_a'])
        if src_obj.value_a != 0 and src_obj.value_b != 40 and not hasattr(src_obj, 'value_c'):
            raise AssertionError("The excluded tags are not working as expected in Excluded case 2")
        log.info(msg= f"Test case: {cases[3]}, an attribute excluded doesn't exist in src_obj")
        dst_obj = DummyObject(0, 0)
        dst_obj.value_c= 5 #pylint: disable= attribute-defined-outside-init
        test_obj = SysShdSharedObjC(dst_obj)
        src_obj = DummyObject(0, 0)
        src_obj.value_a = 40
        src_obj.value_b = 50
        src_obj = test_obj.update_excluding_tags(new_obj= src_obj,
                                                excluded_tags= ['value_a', 'value_c'])
        if src_obj.value_a != 0 and src_obj.value_b != 50 and not hasattr(src_obj, 'value_c'):
            raise AssertionError("The excluded tags are not working as expected in Excluded case 3")
        log.info(msg= f"Test case: {cases[4]}, an attribute excluded doesn't exist in dst_obj")
        dst_obj = DummyObject(0, 0)
        test_obj = SysShdSharedObjC(dst_obj)
        src_obj = DummyObject(0, 0)
        src_obj.value_a = 50
        src_obj.value_b = 60
        src_obj.value_c = 70 #pylint: disable= attribute-defined-outside-init
        src_obj = test_obj.update_excluding_tags(new_obj= src_obj,
                                                excluded_tags= ['value_a', 'value_c'])
        if src_obj.value_a != 50 and src_obj.value_b != 0 and not hasattr(src_obj, 'value_c'):
            raise AssertionError("The excluded tags are not working as expected in Excluded case 4")

    @fixture(scope="function")
    def config(self) -> None:
        """Configure the signal handler to signal when the SIGINT is received .
        """
        signal(SIGINT, self.signal_handler)


    #Test container
    @mark.parametrize("set_environ", [['Update/merge function']],
                indirect=["set_environ"])
    def test_normal_op(self, set_environ, config) -> None: #pylint: disable= unused-argument
        """Test the machine status .

        Args:
            set_environ ([type]): [description]
            config ([type]): [description]
        """
        log.debug(msg="1. Test SALG machine status: check machine status normal operation")

#######################            FUNCTIONS             #######################
