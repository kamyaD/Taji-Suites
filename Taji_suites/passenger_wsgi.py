import os
import sys   # ✅ THIS LINE WAS MISSING

# 🔹 Project root (where manage.py is)
project_home = "/home/ttdfvdip/public_html/Taji_suites"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 🔹 Inner Django project folder
project_inner = "/home/ttdfvdip/public_html/Taji_suites/taji"
if project_inner not in sys.path:
    sys.path.insert(0, project_inner)

# 🔹 Django settings
os.environ["DJANGO_SETTINGS_MODULE"] = "taji.settings"

# 🔹 PyMySQL fix
import pymysql
pymysql.install_as_MySQLdb()

# 🔹 WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()