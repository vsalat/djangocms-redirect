# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

RESPONSE_CODES = (
    ('301', _('301 - Permanent redirection')),
    ('302', _('302- Temporary redirection'),),
    ('410', _('410 - Permanently unavailable'),),
)


@python_2_unicode_compatible
class Redirect(models.Model):
    site = models.ForeignKey(Site, verbose_name=_('site'), on_delete=models.CASCADE)
    old_path = models.CharField(
        _('redirect from'),
        max_length=200,
        db_index=True,
        help_text=_('Select a Page or write an url')
    )
    new_path = models.CharField(
        _('redirect to'),
        max_length=200,
        blank=True,
        help_text=_('Select a Page or write an url')
    )
    response_code = models.CharField(
        _('response code'),
        max_length=3,
        choices=RESPONSE_CODES,
        default=RESPONSE_CODES[0][0],
        help_text=_('This is the http response code returned if a destination '
                    'is specified. If no destination is specified the response code will be 410.'))
    subpath_match = models.BooleanField(
        _('Subpath match'),
        default=False,
        help_text=_(
            'If selected all the pages starting with the given string will be redirected by '
            'replacing the matching subpath with the provided redirect path.'
        )
    )
    catchall_redirect = models.BooleanField(
        _('Catchall redirect'),
        default=False,
        help_text=_(
            'If selected all the pages starting with the given string will be redirected to the '
            'given redirect path'
        )
    )

    class Meta:
        verbose_name = _('redirect')
        verbose_name_plural = _('redirects')
        db_table = 'django_redirect'
        unique_together = (('site', 'old_path'),)
        ordering = ('old_path',)

    def __str__(self):
        return '{0} ---> {1}'.format(self.old_path, self.new_path)


@receiver(post_save, sender=Redirect)
@receiver(post_delete, sender=Redirect)
def clear_redirect_cache(**kwargs):
    from .utils import get_key_from_path_and_site
    key = get_key_from_path_and_site(kwargs['instance'].old_path, kwargs['instance'].site_id)
    cache.delete(key)
