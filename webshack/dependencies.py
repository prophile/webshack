import html.parser
from urllib.parse import urljoin
import re
import tinycss
from enum import Enum
from os.path import commonprefix
from collections import namedtuple

class RefCat(Enum):
    internal = 1
    external = 2

Ref = namedtuple('Ref', 'cat ref')

def grok_ref(link, containing_component=None):
    ROOT = 'https://example.com/a/b/'
    if containing_component is not None:
        BASE_URL = urljoin(ROOT, 'components/{}/'.format(containing_component))
    else:
        BASE_URL = ROOT
    COMPONENTS_URL = urljoin(ROOT, 'components/')
    source = urljoin(BASE_URL, link)
    if not source.startswith(COMPONENTS_URL):
        return None
    section = source[len(COMPONENTS_URL):]
    parts = section.split('/')
    component = parts[0]
    elems = '/'.join(parts[1:])
    if containing_component == component:
        return Ref(cat=RefCat.internal, ref=elems)
    else:
        return Ref(cat=RefCat.external, ref=component)

class LinkProcessor(html.parser.HTMLParser):
    def __init__(self, receive_match, **kwargs):
        super().__init__()
        self.receive_match = receive_match
        self.analyse_args = kwargs

    def process_link(self, link):
        if link is None:
            return
        match = grok_ref(link, **self.analyse_args)
        if match is not None:
            self.receive_match(match)

    def handle_link(self, attrs):
        self.process_link(attrs.get('href'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link":
            self.handle_link(attrs)
        if tag == "script":
            self.process_link(attrs.get('src'))
        if tag == "img":
            self.process_link(attrs.get('src'))

COMPONENT_RE = re.compile('components/(.*?)/')
def get_component(path):
    match = COMPONENT_RE.match(str(path))
    if match is not None:
        return match.group(1)
    return None

def identify_html_refs(path, get_ref):
    parser = LinkProcessor(get_ref,
                           containing_component=get_component(path))
    with path.open('r') as f:
        parser.feed(f.read())
    with path.open('r') as f:
        parser.feed(f.read())

def identify_css_refs(path, get_ref):
    def dispatch_link(uri):
        match = grok_ref(uri,
                         containing_component=get_component(path))
        if match is not None:
            get_ref(match)
    parser = tinycss.make_parser()
    with path.open('rb') as f:
        stylesheet = parser.parse_stylesheet_file(f)
    for rule in stylesheet.rules:
        if isinstance(rule, tinycss.css21.ImportRule):
            dispatch_link(rule.uri)
        elif isinstance(rule, tinycss.css21.RuleSet):
            for decl in rule.declarations:
                for part in decl.value:
                    if part.type == "URI":
                        dispatch_link(part.value)

EXTENSION_HANDLERS = {'.html': identify_html_refs,
                      '.css': identify_css_refs}

def identify_non_refs(path, get_ref):
    pass

def identify_refs(path, get_ref):
    handler = EXTENSION_HANDLERS.get(path.suffix, identify_non_refs)
    return handler(path, get_ref)

def identify_dependencies(path):
    dependencies = set()
    def get_ref(ref):
        if ref.cat == RefCat.external:
            dependencies.add(ref.ref)
    identify_refs(path, get_ref)
    return iter(dependencies)

def verify(path):
    def get_ref(ref):
        if ref.cat == RefCat.internal:
            new_path = path.parent / ref.ref
            if not new_path.exists():
                print("Missing file: {}".format(ref.ref))
                raise IOError("IS BROKEN")
    identify_refs(path, get_ref)

