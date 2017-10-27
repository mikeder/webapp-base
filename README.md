## Webapp-Base

A tornado based core library for web applications.

### Current Features
* Asynchronous HTTP client
* Auto patching SQLite database
* Basic frontend with Bootstrap and Jquery



## TODO: Nice things to have in a core library
1) Cache interface that supports multiple back-end caching techs (Heap, Memcached, Redis).
2) Database interface that supports at least MySQL and SQLite with auto-patching.
3) Multiple web interfaces (web frontend, REST and Websocket API's)
4) Message queueing/consuming interface for multiprocessing and RabbitMQ/SQS etc.
5) Common logging interface with key=pair and json formatting.
6) Config loader that supports ini, json, yaml, etc.
