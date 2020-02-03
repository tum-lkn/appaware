# Analyze a bottleneck scenario

Mainly tries to find the right number of applications for the minimum and maximum utility for a bottleneck link based on a given distribution of application types.

## QUICKSTART

Look for all possible utility values for a bottleneck capacity of 10000 Kbps and equal weight for ssh, web and webdl:

	python3 search.py -c 10000 -w 1.0 -d 1.0 -s 1.0

The output is by default written to **runs\_searches/result\_[ID].csv**.

## Arguments

```
usage: search.py [-h] [-v] [--search-folder SEARCH_FOLDER]
                 [--model_dir MODEL_DIR] [--delay-approx DELAY_APPROX]
                 [--time-limit TIME_LIMIT] [--capacity CAPACITY]
                 [--search-cnt SEARCH_CNT]
                 [--model_ssh_weight MODEL_SSH_WEIGHT]
                 [--model_web_weight MODEL_WEB_WEIGHT]
                 [--model_webdl_weight MODEL_WEBDL_WEIGHT]

Searches for a minimum and maximum number of clients for a given application
max and bottleneck throughput.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable debug log.
  --search-folder SEARCH_FOLDER
                        Where to store the result of the search. (default:
                        runs_searches)
  --model_dir MODEL_DIR, -m MODEL_DIR
                        Where the application models are stored. (default:
                        samples/models/)
  --delay-approx DELAY_APPROX
                        Which delay approx. to use. (default:
                        samples/simple/mm1.npy)
  --time-limit TIME_LIMIT
                        Time limit for solving one scenario in seconds.
                        (default: 10)
  --capacity CAPACITY, -c CAPACITY
                        Capacity of the bottleneck link in Kbps. (default:
                        10000)
  --search-cnt SEARCH_CNT
                        How many searches to do in the range from min utility
                        to max utility. (default: 10)
  --model_ssh_weight MODEL_SSH_WEIGHT, -s MODEL_SSH_WEIGHT
                        Weight in the application mix of model_ssh. (default:
                        1.000000)
  --model_web_weight MODEL_WEB_WEIGHT, -w MODEL_WEB_WEIGHT
                        Weight in the application mix of model_web. (default:
                        1.000000)
  --model_webdl_weight MODEL_WEBDL_WEIGHT, -d MODEL_WEBDL_WEIGHT
                        Weight in the application mix of model_webdl.
                        (default: 1.000000)
```
