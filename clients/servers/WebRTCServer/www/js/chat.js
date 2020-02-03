// our username and name we are connected to
var name;
var connectedUser;
var peerConnection;
var stream;

// UI elements
var loginPage = document.querySelector('#loginPage');
var callPage = document.querySelector('#callPage');

var usernameInput = document.querySelector('#usernameInput');
var calleeNameInput = document.querySelector('#calleeNameInput');

var loginBtn = document.querySelector('#loginBtn');
var callBtn = document.querySelector('#callBtn');
var hangUpBtn = document.querySelector('#hangUpBtn');

var localVideo = document.querySelector('#localVideo');
var remoteVideo = document.querySelector('#remoteVideo');

var localUsername = document.querySelector('#localUsername');
var remoteUsername = document.querySelector('#remoteUsername');
var statusBar = document.querySelector('#statusBar');

var appStatus = {socketConnected: false, socket: "not connected", app: "waiting for socket", username: "", remoteUsername: ""}

var rtcStatList = new Array();

// storage for userAvailable request because of async WebSocket messaging
var userAvailableResponse = null

// TODO Browser compability shim
//https://webrtc.github.io/adapter/adapter-latest.js

navigator.getUserMedia = (navigator.getUserMedia              ||
                          navigator.mozGetUserMedia           ||
                          navigator.mediaDevices.getUserMedia ||
                          navigator.webkitGetUserMedia);
window.RTCSessionDescription = (window.RTCSessionDescription    ||
                                window.mozRTCSessionDescription ||
                                window.webkitRTCSessionDescription);
window.RTCIceCandidate = (window.RTCIceCandidate    ||
                          window.mozRTCIceCandidate ||
                          window.webkitRTCIceCandidate);
window.RTCPeerConnection = (window.RTCPeerConnection    ||
                            window.mozRTCPeerConnection ||
                            window.webkitRTCPeerConnection);

var signalConnection = null;

function connectSignalConnection() {
    //connecting to our signaling server
    socketAddress = "wss://" + window.location.host + "/ws/"
    console.log(socketAddress)

    signalConnection = new WebSocket(socketAddress);

    updateAppStatus("app", "waiting for socket");

    signalConnection.onopen = function () {
        console.log("Connected to the signaling server");
        updateAppStatus("socket", "connected");
    };

    signalConnection.onclose = function () {
        console.log("Signaling Connection Closed");
        updateAppStatus("socket", "closed");
        updateAppStatus("socketConnected", false);
    };

    //handle message from signaling server
    signalConnection.onmessage = function (msg) {
        console.log("Got message", msg.data);

        var data = JSON.parse(msg.data);

        switch(data.type) {
            case "hello":
                updateAppStatus("socketConnected", true);
                updateAppStatus("socket", "ready");
                updateAppStatus("app", "waiting for login");
                loginBtn.disabled = false;
                break;
            case "login":
                handleLogin(data.success);
                break;
            //when somebody wants to call us
            case "offer":
                handleOffer(data.offer, data.name);
                break;
            case "answer":
                handleAnswer(data.answer);
                break;
            //when a remote peer sends an ice candidate to us
            case "candidate":
                handleCandidate(data.candidate);
                break;
            case "leave":
                handleLeave();
                break;
            case "userAvailable":
                userAvailableResponse = data.available;
                break;
            default:
                break;
        }
    };

    signalConnection.onerror = function (err) {
        console.log("Got error", err);
        updateAppStatus("socket", "error");
        // if not connected error is most likely because server isn't running try reconnecting
        if (!appStatus["socketConnected"]) {
            console.log("Reconnect in 1sec")
            updateAppStatus("app", "socket reconnect");
            setTimeout(function () {connectSignalConnection();}, 1000);
        }
    };
}

function initPeerConnection() {
    peerConnection = new window.RTCPeerConnection();

    // setup stream listening
    peerConnection.addStream(stream);

    // when a remote user adds stream to the peer connection, we display it
    peerConnection.onaddstream = function (e) {
        remoteVideo.src = window.URL.createObjectURL(e.stream);
    };

    // setup ice handling
    peerConnection.onicecandidate = function (event) {
        if (event.candidate) {
            send({
                type: "candidate",
                candidate: event.candidate
            });
        }
    };
}

connectSignalConnection();

// send message json encoded
function send(message) {
    // if we are conencted attach name to message
    if(connectedUser) {
        message.name = connectedUser;
    }
    if(signalConnection) {
        signalConnection.send(JSON.stringify(message));
    }
    else {
        console.log("No signalConnection - couldn't send", message)
    }
};

