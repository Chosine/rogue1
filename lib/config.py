"""
    Set up defaults and read sentinel.conf
"""
import sys
import os
from gobyte_config import GoByteConfig

default_sentinel_config = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '../sentinel.conf')
)
sentinel_config_file = os.environ.get('SENTINEL_CONFIG', default_sentinel_config)
sentinel_cfg = GoByteConfig.tokenize(sentinel_config_file)
sentinel_version = "1.5.0"


def get_gobyte_conf():
    if sys.platform == 'win32':
        gobyte_conf = os.path.join(os.getenv('APPDATA'), "GoByteCore/gobyte.conf")
    else:
        home = os.environ.get('HOME')

        gobyte_conf = os.path.join(home, ".gobytecore/gobyte.conf")
        if sys.platform == 'darwin':
            gobyte_conf = os.path.join(home, "Library/Application Support/GoByteCore/gobyte.conf")

    gobyte_conf = sentinel_cfg.get('gobyte_conf', gobyte_conf)

    return gobyte_conf


def get_network():
    return sentinel_cfg.get('network', 'mainnet')


def get_rpchost():
    return sentinel_cfg.get('rpchost', '127.0.0.1')


def sqlite_test_db_name(sqlite_file_path):
    (root, ext) = os.path.splitext(sqlite_file_path)
    test_sqlite_file_path = root + '_test' + ext
    return test_sqlite_file_path


def get_db_conn():
    import peewee
    env = os.environ.get('SENTINEL_ENV', 'production')

    # default values should be used unless you need a different config for development
    db_host = sentinel_cfg.get('db_host', '127.0.0.1')
    db_port = sentinel_cfg.get('db_port', None)
    db_name = sentinel_cfg.get('db_name', 'sentinel')
    db_user = sentinel_cfg.get('db_user', 'sentinel')
    db_password = sentinel_cfg.get('db_password', 'sentinel')
    db_charset = sentinel_cfg.get('db_charset', 'utf8mb4')
    db_driver = sentinel_cfg.get('db_driver', 'sqlite')

    if (env == 'test'):
        if db_driver == 'sqlite':
            db_name = sqlite_test_db_name(db_name)
        else:
            db_name = "%s_test" % db_name

    peewee_drivers = {
        'mysql': peewee.MySQLDatabase,
        'postgres': peewe