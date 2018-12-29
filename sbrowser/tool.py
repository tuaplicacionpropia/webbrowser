r"""Command-line tool to cropfaces

Usage::

    $ cropfaces image.jpg NEAR

"""
import sys
from sbrowser import SvgManager
import pkg_resources  # part of setuptools

HELP="""text2img, the Human JSON.

Usage:
  webbrowser [options]
  webbrowser [options] <input>
  webbrowser (-h | --help)
  webbrowser (-V | --version)

Options:
  -h --help     Show this screen.
  -j            Output as formatted JSON.
  -c            Output as JSON.
  -V --version  Show version.
""";

def showerr(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")

def main():
    args = []
    for arg in sys.argv[1:]:
        if arg == '-h' or arg == '--help':
            showerr(HELP)
            return
        elif arg == '-j': format = 'json'
        elif arg == '-c': format = 'compact'
        elif arg == '-V' or arg == '--version':
            showerr('Hjson ' + pkg_resources.require("Hjson")[0].version)
            return

        elif arg[0] == '-':
            showerr(HELP)
            raise SystemExit('unknown option ' + arg)
        else:
            args.append(arg)

    SvgManager.generate(sys.argv)

if __name__ == '__main__':
    main()
