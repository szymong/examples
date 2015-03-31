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

DEFAULT_VALUES = dict(
    config="/tmp/example.cfg",
    repo_branch="something",
)

COMMAND_LINE_ONLY_ARGS = ["create_config"]

class Options:

    def __init__(self, args):
        self.parser = argparse.ArgumentParser(description="Example script.")
        self.args = args

        self.parser.add_argument("--create-config",
                                 dest="create_config",
                                 help="Create configuration file with default values")

        self.parser.add_argument("--config",
                                 dest="config",
                                 help="Path to example.cfg")

        self.parser.add_argument("--repo-branch",
                                 dest="repo_branch",
                                 help="git branch OR git tag from which to build")

        self.options = self.parser.parse_args()
        print "repo-branch from command line is: {}".format(self.options.repo_branch)

        # Here comes the next about 20 arguments

    def get_options(self):
        return self.options

    def get_parser(self):
        return self.parser

def parse_args():
    """ Parses the command line arguments, and returns dictionary with all of them.

    The arguments have dashes in the names, but they are stored in fields with underscores.

    :return: arguments
    :rtype: dictionary
    """
    options = Options(sys.argv).get_options()
    result = options.__dict__
    logger.debug("COMMAND LINE OPTIONS: {}".format(result))

    if options.create_config:
        logger.info("Creating configuration file at: {}".format(options.create_config))
        with open(options.create_config, "w") as c:
            c.write("[{}]\n".format("example"))
            for key in sorted(DEFAULT_VALUES.keys()):
                value = DEFAULT_VALUES[key]
                c.write("{}={}\n".format(key, value or ""))
        exit(0)
    return result

CONFIG_SECTION_NAME = "example"
def read_config(fname, section_name=CONFIG_SECTION_NAME):
    """ Reads a configuration file.

    Here the field names contain the dashes, in args parser we have underscores.
    So additionally I will convert the dashes to underscores here.

    :param fname: name of the config file
    :return: dictionary with the config file content
    :rtype: dictionary
    """
    config = ConfigParser.RawConfigParser()
    config.read(fname)

    result = {key.replace('-','_'):val for key, val in config.items(section_name)}
    logger.info("Read config file {}".format(fname))
    logger.debug("CONFIG FILE OPTIONS: {}".format(result))
    return result

def merge_options(first, second, default={}):
    """
    This function merges the first argument dictionary with the second.
    The second overrides the first.
    Then it merges the default with the already merged dictionary.

    This is needed, because if the user will set an option `a` in the config file,
    and will not provide the value in the command line options configuration,
    then the command line default value will override the config one.

    With the three-dictionary solution, the algorithm is:
    * get the default values
    * update with the values from the config file
    * update with the command line options, but only for the values
      which are not None (all not set command line options will have None)

    As it is easier and nicer to use the code like:
        options.path
    then:
        options['path']
    the merged dictionary is then converted into a namedtuple.

    :param first: first dictionary with options
    :param second: second dictionary with options
    :return: object with both dictionaries merged
    :rtype: namedtuple
    """
    from collections import namedtuple
    options = default
    options.update(first)
    options.update({key:val for key,val in second.items() if val is not None})
    logger.debug("MERGED OPTIONS: {}".format(options))
    return namedtuple('OptionsDict', options.keys())(**options)


def dict_difference(first, second, omit_keys=[]):
    """
    Calculates the difference between the keys of the two dictionaries,
    and returns a tuple with the differences.

    :param first:     the first dictionary to compare
    :param second:    the second dictionary to compare
    :param omit_keys: the keys which should be omitted,
                      as for example we know that it's fine that one dictionary
                      will have this key, and the other won't

    :return: The keys which are different between the two dictionaries.
    :rtype: tuple (first-second, second-first)
    """
    keys_first = set(first.keys())
    keys_second = set(second.keys())
    keys_f_s = keys_first - keys_second - set(omit_keys)
    keys_s_f = keys_second - keys_first - set(omit_keys)

    return (keys_f_s, keys_s_f)


def build_options():
    """
    Builds an object with the merged opions from the command line arguments,
    and the config file.

    If there is an option in command line which doesn't exist in the config file,
    then the command line default value will be used. That's fine, the script
    will just print an info about that.

    If there is an option in the config file, which doesn't exist in the command line,
    then it looks like an error. This time the script will show this as error information,
    and will exit.

    If there is the same option in the command line, and the config file,
    then the command line one overrides the config one.
    """

    options = parse_args()
    config = read_config(options['config'] or DEFAULT_VALUES['config'])

    (f, s) = dict_difference(options, config, COMMAND_LINE_ONLY_ARGS)
    if f:
        for o in f:
            logger.info("There is an option, which is missing in the config file,"
                        "that's fine, I will use the value: {}".format(DEFAULT_VALUES[o]))
    if s:
        logger.error("There are options, which are in the config file, but are not supported:")
        for o in s:
            logger.error(o)
        exit(2)

    merged_options = merge_options(config, options, DEFAULT_VALUES)
    return merged_options


class UpgradeService():

    def __init__(self, options):
        if not options:
            exit(1)
        self.options = options

    def run(self):
        pass

if __name__ == "__main__":
    options = build_options()
    upgrade_service = UpgradeService(options)

    print "repo-branch value to be used is: {}".format(upgrade_service.options.repo_branch)
    upgrade_service.run()

