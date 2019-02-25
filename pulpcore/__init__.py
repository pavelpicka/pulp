import os
from dynaconf.contrib import django_dynaconf
from django.conf import settings

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)


if django_dynaconf.settings.get('MEDIA_ROOT') == '':
    media_root = '/var/lib/pulp'
else:
    media_root = django_dynaconf.settings.get('MEDIA_ROOT')

settings.__setattr__('MEDIA_ROOT', media_root)
settings.__setattr__('WORKING_DIRECTORY', os.path.join(media_root, 'tmp/'))
settings.__setattr__('FILE_UPLOAD_TEMP_DIR', os.path.join(media_root, 'tmp/'))
django_dynaconf.settings.__setattr__('WORKING_DIRECTORY', os.path.join(media_root, 'tmp/'))

# import pydevd
# pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

if not django_dynaconf.settings.get('STATIC_ROOT'):
    django_dynaconf.settings.set('STATIC_ROOT', os.path.join(media_root, 'static/'))
    settings.__setattr__('STATIC_ROOT', os.path.join(media_root, 'static/'))

