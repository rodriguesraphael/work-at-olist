from django.test import TestCase
from django.urls import reverse, resolve

from calls.views import CallInvoiceViewSet, CallLogViewSet


class UrlTestCase(TestCase):
    def resolve_by_name(self, name, **kwargs):
        url = reverse(name, kwargs=kwargs)
        return resolve(url)

    def assert_actions(self, allowed, actions):
        self.assertEqual(len(allowed), len(actions))

        for allows in allowed:
            self.assertIn(allows, actions)

    def test_call_log_url_only_allows_post(self):
        resolver = self.resolve_by_name('call-log-list')
        self.assert_actions(['post'], resolver.func.actions)

    def test_call_invoice_url_only_allow_get(self):
        resolver = self.resolve_by_name(
            'call-invoice-detail',
            source='99999999999'
        )
        self.assert_actions(['get'], resolver.func.actions)

    def test_call_log_resolves_retrieve_url(self):
        resolver = self.resolve_by_name('call-log-list')
        self.assertEqual(resolver.func.cls, CallLogViewSet)

    def test_call_invoice_resolves_retrieve_url(self):
        resolver = self.resolve_by_name(
            'call-invoice-detail',
            source='99999999999'
        )
        self.assertEqual(resolver.func.cls, CallInvoiceViewSet)
