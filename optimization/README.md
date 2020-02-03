# Optimization

Application-level fairness optimization

| Folder / File | Description                                                     |
|---------------|-----------------------------------------------------------------|
| models/       |  Clone of the models repository.                                |
| runs/         | Output folder of the solved scenarios.                          |
| samples/      | Example input files for the optimization.                       |
| solving/      | Gurobi solving code.                                            |
| tools/        | Helper scripts.                                                 |
| vis/          | Scripts to generate result plots.                               |
| run_simple.py | Solve simple scenarios with one bottleneck.                     |
| run.py        | Solve more complex scenarios with a network topology.           |
| search.py     | Tries to find solutions for min and max number of applications. |

## QUICKSTART

### Clone

Use the *--recurse-submodules* option to include also the utility models.

```
git clone --recurse-submodules git@gitlab.lrz.de:DFG_SDN_APPAWARE/optimization.git
```

### run_simple.py

Solves a simple scenario where there are only unidirectional flows and only one bottleneck link.

Determine the throughput allocation for a scenario with 12 web download clients:

    python3 run_simple.py --scenario samples/simple/12webdl.json

The results are stored in *runs/YYYYMMDD_XXXXXXX/*.

To get detailed visual output of the optimization result, use the *--plotting* parameter:

    python3 run_simple.py --scenario samples/simple/12webdl.json --plotting
    
The plots are put into the output folder of the run.  

To use a constant delay function with 2ms delay for the links, you can use the *2ms.npy* throughput -> delay function:

    python3 run_simple.py --scenario samples/simple/12webdl.json --plotting --delay-approx=samples/simple/2ms.npy

## Usage (run_simple.py)

```
usage: run_simple.py [-h] [-v] [--run-folders RUN_FOLDERS] [--summary SUMMARY]
                     [--model_dir MODEL_DIR] [--scenario SCENARIO]
                     [--delay-approx DELAY_APPROX] [--no-flow-types]
                     [--time-limit TIME_LIMIT] [--plotting]

Solve simple bottleneck scenarios.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable debug log.
  --run-folders RUN_FOLDERS
                        Where to store the detailed run results. (default:
                        runs)
  --summary SUMMARY, -s SUMMARY
                        Filename where to store the summary. (default:
                        summary.json)
  --model_dir MODEL_DIR, -m MODEL_DIR
                        Where the application models are stored. (default:
                        models/postprocessing/models/)
  --scenario SCENARIO   Bottleneck scenario file. (default:
                        samples/simple/2ssh.json)
  --delay-approx DELAY_APPROX
                        Which delay approx. to use. (default:
                        samples/simple/max80perc.npy)
  --no-flow-types       Deactivate same MOS per application type.
  --time-limit TIME_LIMIT
                        Time limit for solving the scenario in seconds.
                        (default: 100)
  --plotting            Activate plotting of results. (default: False)
```