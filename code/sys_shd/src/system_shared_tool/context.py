#!/usr/bin/python3
'''
This module manages the constants variables.
Those variables are used in the scripts inside the module and can be modified
in a config yaml file specified in the environment variable with name declared
in system_config_tool.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
#######################         GENERIC IMPORTS          #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger
if __name__ == "__main__":
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################

#######################          PROJECT IMPORTS         #######################
from system_config_tool import sys_conf_update_config_params

#######################          MODULE IMPORTS          #######################

######################             CONSTANTS              ######################
# For further information check out README.md
DEFAULT_CHAN_NUM_MSG : int = 100 # Max number of allowed message per chan
DEFAULT_IPC_MSG_SIZE : int = 100 # Size of message sent through IPC message queue
DEFAULT_CHAN_TIMEOUT : int = 1

CONSTANTS_NAMES = ('DEFAULT_CHAN_NUM_MSG', 'DEFAULT_IPC_MSG_SIZE', 'DEFAULT_CHAN_TIMEOUT')
sys_conf_update_config_params(context=globals(),
                              constants_names=CONSTANTS_NAMES)
