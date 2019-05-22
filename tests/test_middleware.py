# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.models import Page, Title
from django.contrib.sites.models import Site
from .base import BaseRedirectTest
from django.test.client import Client

from djangocms_redirect.models import Redirect


class TestRedirect(BaseRedirectTest):

    def setUp(self):

        self.site = Site.objects.get_current()
        self.homepage = Page.objects.create(site=self.site)
        self.hptitle = Title.objects.create(
            title='Home page',
            slug='home-page',
            page=self.homepage,
            language='en',
        )
        self.homepage.publish(language='en')

        self.page1 = Page.objects.create(site=self.site)

        self.title1 = Title.objects.create(
            title='Test page',
            slug='test-page',
            page=self.page1,
            language='en',
        )
        self.page1.publish(language='en')

    def test_301_redirect(self):

        redirect = Redirect.objects.create(
            site=self.site,
            old_path=str(self.page1.get_absolute_url()),
            new_path='/en/',
            response_code='301',
        )

        client = Client()
        response = client.get('/en/test-page/')
        self.assertEqual(response.status_code, 301)
        self.assertRedirects(response, redirect.new_path, status_code=301)

    def test_302_redirect(self):

        redirect = Redirect.objects.create(
            site=self.site,
            old_path=str(self.page1.get_absolute_url()),
            new_path='/en/',
            response_code='302',
        )

        client = Client()

        response = client.get('/en/test-page/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect.new_path, status_code=302)

    def test_querystring_redirect(self):

        redirect = Redirect.objects.create(
            site=self.site_1,
            old_path=str(self.page1.get_absolute_url()),
            new_path='/en/',
            response_code='302',
        )

        response = self.client.get('/en/test-page/?Some_query_param')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect.new_path + '?Some_query_param', status_code=302)

    def test_410_redirect(self):

        Redirect.objects.create(
            site=self.site,
            old_path=str(self.page1.get_absolute_url()),
            new_path='/en/',
            response_code='410',
        )

        client = Client()

        response = client.get('/en/test-page/')
        self.assertEqual(response.status_code, 410)

        Redirect.objects.create(
            site=self.site,
            old_path='/some-path/',
            response_code='302'
        )

        response2 = client.get('/some-path/')
        self.assertEqual(response2.status_code, 410)

    def test_use_response(self):

        with self.settings(DJANGOCMS_REDIRECT_USE_REQUEST=False):
            redirect = Redirect.objects.create(
                site=self.site,
                old_path=str(self.page1.get_absolute_url()),
                new_path='/en/',
                response_code='302',
            )

            client = Client()

            response = client.get('/en/test-page/')
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, redirect.new_path, status_code=302)

    def test_delete_redirect(self):
        redirect = Redirect.objects.create(
            site=self.site,
            old_path=str(self.page1.get_absolute_url()),
            new_path='/en/',
            response_code='301',
        )

        client = Client()

        response = client.get('/en/test-page/')
        self.assertRedirects(response, redirect.new_path, status_code=301)
        redirect.delete()
        response2 = client.get('/en/test-page/')
        self.assertEqual(response2.status_code, 200)
