#!/usr/bin/python3
"""
This file works as a test for the system logger tool package.
This will be the main test file where the logger is called"""

#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################

#######################      LOGGING CONFIGURATION       #######################

from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger, Logger

if __name__ == "__main__":
    cycler_logger = SysLogLoggerC()
    # Optional to include custom logginConfig.conf
log: Logger = sys_log_logger_get_module_logger(name=__name__, config_by_module_filename="log_config.yaml")
# Optional to include custom log config yaml

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################
import test2
#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

if __name__ == "__main__":
    log.debug("This is a log debug entry to try the log in a file with a main")
    log.info("This is a log INFO entry to try the log in a file with a main")
    test2.log_test()
    log.warning("This is a log WARNING entry to try the log in a file with a main")
    log.error("This is a log ERROR entry to try the log in a file with a main")
    log.critical("This is a log CRITICAL entry to try the log in a file with a main")
