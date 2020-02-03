cur_dir=$(dirname $0)
${cur_dir}/../../Daemon/DaemonCLI.py -r 127.0.0.1 quit
sleep 15
${cur_dir}/run_all.sh "sudo pkill screen"
${cur_dir}/run_all.sh "rm -rf dfg-*"
${cur_dir}/run_all.sh "clients/start_daemons.py -r 10.0.5.0 -k"
