from .common_settings import *

DEBUG = True
SECRET_KEY = 'r1j)cm&vk-ayki44_x0-xc)tc&$g839-xo(njbl7x7grl=4mdm'

DATABASES['default'].update({
    'NAME': 'djtest',
    'USER': 'djuser',
    'PASSWORD': 'djrules',
    'HOST': 'localhost',
    'PORT': '5432'
})

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
