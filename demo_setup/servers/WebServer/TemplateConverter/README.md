# WebClient
## Dependencies
```
provision.sh
```

## Usage
config sample can be found at sample_config.json

```
$ ./TemplateConverter.py --help
usage: TemplateConverter.py [-h] -c CONFIG_FILE [-f] -i INPUT_DIR -o
                            OUTPUT_DIR

TemplateConverter parameter

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config CONFIG_FILE
                        Config file
  -f, --force           Force output replacement
  -i INPUT_DIR, --input INPUT_DIR
                        Input directory to be converted
  -o OUTPUT_DIR, --output OUTPUT_DIR
                        Output directory for converted files
```

## Description
Searches for specified tags in *.html/*.htm files and replaces their resource paths based on resource classification. Tags, classification and servers are specified in sample_config.json
