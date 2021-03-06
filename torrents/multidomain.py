# -*- coding: utf-8 -*-
import re, flask, urllib2
from newrelic.agent import transaction_name
from flask import g, url_for as flask_url_for, redirect, Blueprint, request, current_app, _request_ctx_stack

DOMAIN_SUFFIX = DOMAIN_SUFFIX_CHECKER = None
_MultidomainBlueprint__rule_domains = {}
_MultidomainBlueprint__endpoint_domain = {}

DOMAIN_REPLACER=re.compile(r"^(https?://)[^\/?]*(.*)$")

def update_domain_suffix(new_value):
    global DOMAIN_SUFFIX, DOMAIN_SUFFIX_CHECKER
    if new_value:
        DOMAIN_SUFFIX = new_value
        DOMAIN_SUFFIX_CHECKER = re.compile(r"^https?://[^\/?]*"+DOMAIN_SUFFIX+"([\/?].*)?")
    else:
        DOMAIN_SUFFIX = DOMAIN_SUFFIX_CHECKER = None

def empty_redirect(url, code=302):
    response = redirect(url, code)
    response.data = ""
    return response

def get_domain_suffix():
    if DOMAIN_SUFFIX_CHECKER and DOMAIN_SUFFIX_CHECKER.match(request.url_root):
        return DOMAIN_SUFFIX
    return ""

def redirect_to_domain(domain, http_code):
    return empty_redirect(DOMAIN_REPLACER.sub(r"\1"+domain + get_domain_suffix() + r"\2", request.url), http_code)

def multidomain_view(*args, **kwargs):
    domains = _MultidomainBlueprint__rule_domains[request.url_rule.rule]
    info = domains.get(g.domain, None)
    if info:
        if info[0]!=request.blueprint:
            g.domain_conflict = True
            request.url_rule = next(r for r in _request_ctx_stack.top.url_adapter.map._rules if r.rule==request.url_rule.rule and r.endpoint.startswith(info[0]+"."))
        return info[1](*args, **kwargs)
    else:
        return redirect_to_domain(domains.iterkeys().next(), 301)

def url_for(endpoint, **values):
    # check for language change order
    target_lang = values.pop("_lang", g.lang)

    # absolute URL?
    external = values.pop("_external", False)

    # force schema change?
    schema = values.pop("_secure", None)

    # allows to use "." for current path
    if endpoint==".":
        endpoint = request.endpoint
        path = request.script_root + urllib2.quote(request.path.encode('utf-8'))
        query_string = request.url
        if u"?" in query_string:
            try:
                if not isinstance(query_string, unicode):
                    query_string = query_string.decode("utf-8")
                path += query_string[query_string.find(u"?"):]
            except:
                pass
    else:
        path = flask_url_for(endpoint, **values)

    # check for domain change order
    target_domain = values.pop("_domain", _MultidomainBlueprint__endpoint_domain.get(endpoint, None)) or g.domain

    # if must change anything overrides this method
    if external or not schema is None or (target_domain and target_domain != g.domain) or (target_lang and target_lang!=g.lang):
        # Use https if forced or is current schema
        schema = "https://" if schema or (schema is None and g.secure_request) else "http://"

        if target_lang and target_domain in g.translate_domains and target_lang!=g.langs[0]:
            return schema + target_lang + "." + target_domain + get_domain_suffix() + path
        else:
            return schema + target_domain + get_domain_suffix() + path

    return path

def patch_flask():
    global flask
    flask.url_for = url_for

class MultidomainBlueprint(Blueprint):
    '''
    Blueprint for multiple domains handling.
    '''
    def __init__(self, *args, **kwargs):
        self.domain = kwargs.pop("domain") if "domain" in kwargs else None
        Blueprint.__init__(self, *args, **kwargs)

    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop("endpoint", f.__name__)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        if self.domain:
            # Add rule to domain mapping
            if rule in __rule_domains:
                __rule_domains[rule][self.domain] = (self.name, transaction_name()(view_func))
            else:
                __rule_domains[rule] = {self.domain: (self.name, transaction_name()(view_func))}

            # Add endpoint to domain mapping
            __endpoint_domain[self.name+"."+endpoint] = self.domain

            return Blueprint.add_url_rule(self, rule, endpoint, multidomain_view, **options)
        else:
            return Blueprint.add_url_rule(self, rule, endpoint, view_func, **options)
