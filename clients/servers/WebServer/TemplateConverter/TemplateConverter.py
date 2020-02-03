#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import argparse
from bs4 import BeautifulSoup
import json
import os
import shutil
import sys


class TemplateConverter(object):
    def __init__(self, input_dir, output_dir, config_file, force=False):
        print("__init__()")
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._force = force

        config_file = open(config_file, 'r')
        self._config = json.load(config_file)

    def run(self):
        print("run()")

        # check if input exists
        if not os.path.exists(self._input_dir):
            print("{} not existing - nothing to convert".format(self._input_dir))
            sys.exit(1)

        if os.path.exists(self._output_dir):
            if self._force:
                print("{} already exists - removing it".format(self._output_dir))
                shutil.rmtree(self._output_dir)
            else:
                print("{} already exists - use -f/--force to overwrite it".format(self._output_dir))
                sys.exit(1)

        # copy all files
        shutil.copytree(self._input_dir, self._output_dir)

        # processing files
        for root, dirs, files in os.walk(self._output_dir):
            path = root.split(os.sep)
            #print(root, path, dirs, files)
            #print((len(path) - 1) * '---', os.path.basename(root))
            for file in files:
                #print(len(path) * '---', file)
                filepath = "{}/{}".format(root, file)
                self._process_file(filepath=filepath)

    def _process_file(self, filepath):
        print("_process_file()")
        extension_list = ["html", "htm"]

        # TODO use MIME-Type?
        extension = filepath.split('.')[-1].lower()
        print("File: {} - Extension: {}".format(filepath, extension))
        if not extension in extension_list:
            print("skipping file")
            return

        print("processing %s" % (filepath))

        parser = "html.parser"

        f = open(filepath, 'r')
        data = f.read()
        f.close()

        soup = BeautifulSoup(data, parser)

        # TODO
        # add filter attribute link href filter rel=stylesheet

        print("")
        for category in self._config["categories"]:
            search_tags = self._config["categories"][category]
            for entry in search_tags:
                search_tag = entry["tag"]
                attribute = entry["attribute"]
                print("processing tag {}:".format(search_tag))
                tags = soup.findAll(search_tag)
                print("found {}".format(tags))
                for tag in tags:
                    resource_path = tag[attribute]
                    resource_path = self._generate_resource_path(resource_path=resource_path, category=category, filepath=filepath)
                    tag[attribute] = resource_path

        print("")

        data = str(soup)  # preserves lines a bit better
        data = soup.prettify()  # pretty version

        f = open(filepath, 'w')
        f.write(data)
        f.close()


    def _generate_resource_path(self, resource_path, category, filepath):
        print("_generate_resource_path()")
        print("generating new path for {} (category {}, filepath {})".format(resource_path, category, filepath))

        if resource_path.startswith("http"):
            # leave external link
            return resource_path

        server_url = self._categroy_server(category=category)

        resource_path = server_url + resource_path

        return resource_path

    def _categroy_server(self, category):
        print("_categroy_server()")
        print("server url for category {}".format(category))
        servers = [server["url"] for server in self._config["servers"] if category in server["categories"]]

        if len(servers) > 0:
            server = servers[0]

            if not (server.startswith("http://") or server.startswith("https://")):
                server = "http://{}".format(server)

            if not server.endswith('/'):
                server = server + '/'

            return server
        else:
            return None


if __name__ == "__main__":
    # parse args
    description = ("TemplateConverter parameter")

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-c", "--config", help="Config file", dest="config_file", required=True)
    parser.add_argument("-f", "--force", help="Force output replacement", dest="force", action="store_true")
    parser.add_argument("-i", "--input", help="Input directory to be converted", dest="input_dir", required=True)
    parser.add_argument("-o", "--output", help="Output directory for converted files", dest="output_dir", required=True)

    args = vars(parser.parse_args())

    converter = TemplateConverter(**args)
    converter.run()
