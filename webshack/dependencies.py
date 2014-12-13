import html.parser
import re
import tinycss

RELATIVE_LINK_RE = re.compile('../(.+?)/')

class LinkProcessor(html.parser.HTMLParser):
    def __init__(self, dependencies):
        super().__init__()
        self.dependencies = dependencies

    def process_link(self, link):
        if link is None:
            return
        match = RELATIVE_LINK_RE.match(link)
        if match is not None:
            self.dependencies.add(match.group(1))

    def handle_link(self, attrs):
        if attrs.get('rel', 'default') in ('stylesheet', 'import'):
            self.process_link(attrs.get('href'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link":
            self.handle_link(attrs)
        if tag == "script":
            self.process_link(attrs.get('src'))

def identify_html_dependencies(path):
    deps = set()
    parser = LinkProcessor(deps)
    with path.open('r') as f:
        parser.feed(f.read())
    return iter(deps)

def identify_css_dependencies(path):
    deps = set()
    def dispatch_link(uri):
        match = RELATIVE_LINK_RE.match(uri)
        if match is not None:
            deps.add(match.group(1))
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

