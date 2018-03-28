# WebTrap
This project is designed to create deceptive webpages to deceive and redirect attackers away from real websites.
The deceptive webpages are generated by cloning real websites, specifically their login pages.
For further reading material on the tool development, please visit our [blog](https://blog.illusivenetworks.com/phishing-the-phishers-using-attackers-own-tools-to-combat-apt-style-attacks).

## Getting Started
The project is composed of two tools:
* Web Cloner - Responsible for cloning real websites and creating the deceptive web pag.e
* Deceptive Web server - Responsible for serving the cloned webpages, and reporting to a syslog server upon requests

## Operating System
The project was designed and tested on an Ubuntu 16.04 machine

## Prerequisites
```
pip install requests
apt install gir1.2-webkit2-3.0 python-gi python-gi-cairo python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

## How to use
### How to use the Web Cloner
```
usage: WebCloner.py [-h] [-o OUTPUT_DIRECTORY] website_url

positional arguments:
  website_url           The URL path to the web page you desire to clone

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Setting the output directory for the cloned webpage
```
### How to run the Deceptive web server
```
usage: TrapServer.py [-h] [--webroot-directory WEBROOT_DIRECTORY]
                     [--syslog-server SYSLOG_SERVER]
                     [--log-file-path LOG_FILE_PATH]

optional arguments:
  -h, --help            show this help message and exit
  --webroot-directory WEBROOT_DIRECTORY, -d WEBROOT_DIRECTORY
                        root directory for the HTTP server
  --syslog-server SYSLOG_SERVER, -s SYSLOG_SERVER
                        syslog server that the deceptive user will report the
                        request to it
  --log-file-path LOG_FILE_PATH, -l LOG_FILE_PATH
                        access log file path
```
## Examples
### Cloning Wikipedia login page
```
python ./WebCloner.py -o ~/WikiPediaLoginPage/ https://en.wikipedia.org/w/index.php?title=Special:UserLogin
```
### Running deceptive web server
```
sudo python ./TrapServer.py -d ~/WikiPediaLoginPage/ -s <SYSLOG_SERVER>
```
## Authors

* **Dolev Ben Shushan**

## License

This project is licensed under the  BSD 3-clause license - see the [LICENSE](LICENSE) file for details

## Thanks

* [@king-phisher](https://github.com/securestate/king-phisher) project for the initial web_cloner
* [@Session.js](https://github.com/codejoust/session.js) project for the client side data collection
