#!/usr/bin/python3
'''
This module works to have a logger instead of using prints,
it will create a file to save all the messages
with the hour and the module the message belongs to.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from pathlib import Path
import os

#######################      LOGGING CONFIGURATION       #######################

#######################         GENERIC IMPORTS          #######################
from logging.config import fileConfig
from logging.handlers import RotatingFileHandler
from logging import getLogger, Logger, debug, Formatter, FileHandler,\
    DEBUG, INFO, WARNING, ERROR, CRITICAL
from configparser import ConfigParser

#######################       THIRD PARTY IMPORTS        #######################
import yaml

#######################          MODULE IMPORTS          #######################

#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################
dir_path: str = os.path.dirname(p=os.path.realpath(filename=__file__))

#######################             CLASSES              #######################
class SysLogLoggerC():
    '''
    This function will be called after the system has been called .
    '''
    def __init__(self, \
                 file_config_path:str = dir_path+'/logginConfig.conf', \
                 file_log_levels: str = '...',
                 output_sub_folder : str = None) -> None:
        #Example: file_config_path = './myLogginConfig.conf'
        '''
        Initialize the main logger.
        It is necessaty to be used only once and before any other module is imported
        in the main file.

        Args:
            file_config_path (str): Path to the yaml file that containg the log configuration
        '''
        config_parser = ConfigParser()
        config_parser.read(filenames=file_config_path)
        if 'handler_rotatingFileHandler' in config_parser and 'args' \
            in config_parser['handler_rotatingFileHandler']:   # Check if the logConfigFile
            log_folder, log_file_name = self.__parse_log_folder(config_parser)
            if output_sub_folder is not None:
                log_folder += '/' + output_sub_folder
                Path(log_folder).mkdir(parents = True, exist_ok = True)
                log_file_path = log_folder+"/"+log_file_name
                print(f"Log final filename: {log_file_path}")
            else:
                Path(log_folder).mkdir(parents = True, exist_ok = True)

        ## Logging fileconfig
        print("Fichero leido")

        fileConfig(fname=file_config_path,disable_existing_loggers=True)

        prev_fmt = Logger.root.handlers[0].formatter
        # TODO: comprobar que es el root logger                              #pylint: disable=fixme
        if prev_fmt is not None:
            color_fmt = SysLogCustomFormatterC(fmt=prev_fmt._fmt, style='%',\
                                               datefmt=prev_fmt.datefmt)
            Logger.root.handlers[0].setFormatter(color_fmt)
        # TODO: añadir else y casos de error                                 #pylint: disable=fixme

        print("Logger configurado")
        if file_log_levels != '...' and os.path.isfile(file_log_levels):
            getLogger().__setattr__('custom_levels_path', file_log_levels)
        else:
            raise FileNotFoundError(f'File "{file_log_levels}" not found. \
                                        Please, check the path and try again.')
        #, encoding='utf-8'
        for han in getLogger().handlers:
            if isinstance(han, RotatingFileHandler):
                if output_sub_folder is not None:
                    prev_file = han.baseFilename
                    if os.path.isfile(prev_file):
                        os.remove(prev_file)
                    han.baseFilename = log_file_path
                han.doRollover()
        debug('First log message...')

    def __parse_log_folder(self, config_parser) -> str:
        '''
        This function will transform a string retrieved from
        config_parser['handler_rotatingFileHandler']['args'] like
        "('./log_mqtt_client/logging_rotatingfile_example.log', 'w', 1000000, 20)"
            into
        "./log_mqtt_client"
        '''
        log_folder_list = config_parser['handler_rotatingFileHandler']\
            ['args'].split(",", 1)[0][2:-1].split("/")
        # return log_folder_list
        log_folder = ""
        for aux in range(len(log_folder_list)-1):
            log_folder += log_folder_list[aux] + "/"
        return (log_folder[:-1], log_folder_list[-1])


class SysLogCustomFormatterC(Formatter):
    '''
    Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629
    '''
    grey = '\x1b[38;5;253m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    #bold_red = '\x1b[31;1m'
    bold_red = '\x1b[1;37;41m'
    reset = '\x1b[0m'

    def __init__(self, fmt: str or None = ..., datefmt: str or None = ..., style = ...) -> None:
        '''
        Initialize the custom format logger .

        Args:
            fmt (strorNone, optional): String used to format the log message.
            datefmt (strorNone, optional): Format used to print the datetime.
            style ([type], optional): Style used to print the log message.
        '''
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.fmt: str = fmt
        self.formats: dict[int, str] = {
            DEBUG: self.grey + self.fmt + self.reset,
            INFO: self.blue + self.fmt + self.reset,
            WARNING: self.yellow + self.fmt + self.reset,
            ERROR: self.red + self.fmt + self.reset,
            CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record) -> str:
        '''
        Format log record.

        Args:
            record ([type]): Logger record to be formatted.

        Returns:
            [type]: return the record formatted.
        '''
        log_fmt: str | None = self.formats.get(record.levelno)
        formatter = Formatter(log_fmt)
        return formatter.format(record)


class _SectionNotFoundErrorC(Exception):
    '''
    Handle exception thrown in SysLog sectionNotFoundC .

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
def sys_log_logger_get_module_logger(name : str,
            config_by_module_filename : str = dir_path+'/log_config.yaml') -> Logger:
    '''
    Configures the logger for the given module name and assigns custom logging level defined
    in a .yaml file.

    Args:
        name (str): __name__ E.g. MID.MID_DABS.MID_DABS_Node
        config_by_module_filename (str, optional): Path to the yaml file
        that contains the log configuration by module. Defaults to './log_config.yaml'.

    Returns:
        log (Logger): Return the log to be used in a specific module file
    '''
    root_log: Logger = getLogger()
    try:
        config_by_module_filename = root_log.custom_levels_path # type: ignore
    except AttributeError as exc:
        raise ImportError(f'The main logger has not been initialized before "{name}" import. \
                          Please, initialize the logger before importing any module.') from exc

    log: Logger = getLogger(name)
    try:
        if name != '__main__': #Main script is not named (__name__) like the other scripts
            name_list = name.split('.')
            name = ''
            if len(name_list) > 1:
                # Convert name to module name. Ex: APP.APP_DIAG.APP_DIAG_String -> APP.APP_DIAG
                name = '.'.join(name_list[:-1])
            else:
                # For test file. Ex: Test_APP_DIAG
                name = name_list[0]
        custom_level = __read_config_params(
            filename = config_by_module_filename, section = name)
        log.setLevel(str(custom_level))
        log.debug(msg=f"log level of {name} has been set to {custom_level}")

        # Assign the file handler to the logger
        # if the module name is found in the file_handlers section
        file_handlers = __read_config_params(
            filename = config_by_module_filename, section = 'file_handlers')
        for key in file_handlers:
            for module_name in file_handlers[key]:
                # log.critical(f"module_name: {module_name}")
                if name == module_name:
                    file_handler = FileHandler(filename = "./log/" +\
                                        key + ".log", mode = 'w+', encoding = 'utf-8')
                    config_parser = ConfigParser()
                    config_parser.read("./SYS/SYS_LOG/logginConfig.conf")
                    # if 'formatter_plain' in config_parser and
                    # 'format' in config_parser['handler_rotatingFileHandler']:
                    file_handler.setFormatter(Formatter(fmt = \
                                        config_parser.items('formatter_plain', True)[0][1]))
                    file_handler.setLevel("DEBUG")
                    log.addHandler(file_handler)
                    log.debug(f"Added handler for {module_name} ({key} file)")
        # Custom logging level set in .yaml file will be applied

    except _SectionNotFoundErrorC as exception:
        #Default logging level set in config will be applied
        log.warning(f"{exception}")
        # log.warning(f"Module {name} not found in the log level
        # configuration by module file\n{exception.__str__()}")
    except Exception as exception:
        log.error(f"{exception}")
    return log


def __read_config_params(filename:str = 'config.yaml',
                            section: str|None = None) -> dict:
    '''
    Reads config parameters from a config file.

    Args:
        - filename (str, optional): Path to the file used to read the configuration.
        Defaults to 'config.yaml'.
        - section (str, optional): Section to be parsed from the configuration file.

    Raises:
        - SYS_LOG_Section_Not_Found_Error_c: Throw an exception if the section is
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
            raise _SectionNotFoundErrorC( \
                f"Section {section} not found in the {filename} file")
    return data
