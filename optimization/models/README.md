# Service / Utility Models

| Folder         | Description                                                                                                    |
|----------------|----------------------------------------------------------------------------------------------------------------|
|  service       | Models for (bw,delay) -> KPI                                                                                   |
| utility        | Models for KPI -> QoE/MOS                                                                                      |
| postprocessing |  Read measurements, do (bw,delay) -> KPI -> QoE/MOS. Here the models for the optimization are generated/saved. |

## Examples

### SSH

```python
from utility.ssh import SSHUtility

sshm = SSHUtility()

response_times = [0.1, 0.05] # Response time in seconds

print("= SSH =")
for rpt in response_times:
    print("%.2f s -> Utility %.1f" % (rpt, sshm.predict(rpt)))
```

### WEBDL

```python
from utility.webdl import WebDLUtility
webdlm = WebDLUtility()

dltimes = [10, 150] # Download time in seconds

print("= WebDL =")
for dlt in dltimes:
    print("%.1f s -> Utility %.1f" % (dlt, webdlm.predict(dlt)))
```

### WEB

```python
from utility.web import WebUtility

webm = WebUtility()

dltimes = [0.2, 23.8] # Website load time in seconds

print("= Web =")
for dlt in dltimes:
    print("%.1f s -> Utility %.1f" % (dlt, webm.predict(dlt)))
```