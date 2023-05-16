import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
    return True

def buildargs(args, **kw):
    return lib.buildargs(args, **kw)

def access(args, op, **kw):
    return True

def help(**kw):
    ttyio.echo("{f6}{var:optioncolor}[A]{var:labelcolor}dd")
    ttyio.echo("{var:optioncolor}[E]{var:labelcolor}dit")
    ttyio.echo("{var:optioncolor}[L]{var:labelcolor}ist")
    ttyio.echo("{var:optioncolor}[D]{var:labelcolor}elete")
    ttyio.echo("{f6}{var:optioncolor}[Q]{var:labelcolor}uit")
    return True    

def main(args, **kw):
    bbsengine.util.title("agora")
    
    help()

    done = False
    while not done:
        lib.setarea(args, "main level", help=True)
        choice = ttyio.inputchoice("{f6}{var:promptcolor}agora:{var:inputcolor} ", "AELDQ", "Q", help=help)
        if choice == "A":
            ttyio.echo("Add")
            bbsengine.module.runsubmodule(args, "agora.add")
        elif choice == "KEY_HELP":
            menu()
        elif choice == "Q":
            ttyio.echo("Quit")
            break    
    return True
