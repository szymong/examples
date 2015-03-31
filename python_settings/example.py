#!/usr/bin/env python

import sys
import argparse
import ConfigParser

import logging
logger = logging.getLogger("example")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s : %(lineno)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class Options:

    def __init__(self, args):
        self.parser = argparse.ArgumentParser(description="Example script.")
        self.args = args

        self.parser.add_argument("--create-config",
                                 dest="create_config",
                                 help="Create configuration file with default values")

        self.parser.add_argument("--config",
                                 dest="config",
                                 default="/tmp/example.cfg",
                                 help="Path to example.cfg")

        self.parser.add_argument("--repo-branch",
                                 dest="repo_branch",
                                 default="something",
                                 help="git branch OR git tag from which to build")

        self.options = self.parser.parse_args()
        print "repo-branch from command line is: {}".format(self.options.repo_branch)

        # Here comes the next about 20 arguments

    def get_options(self):
        return self.options

    def get_parser(self):
        return self.parser

class UpgradeService():

    def __init__(self, options):
        if not options:
            exit(1)
        self.options = options
        if self.options.config:
            self.config_path = self.options.config
            self.init_config_file()
        self.init_options()

    def init_config_file(self):
        """ This function is to process the values provided in the config file """

        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.config_path)

        self.repo_branch = self.config.get('example', 'repo-branch')

        # HERE COMES OVER 20 LINES LIKE THE ABOVE

        print "repo-branch from config is: {}".format(self.repo_branch)

    def init_options(self):
        """ This function is to process the command line options.
            Command line options always override the values given in the config file.
        """
        if self.options.repo_branch:
            self.repo_branch = self.options.repo_branch

        # HERE COMES OVER 20 LINES LIKE THE TWO ABOVE

    def run(self):
        pass

if __name__ == "__main__":
    options = Options(sys.argv).get_options()
    upgrade_service = UpgradeService(options)

    print "repo-branch value to be used is: {}".format(upgrade_service.repo_branch)
    upgrade_service.run()

