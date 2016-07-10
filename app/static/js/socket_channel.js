$(function() {
    // Note that the path doesn't matter for routing; any WebSocket
    // connection gets bumped over to WebSocket consumers
    var socket = null
    connectSocket()

    function connectSocket () {
        socket = new WebSocket("ws://" + window.location.host + "/ssh/");
    }

    socket.onopen = function() {
    }

    socket.onmessage = function(sock_res) {
        $('#ws-content').append('<p>' 
        + '<span>' + (new Date()).toString().replace(/GMT.*$/,'') + '</span>' 
        + '<span>' + sock_res.data + ' </span>'
        + '</p>');
    }

    // 监听Socket的关闭
    socket.onclose = function(sock_res) { 
        console.log('Client notified socket has closed', sock_res); 
        connectSocket()
    }; 

    // 发送消息事件绑定
    $('#ws-enter').on('click', sendMsg);
    $('#ws-message').on('keyup', function (event) {
        if (event.keyCode == 13) {
            sendMsg()
        }
    });
    function sendMsg() {
        var message = $('#ws-message').val()
        socket.send(JSON.stringify({
            msg: message
        }));
        $('#ws-message').val('')
    }

    // autosave
    $('#ws-autosave').on('click', function (event) {
        var checkState = document.getElementById('ws-autosave').checked
        socket.send(JSON.stringify({
            msg: 'COMMAND --autosave ' + checkState
        }));
    });

});