import os

from starlette.config import Config
from starlette.datastructures import Secret

# Config values will be given from environment variables and/or ".env" file.
# Also note that if we dont provide configuration file, the defaults act as development environment.
config = Config(os.path.abspath(os.path.join(os.path.dirname(__file__), '.env')))


# for all other settings we first try to fetch them from etcd server. If not found/available
# we get them from project lvl environment variables.
config_x = config('config_x', cast=str, default='This is default for X')
config_y = config('config_y', cast=str, default='This is default for Y')

#DB_URL = config('DB_URL', cast=str, default='localhost')
#DB_USERNAME = config('DB_USERNAME', cast=str, default='postgres')
#DB_PASSWORD = config('DB_PASSWORD', cast=Secret, default='postgres')

AZURE_KEY = config('Ocp-Apim-Subscription-Key', cast=str, default='Not provided')