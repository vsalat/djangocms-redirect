# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.test.utils import override_settings
from djangocms_redirect.models import Redirect

from .base import BaseRedirectTest


class TestRedirect(BaseRedirectTest):

    _pages_data = (
        {'en': {'title': 'home page', 'template': 'page.html', 'publish': True}},
        {'en': {'title': 'test page', 'template': 'page.html', 'publish': True}},
    )

    def test_301_redirect(self):
        pages = self.get_pages()

        redirect = Redirect.objects.create(
            site=self.site_1,
            old_path=pages[1].get_absolute_url(),
            new_path=pages[0].get_absolute_url(),
            response_code='301',
        )

        response = self.client.get(pages[1].get_absolute_url())
        self.assertEqual(response.status_code, 301)
        self.assertRedirects(response, redirect.new_path, status_code=301)

    def test_302_redirect(self):
        pages = self.get_pages()

        redirect = Redirect.objects.create(
            site=self.site_1,
            old_path=pages[1].get_absolute_url(),
            new_path=pages[0].get_absolute_url(),
            response_code='302',
        )

        response = self.client.get(pages[1].get_absolute_url())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect.new_path, status_code=302)

    def test_querystring_redirect(self):
        pages = self.get_pages()

        redirect = Redirect.objects.create(
            site=self.site_1,
            old_path=pages[1].get_absolute_url(),
            new_path=pages[0].get_absolute_url(),
            response_code='302',
        )

        response = self.client.get(pages[1].get_absolute_url() + '?Some_query_param')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect.new_path + '?Some_query_param', status_code=302)

    def test_410_redirect(self):
        pages = self.get_pages()

        Redirect.objects.create(
            site=self.site_1,
            old_path=pages[1].get_absolute_url(),
            new_path=pages[0].get_absolute_url(),
            response_code='410',
        )

        response = self.client.get(pages[1].get_absolute_url())
        self.assertEqual(response.status_code, 410)

        Redirect.objects.create(
            site=self.site_1,
            old_path='/some-path/',
            response_code='302'
        )

        response2 = self.client.get('/some-path/')
        self.assertEqual(response2.status_code, 410)

    def test_use_response_404_only(self):
        pages = self.get_pages()

        with self.settings(DJANGOCMS_REDIRECT_USE_REQUEST=False):
            redirect = Redirect.objects.create(
                site=self.site_1,
                old_path=pages[1].get_absolute_url(),
                new_path=pages[0].get_absolute_url(),
                response_code='302',
            )

            response = self.client.get(pages[1].get_absolute_url())
            self.assertEqual(response.status_code, 200)

    def test_use_response_no404(self):
        pages = self.get_pages()

        with self.settings(DJANGOCMS_REDIRECT_USE_REQUEST=False, DJANGOCMS_REDIRECT_404_ONLY=False):
            redirect = Redirect.objects.create(
                site=self.site_1,
                old_path=pages[1].get_absolute_url(),
                new_path=pages[0].get_absolute_url(),
                response_code='302',
            )

            response = self.client.get(pages[1].get_absolute_url())
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, redirect.new_path, status_code=302)

    def test_delete_redirect(self):
        pages = self.get_pages()

        redirect = Redirect.objects.create(
            site=self.site_1,
            old_path=pages[1].get_absolute_url(),
            new_path=pages[0].get_absolute_url(),
            response_code='301',
        )

        response = self.client.get(pages[1].get_absolute_url())
        self.assertRedirects(response, redirect.new_path, status_code=301)
        redirect.delete()
        response2 = self.client.get(pages[1].get_absolute_url())
        self.assertEqual(response2.status_code, 200)

    def test_redirect_no_append_slash(self):
        pages = self.get_pages()

        with override_settings(APPEND_SLASH=False):
            redirect = Redirect.objects.create(
                site=self.site_1,
                old_path=pages[1].get_absolute_url(),
                new_path=pages[0].get_absolute_url(),
                response_code='301',
            )

            response = self.client.get(pages[1].get_absolute_url().rstrip('/'))
            self.assertRedirects(response, redirect.new_path, status_code=301)


try:
    import memcache
except ImportError:
    pass
else:
    @override_settings(
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': '127.0.0.1:11211',
            }
        }
    )
    class TestMemcacheRedirect(TestRedirect):

        def test_fix_memcache_MemcachedKeyLengthError(self):
            """
            Fixes https://github.com/nephila/djangocms-redirect/issues/8
            Using an url > 250 chars with memcache active, a memcache.Client.MemcachedKeyLengthError is raised
            """
            pages = self.get_pages()
            url_suffix = 'x' * 250  # url > 250 chars

            url = '{}?{}'.format(
                pages[1].get_absolute_url(),
                url_suffix
            )
            expected_url = '{}?{}'.format(
                pages[0].get_absolute_url(),
                url_suffix
            )

            Redirect.objects.create(
                site=self.site_1,
                old_path=pages[1].get_absolute_url(),
                new_path=pages[0].get_absolute_url(),
                response_code='302',
            )
            try:
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, expected_url, status_code=302)
            except memcache.Client.MemcachedKeyLengthError:
                self.fail("memcache.Client.MemcachedKeyLengthError raised")



