#!/usr/bin/env python
__author__ = 'Eric Sales'

INFO="""
    modconfig
        Modify a setting in a config or property file.
        It will overwrite the existing assignment or make an
        addition if the variable isn't found."""

USAGE="""
    USAGE: modconfig.py <file> <var> <new_setting>"""

EXAMPLE="""
    Example: modconfig.py common.properties java.var.update "changed setting"
"""


import fileinput
import sys
HelpOpts = ('-help','-h','--help','-?','?')


def ModConfig(File, Variable, Setting):
    """
    Modify Config file variable with new setting
    """
    VarFound = False
    AlreadySet = False
    V=str(Variable)
    S=str(Setting)
    # use quotes if setting has spaces #
    if ' ' in S:
        S = '"%s"' % S

    for line in fileinput.input(File, inplace = 1):
        # process lines that look like config settings #
        if not line.lstrip(' ').startswith('#') and '=' in line:
            _infile_var = str(line.split('=')[0].rstrip(' '))
            _infile_set = str(line.split(_infile_var+'=')[1].lstrip(' ').rstrip())
            # only change the first matching occurrence #
            if VarFound == False and _infile_var.rstrip(' ') == V:
                VarFound = True
                # don't change it if it is already set #
                if _infile_set.lstrip(' ') == S:
                    AlreadySet = True
                else:
                    line = "%s = %s\n" % (V, S)

        sys.stdout.write(line)


    # Append the variable if it wasn't found #
    if not VarFound:
        print "Variable '%s' not found.  Adding it to %s" % (V, File)
        with open(File, "a") as f:
            f.write("%s = %s\n" % (V, S))
    elif AlreadySet == True:
        print "Variable '%s' unchanged" % (V)
    else:
        print "Variable '%s' modified to '%s'" % (V, S)

    return


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] in HelpOpts:
        try:
            if sys.argv[1] not in HelpOpts:
                print "Invalid Usage.  Expecting 3 arguments."
        except IndexError:
            print "Invalid Usage.  Expecting 3 arguments."

        print USAGE
        print EXAMPLE
        sys.exit()

    ModConfig(sys.argv[1], sys.argv[2], sys.argv[3])
