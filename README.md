## py4web

py4web run apps --host 192.168.0.220 -P 3001

## py4web shell

(py4web) gregoryw@ubuntu2204:~/repos/py4web$ py4web shell apps
Python 3.10.12 (main, Jul 29 2024, 16:56:48) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from apps.wcg.models import db
>>> db.tables
['auth_user', 'auth_user_tag_groups', 'task_run', 'person', 'item', 'owner']
>>>

## from regular python shell

from py4web import *
from apps.myapp.models import db

Brings AssertionError