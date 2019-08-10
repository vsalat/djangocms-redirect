#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import sys
from tempfile import mkdtemp

HELPER_SETTINGS = dict(
    INSTALLED_APPS=[
        'djangocms_redirect',
    ],
    FILE_UPLOAD_TEMP_DIR=mkdtemp(),

    MIDDLEWARE_CLASSES=[
        'djangocms_redirect.middleware.RedirectMiddleware',
    ],
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)


def run():
    from app_helper import runner
    runner.cms('djangocms_redirect')


def setup():
    from app_helper import runner
    runner.setup('djangocms_redirect', sys.modules[__name__], use_cms=True)


if __name__ == '__main__':
    run()

if __name__ == 'cms_helper':
    # this is needed to run cms_helper in pycharm
    setup()
