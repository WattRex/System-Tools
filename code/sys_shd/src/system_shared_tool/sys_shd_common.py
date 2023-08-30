#!/usr/bin/python3
"""
This module has the common classes in system shared.
"""

#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################

#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

class SysShdErrorC(Exception):
    """Internal exception handler.

    Args:
        Exception ([type]): [description]
    """
    def __init__(self, message) -> None:
        '''
        Exception raised for errors when a queue is full and data has tried to be put in it.

        Args:
            message (str): explanation of the error
        '''
        super().__init__(message)

#######################            FUNCTIONS             #######################
