"""The main CLI for ioc."""
import locale
import os
import signal
import subprocess as su
import sys

import click
# This prevents it from getting in our way.
from click import core

import iocage.lib.ioc_check as ioc_check

core._verify_python3_env = lambda: None
user_locale = os.environ.get("LANG", "en_US.UTF-8")
locale.setlocale(locale.LC_ALL, user_locale)

# @formatter:off
# Sometimes SIGINT won't be installed.
# http://stackoverflow.com/questions/40775054/capturing-sigint-using-keyboardinterrupt-exception-works-in-terminal-not-in-scr/40785230#40785230
signal.signal(signal.SIGINT, signal.default_int_handler)
# @formatter:on

try:
    su.check_call(["sysctl", "vfs.zfs.version.spa"],
                  stdout=su.PIPE, stderr=su.PIPE)
except su.CalledProcessError:
    sys.exit("ZFS is required to use iocage.\n"
             "Try calling 'kldload zfs' as root.")


def print_version(ctx, param, value):
    """Prints the version and then exits."""
    if not value or ctx.resilient_parsing:
        return
    print("Version\t0.9.8 BETA")
    sys.exit()


cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          'cli'))


class IOCageCLI(click.MultiCommand):
    """
    Iterates in the 'cli' directory and will load any module's cli definition.
    """

    def list_commands(self, ctx):
        rv = []

        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
                    not filename.startswith('__init__'):
                rv.append(filename.rstrip(".py"))
        rv.sort()

        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"iocage.cli.{name}",
                             None, None, ["cli"])
            mod_name = mod.__name__.replace("iocage.cli.", "")

            try:
                if mod.__rootcmd__ and "--help" not in sys.argv[1:]:
                    if len(sys.argv) != 1:
                        if os.geteuid() != 0:
                            sys.exit("You need to have root privileges to"
                                     f" run {mod_name}")
            except AttributeError:
                # It's not a root required command.
                pass

            return mod.cli
        except (ImportError, AttributeError):
            return


@click.command(cls=IOCageCLI)
@click.option("--version", "-v", is_flag=True, callback=print_version,
              help="Display iocage's version and exit.")
def cli(version):
    """A jail manager."""
    skip_check = False
    skip_check_cmds = ["--help", "activate", "-v", "--version"]

    try:
        if "iocage" in sys.argv[0] and len(sys.argv) == 1:
            skip_check = True

        for arg in sys.argv[1:]:
            if arg in skip_check_cmds:
                skip_check = True
            elif "clean" in arg:
                skip_check = True
                ioc_check.IOCCheck(silent=True)

        if not skip_check:
            ioc_check.IOCCheck()
    except RuntimeError as err:
        exit(err)


if __name__ == '__main__':
    cli()
