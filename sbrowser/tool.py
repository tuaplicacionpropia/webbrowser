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

#fullscreenshot a b c d
#len = 6
#args = ['/media/jmramoss/ALMACEN/pypi/webbrowser/sbrowser/tool.py', 'fullscreenshot', 'a', 'b', 'c', 'd']

def main():
  #print("len = " + str(len(sys.argv)))
  #print("args = " + str(sys.argv))
  args = []
  for i in range(2, len(sys.argv)):
    args.append(sys.argv[i])

  getattr(sys.modules[__name__], sys.argv[1])(args)

def fullscreenshot (args):
  print("executing fullscreenshot " + str(args))
  url = args[0]
  target = None if len(args) > 1 else args[1]
  browser = sbrowser.Browser()
  browser.openUrl(url).maximize()
  browser.fullscreenshot(target)
  pass

def screenshot (args):
  print("executing screenshot " + str(args))
  pass

if __name__ == '__main__':
    main()
