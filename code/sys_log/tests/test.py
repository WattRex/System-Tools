#!/usr/bin/python3
"""
This file works as a test for the system logger tool package.
This will be the main test file where the logger is called"""

#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################

#######################      LOGGING CONFIGURATION       #######################
import system_logger_tool as sys_log

if __name__ == "__main__":
    cycler_logger = sys_log.SysLogLoggerC() 
    # Optional to include custom logginConfig.conf
log = sys_log.sys_log_logger_get_module_logger(__name__, "log_config.yaml") 
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
