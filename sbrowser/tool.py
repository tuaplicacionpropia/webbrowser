r"""Command-line tool to cropfaces

Usage::

    $ cropfaces image.jpg NEAR

"""
import sys
import sbrowser
import pkg_resources  # part of setuptools

HELP="""sbrowser, automate web browser.

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
  print("len = " + str(len(sys.argv)))
  print("args = " + str(sys.argv))

  #getattr(sys.modules[__name__], sys.method_name)(*args)

def fullscreenshot (args):
  pass

def screenshot (args):
  pass

if __name__ == '__main__':
    main()
