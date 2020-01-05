import os
import etcd3

VERSION = '1.4.5'
MODULE = 'image_processor'
API_VERSION = 'v1'
PREFIX = f'/api/{API_VERSION}'

ETCD_HOST_URL = os.environ.get('ETCD_HOST_URL', 'etcd')
ETCD_HOST_PORT = os.environ.get('ETCD_HOST_PORT', '2379')


try:
    etcd = etcd3.client(host=ETCD_HOST_URL, port=ETCD_HOST_PORT)
    etcd.status()
except etcd3.exceptions.ConnectionFailedError:
    # Raise warning that etcd connection failed.
    pass
else:
    # on initial setup populate environment variables from config server.
    for value, metadata in etcd.get_range(range_start=f'/{__name__}/', range_end=f'/{__name__}0'):
        key, value = metadata.key.decode('utf-8'), value.decode('utf-8')
        config_var_name = os.path.basename(key)
        os.environ[config_var_name] = value

    # this import must be after we set environment variables from the etcd.
    from image_processor import settings

    def etcd_watch_callback(event):
        etcd_key, etcd_value = event.key.decode('utf-8'), event.value.decode('utf-8')
        # zamiži na eno oko in pojdi naprej.
        settings.__dict__[os.path.basename(etcd_key)] = etcd_value

    etcd.add_watch_callback(key=f'/{__name__}/', range_end=f'/{__name__}0', callback=etcd_watch_callback)

from .main import app
