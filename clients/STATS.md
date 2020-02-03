# stats.py

## Usage:

```
usage: stats.py [-h] [-v] [-f FREQUENCY] [--write] [--redis] [--ip] [--tc]
                [--ss] [--queue-limits] [--file-name FILE_NAME]
                [--redis-ip REDIS_IP] [--redis-port REDIS_PORT]
                host_name iface

StatusPusher

positional arguments:
  host_name             Name of the host stats.py is running on
  iface                 Interface to monitor

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable debug log.
  -f FREQUENCY, --frequency FREQUENCY
                        Number of samples per second. (default 1)
  --write               Write statistics to file
  --redis               Enable redis
  --ip                  Parse ip output
  --tc                  Parse tc output
  --ss                  Parse ss output
  --queue-limits        Parse queue limits
  --file-name FILE_NAME
                        Name of output file. (default 'stats.txt')
  --redis-ip REDIS_IP   IP of the redis instance. (default 192.168.10.11)
  --redis-port REDIS_PORT
                        Port of the redis instance. (default 6379)
```

### Example

To write all stats to file:
```
python3 stats.py test_host eth0 --write --tc --ip --queue-limits --ss
```