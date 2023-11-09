#!/usr/bin/python3
"""
This module will manage the shared objects.
It will lock the shared object in order to change it savely,
for each channel.
"""

#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################
from copy import deepcopy
from threading import Condition
from typing import List


#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, SysLogLoggerC, sys_log_logger_get_module_logger

if __name__ == "__main__":
    cycler_logger = SysLogLoggerC()
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################
from .sys_shd_common import SysShdErrorC
#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

class SysShdSharedObjC:
    """Class method for creating a class that is used by the sharedObj .
    """
    def __init__(self, shared_obj) -> None:
        '''
        Initialize the mutex lock used to protect the shared object.

        Args:
            shared_obj ([type]): Reference to the shared object.
        '''
        self.__mutex = Condition()
        self.__shared_obj = shared_obj

    def read(self) -> object:
        '''
        Gets the mutex control, copy the shared object, release the mutex control
        and returns the copy.

        Returns:
            object: Copy of the private shared_obj attribute.
        '''
        self.__mutex.acquire()
        copied_obj = deepcopy(self.__shared_obj)
        self.__mutex.release()
        return copied_obj

    def write(self, new_obj) -> None:
        '''
        Gets the mutex control, check if the type of the stored shared_obj is equal
        to the new one, write a copy of the passed object to the local shared_obj
        attribute and return the mutex control.

        Args:
            new_obj ([type]): Object desired to be shared among threads.
        '''
        self.__mutex.acquire()
        if type(self.__shared_obj) is type(new_obj):
            self.__shared_obj = deepcopy(new_obj)
        else:
            log.warning("Type of new object assigned to shared object is \
                        different from the previous one assigned.")
        self.__mutex.release()

    def merge_included_tags(self, new_obj : object, included_tags : List[str]) -> object:
        '''
        Merge shared object with the new object using the attributes specified in included_tags.
        Copies from new_obj to the shared object the attributes whose names appear in included_tags.
        If the attribute is a dictionary, or it is a subclass contained in an dict,
        the merge is done recursively for each item in dict.

        Args:
            new_obj (object): Object that contains the attributes to be copied.
            included_tags (List[str]): Nested names of attributes to be included in merge.
        Returns:
            object: Return a copy of the merged object
        '''
        temp_obj = self.read()

        for tag in included_tags:
            attribs = tag.split(".")
            _merge_class(temp_obj, new_obj, attribs)

        self.write(temp_obj)

        return temp_obj

    def merge_exclude_tags(self, new_obj : object, excluded_tags : List[str]) -> object:
        '''
        Merge shared object with the new object excluding the attributes specified in excluded_tags.
        Copies from new_obj to the shared object all the attributes,
        except those names that appear in excluded_tags.
        If the attribute is a dictionary, or it is a subclass contained in an dict,
        the merge is done recursively for each item in dict.

        Args:
            new_obj (object): Object that contains the attributes to be copied.
            excluded_tags (List[str]): Nested names of attributes to be excluded in merge.
                Attributes preserved from shared object.
            Merge the included_tags into the class .

        Args:
            new_obj (object): [description]
            included_tags (List[str]): [description]

        Returns:
            object: Return a copy of the merged object
        '''
        # Copy original data to preserver excluded tags
        temp_obj = self.read()

        # Write excluded original tags to new object
        for tag in excluded_tags:
            attribs = tag.split(".")
            _merge_class(new_obj, temp_obj, attribs)

        # Write new object with excluded tags to shared object
        self.write(new_obj)

        return new_obj

#######################            FUNCTIONS             #######################
def _merge_class(dst_obj : object, src_obj : object, attribs : List[str]) -> None:
    '''
    Copy the attribute composed of attribs list sequence from src_obj to dst_obj.

    Args:
        dst_obj (object): Destination object where specified attribute is copied.
        src_obj (object): Source object where specified attribute is copied from.
        attribs (List[str]): Sequence of attributes names used
        to achieve the nested attributes to be copied.

    Raises:
        SysShdChanErrorC: Throw an exception if the attribute doesn't exists.
    '''
    # if hasattr(dst_obj, attribs[0]) and hasattr(src_obj, attribs[0]):
    if hasattr(src_obj, attribs[0]):
        if hasattr(dst_obj, attribs[0]):
        ## Attribute exists on both instances, perform merge
            old_inst = getattr(dst_obj, attribs[0])
            if isinstance(old_inst, dict):
                new_dict = getattr(src_obj, attribs[0])
                for key, value in old_inst.items():
                    if len(attribs) > 1:
                        _merge_class(value, new_dict[key], attribs[1:])
                    else:
                        old_inst[key] = new_dict[key]
                setattr(dst_obj, attribs[0], old_inst)
            else:
                if len(attribs) > 1:
                    _merge_class(getattr(dst_obj, attribs[0]), \
                                        getattr(src_obj, attribs[0]), attribs[1:])
                else:
                    setattr(dst_obj, attribs[0], getattr(src_obj, attribs[0]))
        else:
            ## Attribute exists only on dst, not in source: copy it to dst
            new_inst = getattr(src_obj, attribs[0])
            setattr(dst_obj, attribs[0], new_inst)

    else:
        log.error(f"New object doesn't have attribute: {attribs[0]}")
        raise SysShdErrorC(message=f"New object doesn't have attribute: {attribs[0]}")
