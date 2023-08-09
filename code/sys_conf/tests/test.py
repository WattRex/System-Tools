#!/usr/bin/python3
"""
    This is a test for system config tool 
"""
#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################

#######################       THIRD PARTY IMPORTS        #######################
from system_config_tool import sys_conf_read_config_params, SysConfSectionNotFoundErrorC

#######################          MODULE IMPORTS          #######################

try:
    sys_conf_read_config_params(
            filename = "./log_config.yaml", section = 'sys_conf')
    print("No errors and working correctly")
except SysConfSectionNotFoundErrorC as exception:
    print(exception)
    print("Could not read correctly log config params")
