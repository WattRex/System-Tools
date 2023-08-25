#!/usr/bin/python3
"""
This file works as a test for the system logger tool package.
This will be a secondary test file to prove that the package can be called from
different files and works properly"""

#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################

#######################      LOGGING CONFIGURATION       #######################
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger, Logger

if __name__ == "__main__":
    cycler_logger = SysLogLoggerC(file_log_levels="log_config.yaml")
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################

#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

def log_test():
    """
    Test the logger in other files
    """
    log.info("This is a message to test info in secondary file")
    log.debug("This is a message to test DEBUG in secondary file")
    log.error("This is a message to test ERROR in secondary file")
    log.critical("This is a message to test CRITICAL in secondary file")
