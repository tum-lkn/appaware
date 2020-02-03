# Virtual Testbed Set-up

## Machines

The vagrant contains the following virtual machines:

| Name             | Role          | Mgnt- IP      | Services                                  |
| ---------------- | ------------- | ------------- | ----------------------------------------- |
| pc1              | client0       | 10.0.1.0      | Client applications (browser, etc.)       |
| pc2              | server0       | 10.0.2.0      | Server applications (nginx, etc.)         |
| pc5              | server1       | 10.0.5.0      | Server applications (nginx, etc.)         |
| pc6              | -------       | 10.0.6.0      | Server applications (nginx, etc.)         |
| switch           | switch        | 10.0.7.0      | (Virtual) Bottleneck Switch               |
| mgnt             | mgnt-pc       | 10.0.8.0      | Redis, DemoController, GUI, AppController |

## Management Network

The Management Networks is defined by 10.0.0.0/20 (netmask 255.255.240.0)

## Test Network

### Subnets:

| IP-Address  | CIDR-Suffix | Network mask  | First IP    | Last-IP       |
|-------------|-------------|---------------|-------------|---------------|
| 192.168.0.0 | 22          | 255.255.252.0 | 192.168.0.1 | 192.168.3.254 |
| 192.168.4.0 | 22          | 255.255.252.0 | 192.168.4.1 | 192.168.7.254 |


### IPs

#### Subnet 1

| PC Name            | IP-Address    |
| ------------------ | ------------- |
| PC1                | 192.168.1.0   |
| PC2                | 192.168.2.0   |
| Switch - Subnetz 1 | 192.168.3.100 |

#### Subnet 2

| PC Name            | IP-Address    |
| ------------------ | ------------- |
| Switch - Subnetz 2 | 192.168.4.100 |
| PC5                | 192.168.5.0   |
| PC6                | 192.168.6.0   |
