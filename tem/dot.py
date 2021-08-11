import sys, os, argparse
from . import cli, util
from .util import print_cli_err, print_cli_warn, print_err

def setup_common_parser(parser):
    """
    Setup ``parser`` in a way that is common to all subcommands derived from
    `dot`.
    """
    parser.add_argument(
        'files', metavar='FILES', nargs='*', default=[],
        help='files to operate on')

    # Action options
    action_opts = parser.add_argument_group('action options')
    action_opts_ex = action_opts.add_mutually_exclusive_group()
    action_opts_ex.add_argument(
        '-x', '--exec', action='store_true', help='execute FILES (default)')
    action_opts_ex.add_argument(
        '-n', '--new', action='store_true',
        help='create new empty FILES')
    action_opts_ex.add_argument(
        '-a', '--add', action='store_true',
        help='copy FILES')
    action_opts_ex.add_argument(
        '-D', '--delete', action='store_true',
        help='delete FILES')
    action_opts.add_argument(
        '-l', '--list', action='store_true',
        help='list matching FILES')
    cli.add_edit_options(action_opts)

    # Modifier options
    modifier_opts = parser.add_argument_group('modifier options')
    modifier_opts.add_argument('-t', '--template',
                               help='use TEMPLATE as root directory')
    modifier_opts.add_argument('--root', metavar='DIR',
                               help='override root directory with DIR')
    modifier_opts.add_argument('-v', '--verbose', action='store_true',
                               help='report successful and unsuccessful runs')
    modifier_opts.add_argument('-f', '--force', action='store_true',
                               help="perform action disregarding warnings")
    modifier_opts.add_argument('-r', '--recursive', action='store_true',
                               help='recurse up the directory tree')
    modifier_opts.add_argument('-I', '--ignore', metavar='FILE', default=[],
                               help='ignore FILE')

    cli.add_general_options(parser)

    return action_opts, modifier_opts

def setup_parser(subparsers):
    p = subparsers.add_parser('dot', add_help=False)
    action_opts, modifier_opts = setup_common_parser(p)

    modifier_opts.add_argument('--subdir', metavar='SUB',
                               help='subdirectory under .tem/ to use')

    p.set_defaults(func=cmd)

def validate_file_arguments_as_script_names(files):
    any_invalid_files = False
    for file in files:
        if '/' in file:
            print_cli_err("'{}' is an invalid script name".format(file))
            any_invalid_files = True
    if any_invalid_files: exit(1)

def validate_and_get_dotdir(subdir, rootdir=None, recursive=False):
    """
    Make sure that ``rootdir`` and ``subdir`` can form a valid dotdir, and then
    return them in a usable form. A dotdir is a path of the form
    `$rootdir/.tem/$subdir`.
    :param root: directory that contains the `.tem/` subdirectory of interest
    :param subdir: directory under `.tem/`
    :return: resolved ``(rootdir, subdir)`` pair
    .. note::

        If ``rootdir`` is ``None`` and ``recursive`` is ``True``, the filesystem
        is searched upwards until a directory containing `.tem/$subdir` is
        found.  That directory will be taken as the rootdir. If ``recursive`` is
        ``False``, cwd will be used as ``rootdir``.
    """
    if not subdir:
        print_cli_err("subdir must be non-empty")
        exit(1)

    if rootdir == None:
        # We have to look upwards for a suitable rootdir
        if recursive:
            cwd = os.getcwd()
            # Find a parent directory with a subdirectory tree as in `subdir`
            while True:
                if os.path.isdir(cwd + '/.tem/' + subdir):
                    # subdir exists under `cwd`
                    rootdir = cwd
                    break
                if cwd == '/':                              # dead end
                    print_cli_err("a valid root directory could not found")
                    exit(1)
                cwd = os.path.dirname(cwd)                  # Go up one directory
        else:
            rootdir = '.'
    elif not os.path.isdir(rootdir):                    # rootdir doesn't exist
        print_cli_err("'{}' is not a directory".format(rootdir))
        exit(1)
    dotdir = rootdir + '/.tem/' + subdir

    # Validation
    if not os.path.isdir(dotdir):
        if os.path.exists(dotdir):
            # TODO
            print_cli_err("'{}' exists and is not a directory"
                          .format(util.abspath(dotdir)))
            print_err('Try running `tem init --force`. Please read the manual before doing that.')
        else:
            print_cli_err("directory '{}' not found".format(dotdir))
            print_err('Try running `tem init` first.')
            exit(1)
        # TODO if args.exec or not args.force: exit(1)

    return rootdir, subdir

