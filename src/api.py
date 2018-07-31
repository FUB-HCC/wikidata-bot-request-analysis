import pywikibot
from pywikibot.data import api


class WikidataAPI(object):
    """
    Wrapper Class for The MediaWiki action API.
    """

    SITE = pywikibot.site.DataSite('wikidata', 'wikidata')

    DEFAULT_USERS_PARAMS = {
        'usprop': 'blockinfo|groups|implicitgroups|rights|editcount|registration'
    }

    DEFAULT_REVISIONS_PARAMS = {
        'rvprop': 'timestamp|user',
        'rvlimit': 'max',
        'formatversion': '2',
    }

    DEFAULT_ALLUSERS_PARAMS = {
        'augroup': 'bot',
    }

    @classmethod
    def users(cls, users, **params):
        """
        Wrapper function to make a request with action=query and list=users.
        @:param users: user names
        @:type users: list
        @:param params: query params
        @:type params: dict
        @:return: users
        @:rtype: dict
        """

        params = {**cls.DEFAULT_USERS_PARAMS, **params}

        params = {**params, **{
            'action': 'query',
            'list': 'users',
            'ususers': '|'.join(users),
        }}

        request = api.Request(site=cls.SITE, **params)
        return request.submit()

    @classmethod
    def revisions(cls, pages, **params):
        """
        Wrapper function to make a request with action=query and prop=revisions.
        @:param pages: page names
        @:type pages: list
        @:param params: query params
        @:type params: dict
        @:return: revisions
        @:rtype: dict
        """

        params = {**cls.DEFAULT_REVISIONS_PARAMS, **params}

        params = {**params, **{
            'action': 'query',
            'prop': 'revisions',
            'titles': '|'.join(pages),
        }}

        request = api.Request(site=cls.SITE, **params)
        return request.submit()

    @classmethod
    def allusers(cls, **params):
        """
        Wrapper function to make a request with action=query and list=allusers.
        @:param params: query params
        @:type params: dict
        @:return: users
        @:rtype: dict
        """

        params = {**cls.DEFAULT_ALLUSERS_PARAMS, **params}

        params = {**params, **{
            'action': 'query',
            'list': 'allusers',
        }}

        request = api.Request(site=cls.SITE, **params)
        return request.submit()
