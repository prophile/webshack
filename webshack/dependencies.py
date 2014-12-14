import html.parser
from urllib.parse import urljoin
import re
import tinycss

def analyse_link(link, search_deps=True):
    ROOT = 'https://example.com/a/b/c/'
    BASE_URL = urljoin(ROOT, '__this_component/')
    source = urljoin(BASE_URL, link)
    if source.startswith(BASE_URL):
        if not search_deps:
            return source[len(BASE_URL):]
    elif source.startswith(ROOT):
        if search_deps:
            return source[len(ROOT):].split('/')[0]
    return None

class LinkProcessor(html.parser.HTMLParser):
    def __init__(self, receive_match, **kwargs):
        super().__init__()
        self.receive_match = receive_match
        self.analyse_args = kwargs

    def process_link(self, link):
        if link is None:
            return
        match = analyse_link(link, **self.analyse_args)
        if match is not None:
            self.receive_match(match)

    def handle_link(self, attrs):
        if attrs.get('rel', 'default') in ('stylesheet', 'import'):
            self.process_link(attrs.get('href'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link":
            self.handle_link(attrs)
        if tag == "script":
            self.process_link(attrs.get('src'))
        if tag == "img":
            self.process_link(attrs.get('src'))

def identify_html_dependencies(path):
    deps = set()
    parser = LinkProcessor(deps.add, search_deps=True)
    with path.open('r') as f:
        parser.feed(f.read())
    with path.open('r') as f:
        parser.feed(f.read())
    return iter(deps)

def identify_css_dependencies(path):
    deps = set()
    def dispatch_link(uri):
        match = analyse_link(uri, search_deps=True)
        if match is not None:
            deps.add(match)
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
    return iter(deps)

EXTENSION_HANDLERS = {'.html': identify_html_dependencies,
                      '.css': identify_css_dependencies}

def identify_non_dependencies(path):
    return ()

def identify_dependencies(path):
    return EXTENSION_HANDLERS.get(path.suffix, identify_non_dependencies)(path)

