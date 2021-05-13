import re
import statistics

import parsing.MyPerfectRequest
from data.Ekatalog_db import *
from data.Proxy_db import *
from data.Smartphones_db import *
from data.Pda_db import *

from parsing import Main, MyPerfectProxy, MyPerfectRequest

p = Main.Pda()

p.total_parsing()
