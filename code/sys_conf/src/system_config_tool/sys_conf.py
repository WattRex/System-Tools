#!/usr/bin/python3
'''
This module works to have a configuration, mainly for the logger.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from sys import argv
from os import getenv

#######################       THIRD PARTY IMPORTS        #######################
import yaml

#######################      LOGGING CONFIGURATION       #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger
if __name__ == "__main__":
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          MODULE IMPORTS          #######################

#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################
class SysConfSectionNotFoundErrorC(Exception):
    '''
    Handle exception thrown in SysConf sectionNotFoundC .

    Args:
        Exception ([type]): [description]
    '''
    def __init__(self, message) -> None:
        '''
        Exception raised for errors when a section is not found in the file.

        Args:
            - message (str): explanation of the error
        '''
        super().__init__(message)


#######################            FUNCTIONS             #######################
def sys_conf_read_config_params(filename:str = 'config.yaml',
                            section: str|None = None) -> dict:
    '''
    Reads config parameters from a config file.

    Args:
        - filename (str, optional): Path to the file used to read the configuration.
        Defaults to 'config.yaml'.
        - section (str, optional): Section to be parsed from the configuration file.

    Raises:
        - SYS_CONF_Section_Not_Found_Error_c: Throw an exception if the section is
        not found in the file or the file does not exists.

    Returns:
        - data (dict): Dictionary with the configuration section read.
    '''
    data = {}
    with open(filename, 'r', encoding= 'utf-8') as file:
        data = yaml.safe_load(file)
    if section is not None:
        if section in data:
            data = data[section]
        else:
            raise SysConfSectionNotFoundErrorC( \
                f"Section {section} not found in the {filename} file")
    return data


def sys_conf_update_config_params(context : dict,
                                  constants_names : tuple,
                                  section : str|None = None):
    '''
    Update the constants in the context dictionary with the values read from the
    configuration file.

    Args:
        - context (dict): Dictionary with the context to be updated.
        - constants_names (tuple): Tuple with the names of the constants to be
        updated.
        - section (str, optional): Section to be parsed from the configuration file.
    '''
    if section is None:
        section = context['__package__'].split(".")[-1]
    custom_params = sys_conf_read_config_params(filename = getenv('CONFIG_FILE_PATH', ''),
                                                section=section)
    for const_name in constants_names:
        if const_name in custom_params:
            context[const_name] = custom_params[const_name]
            log.debug(f"Constant {const_name} updated to: {custom_params[const_name]}")


def sys_conf_get_argv_password() -> str:
    '''
    Get the password from the sys.argv if a -p or --password argument
    followed by the password was given in the python command.
    Examples: \n
    `python3 main.py -p s3cr3tp4ssw0rd`\n
    `python3 main.py --password s3cr3tp4ssw0rd`

    Returns:
        - password (str): Returns the password given as argument in the python
        command or "" (empty str) if no argument was given.
    '''
    password = ''
    if len(argv) > 1:
        if '-p' in argv:
            list_index = argv.index('-p')
            password = argv[list_index + 1]
        elif '--password' in argv:
            list_index = argv.index('--password')
            password = argv[list_index + 1]
    return password
