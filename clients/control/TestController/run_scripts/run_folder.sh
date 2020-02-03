#!/bin/bash

if [ -z "$1" ]; then
	echo "No folder supplied"
	exit 1
fi

folder=$1

cur_dir=$(dirname $0)

echo $folder

for file in ${folder}/*.json; do
	config_path=$(realpath $file)
	config_name=$(basename $config_path)
	
	echo $config_name
	${cur_dir}/restart_daemons.sh
	sleep 10
	${cur_dir}/../TestController.py -c $config_path
	sleep 90
done