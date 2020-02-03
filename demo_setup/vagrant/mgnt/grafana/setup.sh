#!/usr/bin/env bash

function get_url_code {
	last_response=$(
	    curl $1 \
        	--write-out %{http_code} \
	        --silent \
        	--output /dev/null \
	)

	echo "GET: $1 (code: $last_response)"
}

function wait_for_url {

	local COUNTER="0"
	local MAX_WAIT=120

	echo "Waiting for $1 to return code $2 (max: $MAX_WAIT s)."

	while (( $COUNTER < $MAX_WAIT ));
	do

		get_url_code $1
		local resp=$last_response

		echo Waited $COUNTER/$MAX_WAIT seconds so far.

		if [[ "$resp" -eq $2 ]]; then
			break
		fi

		COUNTER=$[$COUNTER + 1]

		sleep 1
	done

	if (( $COUNTER == $MAX_WAIT ));
	then
		echo "FAILED TO GET CODE $2 FROM URL $1 !"
	else
		echo "URL($1) available now. After $COUNTER seconds."
	fi
}

IP="10.0.8.0"
# Grafana
GIP=$IP
# InfluxDb
IIP=$IP

echo "Setting up InfluxDb and Grafana at $IP."

# Make sure InfluxDB database exists

wait_for_url "http://$IIP:8086/ping" 204
curl -s -S -G http://$IIP:8086/query -X POST --data-urlencode "q=CREATE DATABASE appaware"

sleep 0.5

# Add InfluxDb datasource to Grafana

wait_for_url "http://admin:admin@$IIP:3000/api/datasources" 200
curl -s -S -H "Content-Type:application/json" -X POST http://admin:admin@$GIP:3000/api/datasources --data-binary @datasource.json

sleep 0.5

# Add the dashboard to Grafana
wait_for_url "http://admin:admin@$IIP:3000/api/dashboards/home" 200
curl -s -S -H "Content-Type:application/json" -X POST http://admin:admin@$GIP:3000/api/dashboards/db --data-binary @demodashboard.json
