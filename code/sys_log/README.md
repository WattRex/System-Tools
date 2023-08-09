# System logger module
Module used for system logger tool.  It will record log events and write them out 
in a file with different information such as the file where the log is and the line.
The purpose of this module is to have a logger in common for all the files your app may need.
There are different log levels entries and the minimum log level can be configured 
in a log_config.yaml
This file should be located in the folder where the main file is going to be launched.
There is a template for the log_config.yaml
The different log level entries are from less important to most:
DEBUG, INFO, WARNING, ERROR, CRITICAL

```

--- #YAML FILE START
__main__: "DEBUG" 

##### sys #####
sys_shd: "CRITICAL"
sys_conf: "WARNING"
sys_log: "INFO"

file_handlers: {
  # "log_can" : [ drv.drv_can, drv.drv_epc ],
}

```