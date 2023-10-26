# Sync Functionalities

Repository where classes and functions used to share elements within python are stored.
Once a shared object is created and initilized with data, all the data stored in that
object must have the same type.

### IPC channels

The system maximum POSIX queues size is defined by `RLIMIT_MSGQUEUE` constant used on
posix library. It also can be checked by means of `ulimit -q` command. Default value is
819200 bytes. It determines the number of queues allowed:
`num_queues = RLIMIT_MSGQUEUE/num_msg_per_queue/max_msg_size`

The maximum length of a message sent through POSIX queue is define in the file:
`cat /proc/sys/fs/mqueue/msgsize_max`

Can be change using the command:
`sudo sh -c 'echo 200 > /proc/sys/fs/mqueue/msgsize_max'`

The maximum number of a messages allocated in a POSIX queue is define in the file:
`cat /proc/sys/fs/mqueue/msg_max`
Can be change using the command:
`sudo sh -c 'echo 200 > /proc/sys/fs/mqueue/msg_max'`

The parameters `max_msg` and `max_message_size` given to `SysShdIpcChanC` must be
lower that ones specified on Linux files.

For further information, check the [Github Issue: Change default values for message queue](https://github.com/osvenskan/posix_ipc/issues/21#issuecomment-912659571)
