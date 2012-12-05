from zope.interface import Interface
import zope.component
from zope.schema.interfaces import WrongType, WrongContainedType
from time import time
import unittest

from zExceptions import Forbidden
from zExceptions import BadRequest

from Products.PloneTestCase import ptc

from pmr2.oauth.interfaces import IDefaultScopeManager
from pmr2.oauth.interfaces import ITokenManager, IConsumerManager
from pmr2.oauth.token import Token
from pmr2.oauth.consumer import Consumer
from pmr2.oauth.scope import DefaultScopeManager

from pmr2.oauth.tests import base


class DefaultScopeManagerTestCase(ptc.PloneTestCase):

    def afterSetUp(self):
        self.scopeManager = DefaultScopeManager()

    def assertScopeValid(self, client, owner, container, name):
        self.assertTrue(self.scopeManager.validate(
            client, owner, container, name))

    def assertScopeInvalid(self, client, owner, container, name):
        self.assertFalse(self.scopeManager.validate(
            client, owner, container, name))

    def test_0000_empty_scope(self):
        self.assertEqual(self.scopeManager.default_scopes, None)
        self.assertScopeInvalid('', '', None, '')

    def test_0100_root_scope(self):
        self.scopeManager.default_scopes = {
            'Plone Site': ['folder_contents'],
        }
        self.assertScopeValid('', '', self.portal, 'folder_contents')
        self.assertScopeInvalid('', '', self.portal, 'manage')

    def test_0101_folder_scope(self):
        self.scopeManager.default_scopes = {
            'Folder': ['folder_contents'],
        }
        self.assertScopeValid('', '', self.folder, 'folder_contents')

    def test_0201_browser_view(self):
        self.scopeManager.default_scopes = {
            'Folder': ['+/addFile', 'folder_contents'],
        }
        # Adding views.
        folder_add = self.folder.restrictedTraverse('+')
        self.assertScopeValid('', '', folder_add, 'addFile')
        self.assertScopeInvalid('', '', folder_add, 'addFolder')
        self.assertScopeInvalid('', '', self.folder, 'addFile')

        # For whatever reason this happened, but still forbidden by
        # scope restrictions.
        portal_add = self.portal.unrestrictedTraverse('+')
        self.assertScopeInvalid('', '', portal_add, 'addFile')

    def test_2000_bad_scope_assignment(self):
        self.assertRaises(WrongContainedType, setattr, 
            self.scopeManager, 'default_scopes', {
                'Folder': 'folder_contents',
            }
        )

        self.assertRaises(WrongType, setattr, 
            self.scopeManager, 'default_scopes', ['folder_contents']
        )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(DefaultScopeManagerTestCase))
    return suite