#!/usr/bin/python3
"""
This file works as a test for the system logger tool package.
This will be the main test file where the logger is called"""

#######################        MANDATORY IMPORTS         #######################
import context #pylint: disable=unused-import

#######################         GENERIC IMPORTS          #######################

#######################      LOGGING CONFIGURATION       #######################
from src.system_logger_tool import SysLogLoggerC,\
    sys_log_logger_get_module_logger, Logger

cycler_logger = SysLogLoggerC(file_log_levels="./code/sys_log/tests/log_config.yaml")

# Optional to include custom logginConfig.conf
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################
from support_code import log_test

#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################
class TestLogs:
    """Classmethod to run pytest .
    """
    def test_logging(self):
        """Test the logging with 2 files .
        """
        log.debug("This is a log debug entry to try the log in a file with a main")
        log.info("This is a log INFO entry to try the log in a file with a main")
        log_test()
        log.warning("This is a log WARNING entry to try the log in a file with a main")
        log.error("This is a log ERROR entry to try the log in a file with a main")
        log.critical("This is a log CRITICAL entry to try the log in a file with a main")
