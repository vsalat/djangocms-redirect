# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from app_helper.base_test import BaseTestCase
from django.core.cache import cache


class BaseRedirectTest(BaseTestCase):

    def setUp(self):
        super(BaseRedirectTest, self).setUp()
        cache.clear()
