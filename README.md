### KCProxy

KCProxy is a small man-in-the-middle server designed for two purposes:

 1. Avoiding legal issues with hosting assets on [kcsrv](https://github.com/KancolleTool/kcsrv)
 2. Allowing easy manipulation of KanColle game files without messing around with anything else.
 

### Usage

 1. Copy config.example.py to config.py
 2. Change the server IP to the one you use.
 3. Enable/disable and configure redis caching.
 
If on a client, you'll need to tunnel Port 80 -> Port 7869 or which port you configured KCProxy to listen on, and open your web browser to http://127.0.0.1/?api_token=your_api_token.  
This token can be retrieved from something such as KC3 Kai, or manual extraction. This needs to be renewed every few hours, or you will get catbombs.  

If on a server, it's recommended to reverse proxy this app through nginx/apache2/lighttpd and have it only hit on `/kcs/` urls. This will proxy the assets, but not the API data.  

### Loading modified files

Any files you put into `modified_files` (by default) will be loaded instead of the DMM counterparts. For example, if you were to create `modified_files/kcs/resources/image/furniture/floor/001.png` and put your own floor texture in, the proxy would load it instead of loading the DMM version.

### Licence

MIT.