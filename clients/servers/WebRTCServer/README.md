# WebRTCServer
## Dependencies and setup
```
provision.sh
```

## Usage

Make sure nginx is running and start signaling server

```
$ service nginx restart

$ nodejs chat.js
```

Start the WebRTCServer.py script from the clients root:

```
python3 -m servers.WebRTCServer.WebRTCServer
```

