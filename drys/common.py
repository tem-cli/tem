import sys, os, shutil
import re
import argparse
import configparser

repos = [ os.path.expanduser('~/.local/share/drys/repo') ]

default_config_paths = [
    '/usr/share/drys/config',
    os.path.expanduser('~/.config/drys/config'),
    os.path.expanduser('~/.drysconfig')
]

aliases = {}

cfg = configparser.ConfigParser()

def print_error_from_exception(e):
    print('error:', re.sub(r'^\[Errno [0-9]*\] ', '', str(e)), file=sys.stderr)

def copy(src, dest):
    try:
        if os.path.isdir(src):
            return shutil.copytree(src, dest,
                            dirs_exist_ok=True, copy_function=copy)
        else:
            return shutil.copy(src, dest)
    except Exception as e:
        print_error_from_exception(e)

def move(src, dest):
    try:
        return shutil.move(src, dest)
    except Exception as e:
        print_error_from_exception(e)

def add_common_options(parser):
    """
    Add options that are common among various commands. By default, when a
    subcommand is called, all options that are defined for the main command are
    valid but they must be specified before the subcommand name. By using this
    function with each subcommand, the option can be specified after the
    subcommand name.
    """
    parser.add_argument('-c', '--config', metavar='FILE',
                        action='append', default=[],
                        help='Use the specified configuration file')

def load_config(paths=[]):
    """
    Load configuration from the specified `paths`. If no paths are specified
    the configuration is only read from the standard paths as specified in `man
    drys-conf`. If no configuration file can be found
    """
    global cfg, aliases
    successful = cfg.read(default_config_paths + paths)

    if not successful:              # No config file could be read
        print('Warning: No configuration file on the system could be read.',
              'Please check if they exist or if their permissions are wrong.',
              file=sys.stderr, sep='\n')
    else:
        failed = set(paths) - set(successful)
        if failed:                  # None of the specified paths could be read
            print("ERROR: The following configuration files could not be read:",
                  end='\n\t', file=sys.stderr)
            print(*failed, sep='\n\t', file=sys.stderr)
            quit(1)
    #aliases = dict(config.get('alias', fallback={}))

def existing_file(path):
    """ Type check for ArgumentParser """
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(path + ' does not exist')
    else:
        return path

def add_repo(repo):
    repos.append(repo)
