//require websocket library
var WebSocketServer = require('ws').Server;

// creating a websocket server at port 9090
var wss = new WebSocketServer({port: 9090});

// all connected to the server users
var users = {};

// handle new connections to server
wss.on('connection', function(connection) {
    console.log("User connected");

    // server connection response
    sendTo(connection, {type: "hello"})

    // handle received messages
    connection.on('message', function(message) {
        var data;
        //accepting only JSON messages
        try {
            data = JSON.parse(message);
        }
        catch (e) {
            console.log("Invalid JSON");
            data = {};
        }

        switch (data.type) {
            //when a user tries to login
            case "login":
                console.log("User login request", data.name);

                // name already taken
                if(users[data.name]) {
                    sendTo(connection, {
                        type: "login",
                        success: false
                    });
                }
                else {
                    // store user and connection on the server
                    users[data.name] = connection;
                    connection.name = data.name;

                    sendTo(connection, {
                        type: "login",
                        success: true
                    });
                }
                break;

            // offer other user a call
            case "offer":
                console.log("Sending offer to", data.name, "(Caller", connection.name + ")");

                // if user exists
                var conn = users[data.name];
                if(conn != null) {
                    // store callee name
                    connection.otherName = data.name;

                    sendTo(conn, {
                        type: "offer",
                        offer: data.offer,
                        name: connection.name
                    });
                }
                break;

            case "answer":
                console.log("Sending answer to: ", data.name);
                //for ex. UserB answers UserA
                var conn = users[data.name];

                if(conn != null) {
                    connection.otherName = data.name;
                    sendTo(conn, {
                        type: "answer",
                        answer: data.answer
                    });
                }
                break;

            case "candidate":
                console.log("Sending candidate to:",data.name);
                var conn = users[data.name];

                if(conn != null) {
                    sendTo(conn, {
                        type: "candidate",
                        candidate: data.candidate
                    });
                }
                break;

            case "leave":
                console.log("Disconnecting from", data.name);
                var conn = users[data.name];

                // notify the other user so he can disconnect his peer connection
                if(conn != null) {
                    conn.otherName = null;
                    sendTo(conn, {
                        type: "leave"
                    });
                }
                break;

            case "userAvailable":
                console.log("Request if user is available:", data.name);
                var available = false;
                var conn = users[data.name];
                // user logged in
                if(conn != null) {
                    // and not in a conversation
                    if(conn.otherName == null) {
                        available = true;
                    }
                }

                sendTo(connection, {
                    type: "userAvailable",
                    available: available
                });

                break;

            default:
                sendTo(connection, {
                    type: "error",
                    message: "Command not found: " + data.type
                });
                break;
        }
    });

    // user disconnects
    connection.on("close", function() {
        if(connection.name) {
            console.log("User left", connection.name)
            // delete user and stored connection
            delete users[connection.name];

            // if user was conencted
            if(connection.otherName) {
                console.log("Informing", connection.otherName, "about disconnect");
                var conn = users[connection.otherName];

                if(conn != null) {
                    conn.otherName = null;
                    sendTo(conn, {
                        type: "leave"
                    });
                }
            }
        }
        console.log("Conenction closed")
    });
});

// send messages json encoded
function sendTo(connection, message) {
    connection.send(JSON.stringify(message));
}
