var ws = new WebSocket("ws://localhost:8001/ws");
ws.onopen = function() {
   ws.send("Hello, world");
};
ws.onmessage = function (evt) {
   while (alert(evt.data)) {
        ws.send("ping")
   };
   ws.send("closing..")
   ws.close();
};