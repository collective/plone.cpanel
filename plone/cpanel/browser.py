from operator import itemgetter

from plone.i18n.locales.interfaces import IContentLanguageAvailability
from zope.component import adapts
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import locales, LoadLocaleError
from zope.interface import Interface
from zope.publisher.interfaces import IRequest
from zope.publisher.browser import BrowserView

from AccessControl import getSecurityManager
from AccessControl.Permissions import view as View
from OFS.interfaces import IApplication
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.GenericSetup import profile_registry
from Products.GenericSetup import BASE, EXTENSION
from Products.GenericSetup.upgrade import normalize_version
from ZPublisher.BaseRequest import DefaultPublishTraverse

from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.interfaces import IPloneSiteRoot

import hashlib
import random


class AppTraverser(DefaultPublishTraverse):
    adapts(IApplication, IRequest)

    def publishTraverse(self, request, name):
        if name == 'index_html':
            view = queryMultiAdapter((self.context, request),
                        Interface, 'plone-cpanel')
            if view is not None:
                return view
        return DefaultPublishTraverse.publishTraverse(self, request, name)


class Overview(BrowserView):

    def sites(self, root=None):
        if root is None:
            root = self.context

        result = []
        secman = getSecurityManager()
        for obj in root.values():
            if IPloneSiteRoot.providedBy(obj):
                if secman.checkPermission(View, obj):
                    result.append(obj)
            elif obj.getId() in getattr(root, '_mount_points', {}):
                result.extend(self.sites(root=obj))
        return result

    def outdated(self, obj):
        mig = obj.get('portal_migration', None)
        if mig is not None:
            return mig.needUpgrading()
        return False

    def can_manage(self):
        secman = getSecurityManager()
        return secman.checkPermission(ManagePortal, self.context)

    def upgrade_url(self, site, can_manage=None):
        if can_manage is None:
            can_manage = self.can_manage()
        if can_manage:
            return site.absolute_url() + '/@@plone-upgrade'
        else:
            return self.context.absolute_url() + '/@@plone-root-login'



    default_extension_profiles = (
        'plonetheme.classic:default',
        'plonetheme.sunburst:default',
        )

    def profiles(self):
        base_profiles = []
        extension_profiles = []

        # profiles available for install/uninstall, but hidden at the time
        # the Plone site is created
        not_installable = [
            'kupu:default',
            'plonetheme.classic:uninstall',
            'Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow',
            'plone.app.registry:default',
            'plone.app.z3cform:default',
            'plone.app.collection:default',
        ]
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        for util in utils:
            not_installable.extend(util.getNonInstallableProfiles())

        for info in profile_registry.listProfileInfo():
            if info.get('type') == EXTENSION and \
               info.get('for') in (IPloneSiteRoot, None):
                profile_id = info.get('id')
                if profile_id not in not_installable:
                    if profile_id in self.default_extension_profiles:
                        info['selected'] = 'selected'
                    extension_profiles.append(info)

        def _key(v):
            # Make sure implicitly selected items come first
            selected = v.get('selected') and 'automatic' or 'manual'
            return '%s-%s' % (selected, v.get('title', ''))
        extension_profiles.sort(key=_key)

        for info in profile_registry.listProfileInfo():
            if info.get('type') == BASE and \
               info.get('for') in (IPloneSiteRoot, None) and \
               info.get('id') != u'Products.kupu:default':
                base_profiles.append(info)

        return dict(
            base=tuple(base_profiles),
            default=_DEFAULT_PROFILE,
            extensions=tuple(extension_profiles),
        )

    def browser_language(self):
        language = 'en'
        pl = IUserPreferredLanguages(self.request)
        if pl is not None:
            languages = pl.getPreferredLanguages()
            for httplang in languages:
                parts = (httplang.split('-') + [None, None])[:3]
                if parts[0] == parts[1]:
                    # Avoid creating a country code for simple languages codes
                    parts = [parts[0], None, None]
                elif parts[0] == 'en':
                    # Avoid en-us as a language
                    parts = ['en', None, None]
                try:
                    locale = locales.getLocale(*parts)
                    language = locale.getLocaleID().replace('_', '-').lower()
                    break
                except LoadLocaleError:
                    # Just try the next combination
                    pass
        return language

    def languages(self, default='en'):
        util = queryUtility(IContentLanguageAvailability)
        if '-' in default:
            available = util.getLanguages(combined=True)
        else:
            available = util.getLanguages()
        languages = [(code, v.get(u'native', v.get(u'name'))) for
                     code, v in available.items()]
        languages.sort(key=itemgetter(1))
        return languages

    def __call__(self):
        context = self.context
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            email = form.get('email', None)
            fullname = form.get('fullname', None)
            if email or fullname:

                # Simple naming routine
                site_id = None
                while not site_id:
                    site_id = hashlib.md5(str(random.random()))[:5]
                    if not context.get(site_id, None):
                        site_id = None

                site = addPloneSite(
                    context, site_id,
                    title=form.get('title', ''),
                    profile_id=form.get('profile_id', _DEFAULT_PROFILE),
                    extension_ids=form.get('extension_ids', ()),
                    setup_content=form.get('setup_content', False),
                    default_language=form.get('default_language', 'en'),
                    )
                # setup manager
                site.portal_membership.addUser(email, fullname)
                # setup VHM
                site_alias = form.get('site_id', 'Plone')
                site.virtual_hosting.addMapping("%s/%s"% (site_alias, site_id))

                self.request.response.redirect(site.absolute_url())

        return self.index()

