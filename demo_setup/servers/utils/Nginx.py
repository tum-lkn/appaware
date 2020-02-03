#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import shlex
import subprocess
import tempfile

from . import Process


class Nginx(object):
    def __init__(self):
        self._config_dir = tempfile.TemporaryDirectory()
        self._config_dir_path = self._config_dir.name
        self._nginx_process = None
        self._nginx_conf = None
        self._ssl_cert = None
        self._ssl_key = None

    def start(self):
        cmd = "sudo nginx -c %s" % (self._nginx_conf)
        self._nginx_process = Process.Process(cmd=cmd)
        self._nginx_process.start()

    def stop(self):
        self._nginx_process.stop()

    def clean_up(self):
        self._config_dir.cleanup()

    def generate_config(self, servers, websockets=None):

        self._generate_ssl_certs()

        websocket_entries = []
        if websockets:
            for websocket in websockets:
                name = websocket["name"]
                url = websocket["url"]
                port = websocket["port"]
                websocket_entry = self._generate_websocket_entry(name=name, url=url, port=port)
                websocket_entries.append(websocket_entry)

        server_entries = []
        used_ports = []
        for server in servers:
            port = server.get("port", 80)

            if port in used_ports:
                # skip because port is already in use
                continue

            document_root = server.get("document_root", "/var/www")
            ssl = server.get("ssl", False)
            websocket = server.get("websocket", None)
            redirect = server.get("redirect", None)

            server_entry = self._generate_server_entry(port=port, document_root=document_root, ssl=ssl, websocket=websocket, redirect=redirect)
            server_entries.append(server_entry)

        nginx_conf = """
            user www-data;
            worker_processes auto;
            pid /run/nginx.pid;

            daemon off;

            events {
                worker_connections 768;
            }

            http {
                sendfile on;
                tcp_nopush on;
                tcp_nodelay on;
                keepalive_timeout 65;
                types_hash_max_size 2048;

                include /etc/nginx/mime.types;
                default_type application/octet-stream;

                ssl_prefer_server_ciphers on;

                access_log /var/log/nginx/access.log;
                error_log /var/log/nginx/error.log;

                gzip on;
                gzip_disable "msie6";

                include /etc/nginx/conf.d/*.conf;

                %s

                %s
            }
            """ % ("\n".join(websocket_entries), "\n".join(server_entries))

        self._nginx_conf = os.path.join(self._config_dir_path, "nginx.conf")

        nginx_conf_file = open(self._nginx_conf, 'w')
        nginx_conf_file.write(nginx_conf)
        nginx_conf_file.close()

    def _generate_ssl_certs(self):
        ssl_dir = os.path.join(self._config_dir_path, "ssl")
        os.makedirs(ssl_dir)

        self._ssl_cert = os.path.join(ssl_dir, "nginx.crt")
        self._ssl_key = os.path.join(ssl_dir, "nginx.key")

        cmd = 'openssl req -x509 -nodes -days 365 -newkey rsa:2048 -subj "/" -keyout %s -out %s' % (self._ssl_key, self._ssl_cert)
        cmd = shlex.split(cmd)

        ssl_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ssl_process.wait()

    def _generate_websocket_entry(self, name, url, port):
        entry = """
            upstream %s {
                server %s:%s;
            }
        """ % (name, url, port)
        return entry


    def _generate_server_entry(self, port, document_root, ssl=False, websocket=None, redirect=None):
        if ssl:
            listen = """
                listen %s ssl;
                listen [::]:%s ssl ipv6only=on;
            """ % (port, port)

            ssl_conf = """
            ssl_certificate %s;
            ssl_certificate_key %s;
            """ % (self._ssl_cert, self._ssl_key)
        else:
            listen = """
                listen %s default_server;
                listen [::]:%s default_server ipv6only=on;
            """ % (port, port)

            ssl_conf = ""

        if websocket:
            websocket_conf = ""
            for entry in websocket:
                location = entry["location"]
                proxy = entry["proxy"]

                conf = """
                    location %s {
                        proxy_pass http://%s;
                        proxy_http_version 1.1;
                        proxy_set_header Upgrade $http_upgrade;
                        proxy_set_header Connection "upgrade";
                    }
                """ % (location, proxy)

                websocket_conf += conf
        else:
            websocket_conf = ""

        entry = """
            server {
                %s

                root %s;
                index index.html index.htm;

                # Make site accessible from http://localhost/
                server_name localhost;

                %s

                location / {
                    try_files $uri $uri/ =404;
                    autoindex on;
                }

                %s
            }
        """ % (listen, document_root, ssl_conf, websocket_conf)

        return entry
