#!/usr/bin/env python
import os
import sys

PATH_APP='/usr/local/virttool'
if PATH_APP not in sys.path:
    sys.path.append(PATH_APP)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "virttool.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
