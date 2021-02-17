# libreninja-server
Handshake server for Libreninja / OBS Ninja V6

This is a 3rd party handshake server for Libreninja or OBS Ninja V6. For Deployment, you need to proxy the connection through e.g. NGINX in order to handle SSL Encryption of the Websocket connection. It is important to set the Timeout time to large values, e.g. 1d. 

For Configuration of this Server, look inside config.py.

Packages required: AIOHTTP, the rest should be python built in packages, tested with Python 3.8
