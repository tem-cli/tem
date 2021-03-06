"""tem config subcommand"""
import os
import sys
from io import StringIO

from .. import config, util
from . import common as cli


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    parser.add_argument(
        "-f",
        "--file",
        action="append",
        default=[],
        help="used config file (can be specified multiple times",
    )
    parser.add_argument(
        "-g",
        "--global",
        dest="glob",
        action="store_true",
        help="global configuration file will be used",
    )
    parser.add_argument(
        "-s",
        "--system",
        action="store_true",
        help="system configuration file will be used",
    )
    parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        help="local repository configuration file will be used",
    )
    cli.add_edit_options(parser)
    parser.add_argument(
        "-i",
        "--instance",
        action="store_true",
        help="print OPTIONs that are active in the running instance",
    )

    parser.add_argument(
        "option",
        metavar="OPTION",
        nargs="?",
        help="configuration option to get or set",
    )
    parser.add_argument(
        "value",
        metavar="VALUE",
        nargs="*",
        help="value for the specified configuration OPTION",
    )
    cli.add_general_options(parser)


def determine_config_files_from_args(args):
    """Determine all the config files this subcommand should operate on."""
    files = []
    local_config = "./.tem/config"
    if args.file:
        files += args.file
    if args.local or not (
        args.instance or args.glob or args.system or args.file
    ):
        files.append(local_config)
    if args.glob:
        files.append(os.path.expanduser("~/.config/tem/config"))
    if args.system:
        files += config.SYSTEM_PATHS
    return files


# TODO use this function as standard, especially in this module
def write_config(config_file):
    """Write instance configuration to ``config_file``

    On error, print a standard error message to stderr.
    """

    with open(config_file, "w", encoding="utf-8") as file_object:
        try:
            config.cfg.write(file_object)
        except Exception as e:
            cli.print_exception_message(e)
            sys.exit(1)


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    files = determine_config_files_from_args(args)

    if args.edit or args.editor:
        p = cli.edit_files(files, override_editor=args.editor)
        sys.exit(p.returncode)
    elif args.option:  # A config option was specified
        # Form value by concatenating arguments
        value = " ".join(args.value) if args.value else ""
        # Write the configuration to all config files
        for file in files:
            # Parse the file's original contents
            cfg = config.Parser(file)
            # Set the option's value to the one specified
            cfg[args.option] = value
            if not os.path.exists(os.path.dirname(file)):
                os.makedirs(os.path.dirname(file))
            # Write the changes
            with open(file, "w", encoding="utf-8") as file_object:
                cfg.write(file_object)
    else:  # No config options were specified
        # We add an imaginary file that contains all the configuration that has
        # been loaded into this instance of the program
        if args.instance:
            files.insert(0, None)
        for file in files:
            if file and not os.path.isfile(file):
                print(
                    "warning: file " + file + " does not exist",
                    file=sys.stderr,
                )
            else:
                if file:
                    cfg = config.Parser(file)
                    fname = util.shortpath(file)
                else:
                    cfg = config.cfg
                    fname = "ACTIVE INSTANCE"
                print("\033[1;4m" + fname + ":" + "\033[0m", file=sys.stderr)

                stream = StringIO()
                cfg.write(stream)
                print(
                    "    ", *stream.getvalue().split("\n")[:-1], sep="\n    "
                )
