#!/usr/bin/python3
"""
This file works as a test for the system logger tool package.
This will be a secondary test file to prove that the package can be called from
different files and works properly"""

import system_logger_tool as sys_log

if __name__ == "__main__":
    cycler_logger = sys_log.SysLogLoggerC()
log = sys_log.sys_log_logger_get_module_logger(__name__)

def log_test(algo: float = 12):
    """
    Test the logger in other files
    """
    log.info("HOLA")
    print("HOLA")
    log.info("This is a message to test info in secondary file")
    number = int(input("Introduce un numero: "))
    print(f"Suma de los numeros introducidos es {number+algo}")
    log.debug("This is a message to test DEBUG in secondary file")
    log.error("This is a message to test ERROR in secondary file")
    log.critical("This is a message to test CRITICAL in secondary file")
