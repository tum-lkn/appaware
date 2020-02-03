# Netstatspy


Netstatspy fulfills two tasks: Reading/parsing the output of system calls and logging them in different ways.

## Installation

Copy the source code to your project or use pip:

```bash
pip install netstatspy
```

### Limitations

The Code is Linux only and was tested with Ubuntu 17.10. Furthermore netstatspy only supports Python3.X

## Sample Usage

To test if your installation was successful simply call

```bash
netstatspy
```

This will print the ip statistics of all interfaces to your console every second. Netstatspy will stop after 10 seconds.

### Arguments

You can modify the behaviour of netstatspy by adding arguments (see output of help below)

```bash
usage: netstatspy.py [-h] [-v] [--iface IFACE] [-f FREQUENCY] [-t TIME] [-c]
                     [-j] [--file-name FILE_NAME] [--no-ip] [--tc] [--ss]
                     [--queue-limits] [--small-queue]

StatusPusher

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable debug log.
  --iface IFACE         Interface to monitor. If set to None (default value)
                        all available interfaces will be monitored
  -f FREQUENCY, --frequency FREQUENCY
                        Number of samples per second. (default 1)
  -t TIME, --time TIME  The duration (in s) netstatspy should run. If None it
                        will run forever
  -c, --no-console      Do not print statistics to the console
  -j, --json            Write statistics to file
  --file-name FILE_NAME
                        Name of output file. (default 'stats.txt'). Only used
                        if "-j" optionis active
  --no-ip               Do not parse ip output
  --tc                  Parse tc output
  --ss                  Parse ss output
  --queue-limits        Parse queue limits
  --small-queue         Parse small queue values

```

## Used commands

Natstatspy uses/reads the following commands/files to acquire the network statistics

### IP
ip calls the following command:
``` bash
ip -s link
```
### TC
tc calls the following command:
``` bash
tc -s qdisc
```

### SS
ss calls the following command:
``` bash
ss -inm --tcp --udp -o state established
```

Therefore only established udp and tcp connections are parsed

### Queue Limits

### Small Queue Limits

## Classes

### Readers

#### AbstractReader()

The base class every Reader inherits from. There are two public functions:

##### get_all_stats()

Returns a list of all stats that can be collected by this reader.

##### get_type()

Returns a string indicating the type of the logger/statistics it reads. These strings are:

* `'ip'`
* `'tc'`
* `'ss'`
* `'queue_limits'`
* `'small_queue''`

### Loggers