def cmd_common(args, subdir=None):
    """
    If this is called from a `dot` derivative subcommand, subdir and root
    must be specified as function arguments.
    """
    if subdir is None:
        subdir = args.subdir

    files = args.files

    if args.template:
        files += _paths_from_templates(args.template)
    rootdir, subdir = validate_and_get_dotdir(subdir, args.root, recursive=args.recursive)
    dotdir = rootdir + '/.tem/' + subdir

    # Exec is the default action if no other actions have been specified
    if not (args.new or args.add or args.edit or args.editor or args.list):
        args.exec = True

    dest_files = []

    if args.new:                                                        # --new
        validate_file_arguments_as_script_names(files)
        any_conflicts = False
        for file in files:
            dest = dotdir + '/' + file
            if not os.path.exists(dest):
                _create_executable_file(dest)
            elif args.force:
                _make_file_executable(dest)
            else:
                any_conflicts = True
                print_cli_err("file '{}' already exists".format(dest))
            dest_files.append(dest)
        if any_conflicts:
            print_err('\nTry running with --force.')
            exit(1)
    elif args.add:                                                      # --add
        import shutil
        any_nonexisting = False
        any_conflicts = False
        dest_files = []
        for src in files:
            dest = dotdir + '/' + util.basename(src)
            if os.path.exists(src):
                if not os.path.exists(dest) or args.force:
                    shutil.copy(src, dest)
                else:
                    print_cli_warn("file '{}' already exists".format(dest))
                    any_conflicts = True
            else:
                print_cli_warn("file '{}' does not exist".format(src))
                any_nonexisting = True
            dest_files.append(dest)
        if any_nonexisting or any_conflicts:
            exit(1)
    elif args.delete:                                                # --delete
        any_problems = False
        for file in files:
            target_file = dotdir + '/' + file
            if os.path.isfile(target_file):
                os.remove(target_file)
            elif os.path.isdir(target_file):
                print_cli_warn("'{}' is a directory".format(target_file))
            else:
                print_cli_warn("'{}' does not exist".format(target_file))
        if any_problems:
            exit(1)
    else:
        # If no files are passed as arguments, use all files from the dotdir
        if not files:
            files = [ file for file in os.listdir(dotdir)
                     if file not in args.ignore ]
        if not files:
            if args.verbose:
                print_cli_err('no scripts found')
                exit(1)
        elif args.edit or args.editor:
            cli.try_open_in_editor([ (dotdir + '/' + f) for f in files ],
                                   args.editor)
            exit(0)
        elif args.exec:
            # Add .tem/path/ to the PATH env
            os.environ['PATH'] = util.abspath(rootdir) + '/.tem/path:' \
                + os.environ['PATH']
            for file in files:
                if os.path.isdir(dotdir + '/' + file):
                    continue
                if args.edit or args.editor:
                    cli.try_open_in_editor(files, args.editor)
                try:
                    import subprocess
                    subprocess.run(dotdir + '/' + file)
                    if args.verbose:
                        print_err("tem: info: script `{}` was run successfully"
                                  .format(file))
                except:
                    print_cli_err("script `{}` could not be run"
                                  .format(file))
                    exit(1)

    if dest_files and (args.edit or args.editor):           # --edit, --editor
        cli.try_open_in_editor(dest_files, args.editor)

    if args.list:                                                       # --list
        import subprocess; from . import ext
        ls_args = [ 'ls', '-1' ]
        os.chdir(dotdir)
        # Without --new and --add options, only display files from `files`.
        # With --new or --add options, all files will be displayed.
        if not args.new and not args.add:
            ls_args += files
        p = ext.run(ls_args, encoding='utf-8')
        exit(p.returncode)

    # TODO:
    # --add: handle multiple files with same name

# Local helper functions

@cli.subcommand_routine('dot')
def cmd(*args, **kwargs):
    return cmd_common(*args, **kwargs)

def _make_file_executable(path):
    """Equivalent to performing `chmod u+x` on ``path``."""
    os.chmod(path, os.stat(path).st_mode | 0o100)

def _create_executable_file(path):
    """Create a file with the executable permission set."""
    open(path, 'x').close()                                 # Create empty file
    _make_file_executable(path)                             # chmod u+x

# TODO will probably be removed in favor of a more universal approach
def _paths_from_templates(args):
    from .repo import find_template
    repos = cli.resolve_and_validate_repos(args.repo, cmd='')
    template_path = []
    for tmpl in args.template:
        template_path += find_template(tmpl, repos)
    if not template_path:
        print_cli_warn("template '{}' cannot be found".format(args.template))
    return template_path