callPage.style.display = "none";

// connect buttons
loginBtn.addEventListener("click", function (event) {
    // request local video and start peerConnection
    navigator.getUserMedia({ video: true, audio: true }, function (myStream) {
        stream = myStream;

        // show local stream
        localVideo.src = window.URL.createObjectURL(stream);

        initPeerConnection();

    }, function (error) {
            console.log(error);
    });

    name = usernameInput.value;
    if (name.length > 0) {
        send({
            type: "login",
            name: name
        });
    }
});

callBtn.addEventListener("click", function () {
    calleeName = calleeNameInput.value;
    if (calleeName.length > 0) {
        connectedUser = calleeName;

        // TODO move down so only displayed if connected
        remoteUsername.innerText = connectedUser;
        updateAppStatus("remoteUsername", connectedUser);
        updateAppStatus("app", "call active");
        callBtn.disabled = true;
        hangUpBtn.disabled = false;

        // create an offer
        peerConnection.createOffer(function (offer) {
            send({
                type: "offer",
                offer: offer
            });

            peerConnection.setLocalDescription(offer);
        }, function (error) {
            alert("Error when creating an offer");
        });
    }
});

hangUpBtn.addEventListener("click", function () {
    send({
        type: "leave"
    });
    handleLeave();
});

function handleLogin(success) {
    if (success === false) {
        alert("Username already taken");
    }
    else {
        loginPage.style.display = "none";
        callPage.style.display = "block";

        updateAppStatus("app", "ready for calls");
        callBtn.disabled = false;
        hangUpBtn.disabled = true;
        updateAppStatus("username", name);

        localUsername.innerText = name;
    }
};


// offer received
function handleOffer(offer, name) {
    connectedUser = name;
    updateAppStatus("remoteUsername", connectedUser);
    updateAppStatus("app", "call active");
    callBtn.disabled = true;
    hangUpBtn.disabled = false;
    remoteUsername.innerText = connectedUser;

    peerConnection.setRemoteDescription(new window.RTCSessionDescription(offer));

    //create an answer to an offer
    peerConnection.createAnswer(function (answer) {
        peerConnection.setLocalDescription(answer);

        send({
            type: "answer",
            answer: answer
        });

    }, function (error) {
        alert("Error when creating an answer");
    });
};

//when we got an answer from a remote user
function handleAnswer(answer) {
    peerConnection.setRemoteDescription(new window.RTCSessionDescription(answer));
};

//when we got an ice candidate from a remote user
function handleCandidate(candidate) {
    peerConnection.addIceCandidate(new window.RTCIceCandidate(candidate));
};

function handleLeave() {
    remoteUsername.innerText = "";
    updateAppStatus("remoteUsername", "");
    connectedUser = null;
    remoteVideo.src = null;

    peerConnection.close();
    peerConnection.onicecandidate = null;
    peerConnection.onaddstream = null;

    // recreate peer connection to receive new calls
    initPeerConnection();

    updateAppStatus("app", "ready for calls");
    callBtn.disabled = false;
    hangUpBtn.disabled = true;
};

function updateAppStatus(key, value) {
    appStatus[key] = value;

    statusString = ""
    separator = " --- "
    for (var key in appStatus) {
        statusString += key + ": " + appStatus[key] + separator;
    }
    // delete last separator
    statusBar.innerText = statusString.substring(0, statusString.length - separator.length);
}

// functions for automated interaction
function userAvailableRequest(name) {
    userAvailableResponse = null;
    send({
        type: "userAvailable",
        name: name
    });
}

function getUserAvailableResponse() {
    return userAvailableResponse;
}

function getAppStatus() {
    return appStatus;  // JSON.stringify(appStatus);
}

function requestRTCStats() {
    if (navigator.mozGetUserMedia) {
        try {
            peerConnection.getStats().then(function(stats) {
                console.log("requestsd stats arrived and stored");
                rtcStatList.push(stats);
            });
        }
        catch(e) {
            console.log(e);
        }
    }
    else {
        console.log("Currently only Firefox is supported");
    }
}

function promiseRTCStats() {
    return peerConnection.getStats();
}

function getRTCStats() {
    returnList = new Array();
    while(true) {
        element = rtcStatList.pop()
        if(element != null) {
            returnList.push(element);
        }
        else {
            break;
        }
    }
    return returnList;
}