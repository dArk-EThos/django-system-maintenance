import django
from django.core.urlresolvers import resolve, reverse
from django.template.loader import render_to_string
from django.test import TestCase

from system_maintenance import views
from system_maintenance.tests.utilities import (
    CustomAssertions, login_normal_user, login_sysadmin_superuser,
    login_sysadmin_user, populate_test_db)


class CommonViewTests:

    """
    A mixin consisting of a set of tests that are common to multiple views.

    Unless these tests are overridden, a `TestCase` that uses this mixin must
    define a set of view-specific variables in the `setUp()` method similar
    to this:

        def setUp(self):
            populate_test_db()
            login_sysadmin_user(self)

            self.namespace = 'system_maintenance:documentation_record_list'
            self.template = 'system_maintenance/documentation_record_list.html'
            self.title = 'Documentation Records'
            self.url = '/system_maintenance/documentation/'
            self.view = views.DocumentationRecordListView
    """

    def test_namespace_reverses_to_url(self):
        """
        Test that a given namespace reverses to the correct URL.
        """
        self.assertEqual(reverse(self.namespace), self.url)

    def test_url_resolves_to_view(self):
        """
        Test that a given URL resolves to the correct view.
        """
        found = resolve(self.url)

        if django.VERSION < (1, 8):
            found_name = found.func.func_name
        else:
            found_name = found.func.__name__

        self.assertEqual(found_name, getattr(self.view, '__name__', None))

    def test_view_returns_correct_title(self):
        """
        Test that view's response contains the correct page title.
        """
        url = reverse(self.namespace)
        response = self.client.get(url)
        self.assertContains(response, '<title>{}</title>'.format(self.title))

    def test_view_returns_static_files_links(self):
        """
        Test that view's response contains links to the correct static files.
        """
        url = reverse(self.namespace)
        response = self.client.get(url)
        self.assertContains(response, 'bootstrap.min.css')
        self.assertContains(response, 'bootstrap.min.js')
        self.assertContains(response, 'jquery.min.js')
        self.assertContains(response, '/static/system_maintenance/css/app.css')
        self.assertContains(response, '/static/system_maintenance/js/app.js')

    def test_view_returns_correct_html(self):
        """
        Test that a view's response contains the correct HTML based on the
        template.
        """
        url = reverse(self.namespace)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        expected_html = render_to_string(self.template)
        self.assertEqual(response.content.decode(), expected_html)


class RedirectAnonymousUserToAuthenticationTest(TestCase, CustomAssertions):

    def test_system_maintenance_home_view(self):
        self.assertRedirectUserToAuthentication(
            'system_maintenance:system_maintenance_home_view')

    def test_documentation_record_list(self):
        self.assertRedirectUserToAuthentication(
            'system_maintenance:documentation_record_list')


class RedirectNonSysAdminUserToAuthenticationTest(TestCase, CustomAssertions):

    def setUp(self):
        populate_test_db()
        login_normal_user(self)

    def test_system_maintenance_home_view(self):
        self.assertRedirectUserToAuthentication(
            'system_maintenance:system_maintenance_home_view')

    def test_documentation_record_list(self):
        self.assertRedirectUserToAuthentication(
            'system_maintenance:documentation_record_list')


class HomeViewTest(TestCase, CommonViewTests):

    def setUp(self):
        populate_test_db()
        login_sysadmin_user(self)

        self.namespace = 'system_maintenance:system_maintenance_home_view'
        self.title = 'System Maintenance'
        self.url = '/system_maintenance/'

    def test_url_resolves_to_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, views.system_maintenance_home_view)

    def test_view_returns_correct_html(self):
        """
        Test that normal system administrators have links to System
        Maintenance pages, but not admin pages.
        """
        url = reverse(self.namespace)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        root = '/system_maintenance/'
        self.assertContains(response, '{}records/'.format(root))
        self.assertContains(response, '{}documentation/'.format(root))
        self.assertContains(
            response, 'System maintenance records and other important ' +
            'system administration information is accessible via the ' +
            'buttons below.')

        self.assertNotContains(response, 'System Maintenance Admin Page')
        self.assertNotContains(response, '/admin/system_maintenance/')
        self.assertNotContains(response, 'glyphicon-wrench')

    def test_view_returns_correct_html_for_superuser_sysadmin(self):
        """
        Test that superuser system administrators have links to System
        Maintenance admin pages.
        """
        login_sysadmin_superuser(self)
        url = reverse(self.namespace)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        root = '/admin/system_maintenance/'
        self.assertContains(response, '{}maintenancerecord/'.format(root))
        self.assertContains(response, '{}documentationrecord/'.format(root))
        self.assertContains(response, '{}hardware/'.format(root))
        self.assertContains(response, '{}maintenancetype/'.format(root))
        self.assertContains(response, '{}software/'.format(root))
        self.assertContains(response, '{}system/'.format(root))
        self.assertContains(response, '{}sysadmin/'.format(root))
        self.assertContains(response, 'System Maintenance Admin Page')
        self.assertContains(response, 'glyphicon-wrench')


class DocumentationRecordListViewTest(TestCase, CommonViewTests):

    def setUp(self):
        populate_test_db()
        login_sysadmin_user(self)

        self.namespace = 'system_maintenance:documentation_record_list'
        self.template = 'system_maintenance/documentation_record_list.html'
        self.title = 'Documentation Records'
        self.url = '/system_maintenance/documentation/'
        self.view = views.DocumentationRecordListView

    def test_view_returns_correct_html(self):
        url = reverse(self.namespace)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        expected_html = render_to_string(self.template)
        self.assertEqual(response.content.decode(), expected_html)


class MaintenanceRecordListViewTest(TestCase, CommonViewTests):

    def setUp(self):
        populate_test_db()
        login_sysadmin_user(self)

        self.namespace = 'system_maintenance:maintenance_record_list'
        self.template = 'system_maintenance/maintenance_record_list.html'
        self.title = 'Maintenance Records'
        self.url = '/system_maintenance/records/'
        self.view = views.MaintenanceRecordListView