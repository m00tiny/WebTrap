import argparse
import json
import logging
import logging.handlers
import os
import SimpleHTTPServer
import SocketServer

DEFAULT_SERVER_PORT = 80


def init_access_logs(log_file_path, syslog_hostname=None):
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    if syslog_hostname:
        syslog_handler = init_syslog_logger(syslog_hostname)
        logger.addHandler(syslog_handler)

    file_handler = init_rotating_file_handler(log_file_path)
    logger.addHandler(file_handler)
    return logger

def init_syslog_logger(hostname, port=514):
    return logging.handlers.SysLogHandler(
        address=(hostname, port))

def init_rotating_file_handler(log_file_path):
    path_to_log_file = os.path.abspath(log_file_path)
    log_file_directory_path = os.path.dirname(path_to_log_file)
    if not os.path.exists(log_file_directory_path):
        os.makedirs(log_file_directory_path)

    handler = logging.handlers.RotatingFileHandler(
        path_to_log_file, maxBytes=500000, backupCount=10)
    formatter = logging.Formatter(
        '%(asctime)s-[%(levelname)s]: %(message)s ')
    handler.setFormatter(formatter)
    return handler

class AlertingRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    extensions_map = SimpleHTTPServer.SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map.update({".php": "text/html"})

    def send_alert_to_syslog(self, additional_data=None):
        logging_data_format = "Access To: %s\nServer Forensics Data:%s"
        server_forensics_data = self.get_forensics_data_from_request()
        logging_data = logging_data_format % (
            self.path, server_forensics_data)

        if additional_data:
            logging_data += "\nAdditionalData:%s"
            logging_data = logging_data % (additional_data)

        alerts_logger = logging.getLogger(__name__)
        alerts_logger.info(logging_data)

    def get_forensics_data_from_request(self):
        forensics_report = {}
        forensics_report["client_address"] = self.address_string()
        forensics_report["command"] = str(self.command)
        forensics_report["path"] = self.path
        forensics_report["request_version"] = self.request_version
        forensics_report["headers"] = str(self.headers)
        forensics_report["protocol_version"] = self.protocol_version
        return json.dumps(forensics_report)

    def do_GET(self):
        self.send_alert_to_syslog()
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        # In addition to the regular alert data, we add to it the Post data
        post_data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_alert_to_syslog("PostData:" + post_data_string)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


def main(syslog_server, webroot_directory, log_file_path):
    if not os.path.isdir(webroot_directory):
        print "Error: %s web directory does not exist" % (webroot_directory)
        return

    alerts_logger = init_access_logs(log_file_path, syslog_hostname=syslog_server)
    alerts_logger.setLevel(logging.INFO)

    os.chdir(webroot_directory)
    trap_server = SocketServer.TCPServer(
        ("0.0.0.0", DEFAULT_SERVER_PORT), AlertingRequestHandler)

    print "Starting listening to http requests"
    trap_server.serve_forever()

if __name__ == '__main__':

    arguments_parser = argparse.ArgumentParser(prog=__file__)
    arguments_parser.add_argument("--webroot-directory", "-d", default="./webRoot", type=str,
                                  help="root directory for the HTTP server")
    arguments_parser.add_argument("--syslog-server", "-s", default=None,
                                  type=str,
                                  help="syslog server that the deceptive user will report the request to it")
    arguments_parser.add_argument("--log-file-path", "-l", default="./logs/trap_server_access.log",
                                  type=str, help="access log file path")

    parsed_arguments = arguments_parser.parse_args()
    main(parsed_arguments.syslog_server,
         parsed_arguments.webroot_directory,
         parsed_arguments.log_file_path)
