"""Build a complete, isolated, static documentation site from published evidence.

Every page is generated from what the publisher published on Apify: the Store listing,
the README, the input/output/dataset definitions, the default run memory, and the
Store's pay-per-event prices. When a fact is missing, the page leaves that part out.
"""

import base64
from datetime import datetime
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote, urljoin, urlsplit, unquote
from xml.sax.saxutils import escape as xml_escape

from markdown_it import MarkdownIt
from markdown_it.token import Token

from . import content as facts
from .http import SyncError
from .isolation import check_brand, check_snapshot
from .render import digest, json_text

ASSETS = Path(__file__).with_name("site_assets")


def esc(value):
    return html.escape(str(value), quote=True)


def category_name(category):
    return category.replace("_", " ").title().replace("Ai", "AI").replace("Seo", "SEO")


def category_slug(category):
    return category.lower().replace("_", "-")


def source_example(actor):
    """Only published prefills/defaults: never invent schema fields or values."""
    return facts.schema_example(actor)


def source_relative(target):
    """True for a README link or image that points into the Actor's own source tree
    (`../README.md`, `docs/run.png`, `/src/main.py`, an empty target). Those resolve on
    no public page: neither here nor on the Store, where the source is not published."""
    target = (target or "").strip()
    if target.startswith("#"):
        return False
    parts = urlsplit(target)
    return not (parts.scheme or parts.netloc)


def without_source_links(children):
    """A source-relative link keeps its text and loses the link; a source-relative image
    becomes its alt text. Links do not nest in CommonMark, so one flag pairs open/close."""
    kept, dropping = [], False
    for child in children:
        if child.type == "link_open" and source_relative(child.attrGet("href")):
            dropping = True
            continue
        if child.type == "link_close" and dropping:
            dropping = False
            continue
        if child.type == "image" and source_relative(child.attrGet("src")):
            alt = Token("text", "", 0)
            alt.content = child.content
            kept.append(alt)
            continue
        kept.append(child)
    return kept


def anchor_id(title, prefix="readme-"):
    return prefix + (re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")[:60].strip("-") or "section")


def markdown(text, used=None, anchors=None, shift=0):
    """CommonMark with tables; raw HTML is escapedd, body H1s become H2s, and links into
    the Actor's source tree become plain text (they would be dangling links here).
    `used` shares heading IDs across several fragments of one page; `anchors` maps README
    fragment links to the IDs this page uses; `shift` demotes headings (H2 -> H3)."""
    parser = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table").enable("strikethrough")
    tokens = parser.parse(text)
    used = {} if used is None else used
    for index, token in enumerate(tokens):
        if token.type in ("heading_open", "heading_close"):
            level = min(6, max(2, int(token.tag[1]) + shift))
            token.tag = "h" + str(level)
        if token.type == "heading_open" and index + 1 < len(tokens):
            heading_id = anchor_id(tokens[index + 1].content)
            used[heading_id] = used.get(heading_id, 0) + 1
            if used[heading_id] > 1:
                heading_id += "-" + str(used[heading_id])
            token.attrSet("id", heading_id)
        if token.children:
            token.children = without_source_links(token.children)
            for child in token.children:
                if child.type == "link_open" and (child.attrGet("href") or "").startswith("#"):
                    fragment = child.attrGet("href")[1:]
                    child.attrSet("href", "#" + (anchors or {}).get(fragment, "readme-" + fragment))
    rendered = parser.renderer.render(tokens, parser.options, {})
    # Column alignment comes out as inline styles, which the page's CSP blocks: use classes.
    rendered = re.sub(r' style="text-align:(left|right|center)"', r' class="align-\1"', rendered)

    # Copy buttons for README code blocks are rendered here, not built by script at load time.
    def wrap(match):
        used["__code"] = used.get("__code", 0) + 1
        block_id = f"readme-code-{used['__code']}"
        attrs = match.group(1) or ""
        return (f'<div class="code"><pre><code id="{block_id}"{attrs}>{match.group(2)}</code></pre>'
                f'<button type="button" class="copy" data-copy="{block_id}">Copy</button></div>')
    rendered = re.sub(r"<pre><code((?: class=\"[^\"]*\")?)>(.*?)</code></pre>", wrap, rendered, flags=re.S)
    return rendered.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")


INLINE = MarkdownIt("commonmark", {"html": False, "linkify": False}).disable(["link", "image"])


def inline_md(text):
    """Publisher field text (schema descriptions) as inline Markdown: `code` stays code,
    links and images stay text, HTML is escaped."""
    return "<!--readme-->" + INLINE.renderInline(re.sub(r"\s+", " ", str(text)).strip()) + "<!--/readme-->"


def readme_html(fragment):
    """README-derived HTML, fenced so page checks can tell publisher text from generated text."""
    return "<!--readme-->" + fragment + "<!--/readme-->"


def code_block(text, block_id, language="json", label=None):
    caption = f'<figcaption>{esc(label)}</figcaption>' if label else ""
    return (f'<figure class="code">{caption}<pre><code id="{esc(block_id)}" class="language-{esc(language)}">{esc(text)}</code></pre>'
            f'<button type="button" class="copy" data-copy="{esc(block_id)}">Copy</button></figure>')


def split_table(css, caption, heads, rows, first, noun):
    """A long reference table: the first rows stay visible (scannable, and cheap to lay out);
    the rest sit in a native disclosure in the same HTML, so they stay indexable and searchable."""
    head = "<thead><tr>" + "".join(f'<th scope="col">{h}</th>' for h in heads) + "</tr></thead>"
    def table(chunk, title):
        return f'<div class="table-wrap"><table class="{css} stack"><caption>{title}</caption>{head}<tbody>{"".join(chunk)}</tbody></table></div>'
    if len(rows) <= first + 3:
        return table(rows, caption)
    rest = rows[first:]
    return (table(rows[:first], caption) + f'<details class="more-rows"><summary>Show the other {len(rest)} {noun}</summary>'
            + table(rest, f"{caption}, continued") + "</details>")


def py_literal(value, indent=0):
    """A JSON value written as a Python literal (True/False/None), pretty-printed."""
    pad, inner = "    " * indent, "    " * (indent + 1)
    if isinstance(value, dict):
        if not value:
            return "{}"
        return "{\n" + ",\n".join(f"{inner}{json.dumps(k, ensure_ascii=False)}: {py_literal(v, indent + 1)}" for k, v in value.items()) + f",\n{pad}}}"
    if isinstance(value, list):
        if not value:
            return "[]"
        flat = "[" + ", ".join(py_literal(v, indent + 1) for v in value) + "]"
        if len(flat) <= 70 and "\n" not in flat:
            return flat
        return "[\n" + ",\n".join(inner + py_literal(v, indent + 1) for v in value) + f",\n{pad}]"
    if value is True:
        return "True"
    if value is False:
        return "False"
    if value is None:
        return "None"
    return json.dumps(value, ensure_ascii=False)


def shell_quote(text):
    return "'" + text.replace("'", "'\"'\"'") + "'"


def date_text(stamp):
    try:
        moment = datetime.strptime(stamp[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return ""
    return f"{moment.day} {moment.strftime('%B %Y')}"


def plain(text):
    """README markdown reduced to plain text for summaries and metadata."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`>#|]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def join_words(items, last="and"):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + f" {last} " + items[-1]


SLUG = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,98}[a-z0-9])?$")
ACTOR_ID = re.compile(r"^[A-Za-z0-9]{8,40}$")
# Search-engine ownership files the sync keeps in the published site (Google's FILE method).
GOOGLE_FILE = re.compile(r"^google[0-9a-f]{16}\.html$")
INDEXNOW_KEY = re.compile(r"^[0-9a-f]{32,64}$")
HUB_MINIMUM = 2


def actor_slugs(actors):
    """Readable page paths: the Actor's Store name (`google-maps-scraper`), unique within one
    organization. An ID stays the path only if a name is unusable or would collide."""
    slugs, taken = {}, {a["id"] for a in actors}
    for actor in sorted(actors, key=lambda a: a["id"]):
        name = str(actor.get("name") or "").lower()
        slug = name if SLUG.fullmatch(name) and name not in taken else actor["id"]
        taken.add(slug)
        slugs[actor["id"]] = slug
    return slugs


def fit_title(title, *suffixes, limit=68):
    for suffix in suffixes:
        if len(title + suffix) <= limit:
            return title + suffix
    return title


# Each theme speaks in its own voice on the shared pages, so independent sites never read as one
# template. Facts are the same placeholders everywhere; only the wording differs.
COPY = {
    "studio": {
        "lead": "Pick the site, see exactly what comes back and what a run costs, then copy the call into your workflow. "
                "{count} Apify Actors{examples}, documented from each one's published README, input schema and Store pricing.",
        "search_label": "Which site do you need data from?",
        "sites_title": "Pick a site",
        "sites_note": "{sites} sites, A to Z. The number is how many Actors read that site.",
        "featured": "Featured Actors",
        "how_title": "How a run works",
        "steps": ["<strong>Pick an Actor.</strong> Each page shows what it returns, the inputs it needs and its price per result.",
                  "<strong>Set the input.</strong> Start from an example on the page and keep the result limit small for a first run.",
                  "<strong>Run it on Apify.</strong> From the Console, the API, Python, JavaScript or an AI assistant over MCP, then download JSON, CSV or Excel."],
        "footer": "{brand} publishes these Actors on Apify. Pages are rebuilt from each Actor's published README, schemas and Store pricing.",
    },
    "lab": {
        "lead": "Field lists, price math and runnable code for {count} Apify Actors{examples}: Python, JavaScript, cURL or MCP. "
                "Every page is generated from the Actor's README, input schema and Store pricing, and regenerated when they change.",
        "search_label": "What do you want to pull from the web?",
        "sites_title": "Sites, A to Z",
        "sites_note": "{sites} sites. The count is how many Actors read each one.",
        "featured": "Start here",
        "how_title": "From zero to a dataset",
        "steps": ["<strong>Find the Actor</strong> for your site and check its output fields first: that is your schema.",
                  "<strong>Copy an input</strong> from the README examples and cap the result count while you test.",
                  "<strong>Call it</strong> from code or an MCP client and stream the dataset as JSON, CSV or Excel."],
        "footer": "{brand} builds and publishes these Actors on Apify. This site is generated from their published READMEs, schemas and prices.",
    },
    "editorial": {
        "lead": "What each of these {count} Apify Actors{examples} collects, what it needs from you and what a run costs, "
                "set out from its published README, input schema and Store pricing. No figure here is estimated beyond the published numbers.",
        "search_label": "Which source are you working with?",
        "sites_title": "Sources, A to Z",
        "sites_note": "{sites} sources. Each figure is the number of Actors that read it.",
        "featured": "Selected Actors",
        "how_title": "From question to dataset",
        "steps": ["<strong>Choose the source.</strong> Each page lists the fields a record carries, so you can check the evidence fits the question.",
                  "<strong>Frame the input.</strong> Begin with a published example and a small result cap; widen it once the sample looks right.",
                  "<strong>Run it on Apify</strong> and take the dataset away as CSV, Excel or JSON for your analysis."],
        "footer": "{brand} publishes these Actors on Apify. Every page is compiled from the Actors' published READMEs, schemas and Store prices.",
    },
}
COPY["classic"] = COPY["studio"]
INDEX_MINIMUM = 3


class Site:
    def __init__(self, org, actors, verification_files=()):
        check_snapshot(actors, org)
        self.org = org
        self.actors = sorted(actors, key=lambda a: (a["title"].casefold(), a["id"]))
        self.slugs = actor_slugs(self.actors)
        self.verification_files = sorted(set(verification_files))
        for name in self.verification_files:
            if not GOOGLE_FILE.fullmatch(name):
                raise SyncError("Invalid search verification file name")
        self.brand = org["brand"]
        self.theme = org.get("site", {}).get("theme", "classic")
        if self.theme not in ("classic", "studio", "lab", "editorial"):
            raise SyncError("Unknown documentation theme")
        self.base = org.get("site", {}).get("url") or f"https://{org['github_owner']}.github.io/{org['repository']}/"
        parsed = urlsplit(self.base)
        if parsed.scheme != "https" or parsed.hostname != org["github_owner"].lower() + ".github.io" or parsed.path != "/" + org["repository"] + "/":
            raise SyncError("Pages URL must belong to this brand's configured repository")
        self.prefix = parsed.path
        self.repo = f"https://github.com/{org['github_owner']}/{org['repository']}"
        self.apify = "https://apify.com/" + org["apify_username"]
        self.files = {}
        self.indexed = []
        self.pricing = {a["id"]: facts.pricing_summary(a) for a in self.actors}
        self.platform = {a["id"]: facts.platform_of(a["title"]) for a in self.actors}
        groups = {}
        for actor in self.actors:
            name = self.platform[actor["id"]]
            if name:
                groups.setdefault(name, []).append(actor)
        self.platforms = dict(sorted(groups.items(), key=lambda item: item[0].casefold()))
        self.hubs = {name: "sites/" + facts.platform_slug(name) + "/" for name, members in self.platforms.items() if len(members) >= HUB_MINIMUM}
        if len(set(self.hubs.values())) != len(self.hubs):
            raise SyncError("Two site hubs share one address")
        self.categories = sorted({c for a in self.actors for c in a["categories"]})

    # ------------------------------------------------------------------ helpers

    def link(self, path=""):
        return self.prefix + path

    def doc_path(self, actor, kind="actors"):
        return f"{kind}/{self.slugs[actor['id']]}/"

    def asset(self, path):
        return self.link(path) + "?v=" + digest(self.files.get(path, ""))[:12]

    def primary_category(self, actor):
        return next((c for c in actor["categories"] if c != "AUTOMATION"), actor["categories"][0] if actor["categories"] else "AUTOMATION")

    def price_phrase(self, actor, tier="FREE"):
        summary = self.pricing.get(actor["id"])
        thousand = facts.per_thousand(summary, tier)
        if thousand is None:
            return ""
        return f"{facts.money(thousand)} per 1,000 {facts.result_noun(summary)}s"

    def platform_href(self, name):
        if name in self.hubs:
            return self.link(self.hubs[name])
        members = self.platforms.get(name) or []
        return self.link(self.doc_path(members[0])) if members else self.link("actors/")

    def page(self, path, title, description, body, kind="CollectionPage", active="", noindex=False, redirect=None,
             modified=None, h1_in_title=None, extra_nodes=(), image=None, crumbs=None, search=True):
        canonical = self.base + path
        refresh = ""
        if redirect:
            # GitHub Pages cannot answer 301: an instant refresh plus a canonical to the new
            # address is the redirect search engines accept from a static host.
            noindex = True
            refresh = f'<meta http-equiv="refresh" content="0; url={esc(redirect)}">'
        organization_id = self.base + "#organization"
        website_id = self.base + "#website"
        page_id = canonical + "#webpage"
        organization = {"@type": "Organization", "@id": organization_id, "name": self.brand,
                        "url": self.base, "sameAs": [self.apify, self.repo]}
        website = {"@type": "WebSite", "@id": website_id, "name": self.brand + " Actor documentation",
                   "url": self.base, "publisher": {"@id": organization_id}, "inLanguage": "en"}
        web_page = {"@type": "WebPage" if kind == "TechArticle" else kind, "@id": page_id,
                    "name": title, "description": description, "url": canonical,
                    "isPartOf": {"@id": website_id}, "publisher": {"@id": organization_id},
                    "inLanguage": "en"}
        nodes = [organization, website, web_page]
        if kind == "TechArticle":
            article_id = canonical + "#article"
            web_page["mainEntity"] = {"@id": article_id}
            nodes.append({"@type": "TechArticle", "@id": article_id, "headline": title,
                          "name": title, "description": description, "url": canonical,
                          "author": {"@id": organization_id}, "publisher": {"@id": organization_id},
                          "mainEntityOfPage": {"@id": page_id}, "inLanguage": "en"})
            if modified:
                # The finish time of the published build these pages are generated from: the
                # only true content date we have (no publication date is invented).
                nodes[-1]["dateModified"] = modified
                web_page["dateModified"] = modified
            if image:
                nodes[-1]["image"] = image
        if crumbs:
            breadcrumb_id = canonical + "#breadcrumb"
            web_page["breadcrumb"] = {"@id": breadcrumb_id}
            items = [{"@type": "ListItem", "position": 1, "name": self.brand, "item": self.base}]
            for position, (name, route) in enumerate(crumbs, start=2):
                items.append({"@type": "ListItem", "position": position, "name": name, "item": self.base + route})
            nodes.append({"@type": "BreadcrumbList", "@id": breadcrumb_id, "itemListElement": items})
        for node in extra_nodes:
            nodes.append(node)
        structured = {"@context": "https://schema.org", "@graph": nodes}
        # Escape script delimiters in source-controlled metadata.
        ld = json.dumps(structured, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
        ld_hash = base64.b64encode(hashlib.sha256(ld.encode()).digest()).decode()
        csp = f"default-src 'self'; script-src 'self' 'sha256-{ld_hash}'; style-src 'self'; img-src 'self' https: data:; connect-src 'self'; base-uri 'self'; form-action 'self'; object-src 'none'"
        full_title = title if self.brand in title else title + " | " + self.brand
        navigation = "".join(f'<a href="{self.link(route)}"' + (' aria-current="page"' if label == active else "") + f'>{label.title()}</a>'
                             for label, route in [("actors", "actors/"), ("sites", "sites/"), ("topics", "topics/"), ("guides", "guides/")])
        header_search = ""
        if search:
            header_search = (f'<form class="site-search" action="{self.link("actors/")}" role="search" data-search-index="{self.link("search.json")}">'
                             '<label class="sr-only" for="site-search">Search this site</label>'
                             '<input type="search" role="combobox" id="site-search" name="q" placeholder="Search by site or data" autocomplete="off" '
                             'aria-autocomplete="list" aria-controls="site-search-results" aria-expanded="false">'
                             '<ul id="site-search-results" class="search-results" role="listbox" hidden></ul></form>')
        trail = ""
        if crumbs:
            trail = '<nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="' + self.link() + '">Home</a></li>' + "".join(
                (f'<li><a href="{self.link(route)}">{esc(name)}</a></li>' if index < len(crumbs) - 1 else f'<li aria-current="page">{esc(name)}</li>')
                for index, (name, route) in enumerate(crumbs)) + "</ol></nav>"
        social = f'<meta property="og:image" content="{esc(image)}"><meta name="twitter:card" content="summary">' if image else '<meta name="twitter:card" content="summary">'
        content = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
                   f'<meta http-equiv="Content-Security-Policy" content="{esc(csp)}"><title>{esc(full_title)}</title>'
                   f'<meta name="description" content="{esc(description[:200])}"><meta name="robots" content="{"noindex,follow" if noindex else "index,follow,max-image-preview:large,max-snippet:-1"}">{refresh}'
                   f'<link rel="canonical" href="{esc(redirect or canonical)}"><meta property="og:title" content="{esc(full_title)}">'
                   f'<meta property="og:description" content="{esc(description[:200])}"><meta property="og:type" content="{"article" if kind == "TechArticle" else "website"}">'
                   f'<meta property="og:url" content="{esc(redirect or canonical)}"><meta property="og:site_name" content="{esc(self.brand)}">{social}'
                   f'<meta name="theme-color" content="{esc(self.org.get("site", {}).get("accent", "#155dfb"))}">'
                   f'<link rel="icon" href="{self.asset("assets/mark.svg")}" type="image/svg+xml"><link rel="stylesheet" href="{self.asset("assets/site.css")}">'
                   f'<link rel="alternate" type="application/rss+xml" title="{esc(self.brand)} guides" href="{self.link("feed.xml")}">'
                   f'<script type="application/ld+json">{ld}</script><script src="{self.asset("assets/site.js")}" defer></script></head>'
                   f'<body class="theme-{self.theme}"><a href="#main" class="skip-link">Skip to content</a>'
                   f'<header class="masthead"><div class="inner"><a href="{self.link()}" class="brand"><img src="{self.asset("assets/mark.svg")}" alt="" width="32" height="32"><span>{esc(self.brand)}</span></a>'
                   f'{header_search}<nav class="primary" aria-label="Main">{navigation}</nav></div></header>'
                   f'<main id="main">{trail}{body}</main>'
                   f'<footer class="footer"><div class="inner"><p>{esc(self.copy("footer", brand=self.brand)).replace(esc(self.brand), "<strong>" + esc(self.brand) + "</strong>", 1)}</p>'
                   f'<nav aria-label="Footer"><a href="{self.link("actors/")}">All Actors</a><a href="{self.link("sites/")}">Sites</a><a href="{self.link("topics/")}">Topics</a>'
                   f'<a href="{self.link("guides/")}">Guides</a><a href="{self.link("sources/")}">How these pages are made</a><a href="{self.apify}">{esc(self.brand)} on Apify</a><a href="{self.repo}">GitHub</a></nav></div></footer></body></html>')
        filename = path + "index.html" if path.endswith("/") or not path else path
        self.files[filename] = content
        if not noindex:
            self.indexed.append(canonical)

    # ------------------------------------------------------------------ shared blocks

    def actor_rows(self, actors, hidden_after=None, level=3):
        rows = []
        for index, actor in enumerate(actors):
            target = self.link(self.doc_path(actor))
            platform = self.platform[actor["id"]]
            category = self.primary_category(actor)
            price = self.price_phrase(actor)
            search_text = " ".join([actor["title"], actor["description"], platform or "", category_name(category)]).casefold()
            meta = []
            if platform:
                meta.append(f'<a href="{self.platform_href(platform)}">{esc(platform)}</a>')
            meta.append(f'<a href="{self.link("topics/" + category_slug(category) + "/")}">{esc(category_name(category))}</a>')
            if price:
                meta.append(f'<span>{esc(price)}</span>')
            rows.append(f'<li class="actor-row" data-actor-row data-search="{esc(search_text)}" data-categories="{esc("|".join(actor["categories"]))}"'
                        + (' hidden' if hidden_after is not None and index >= hidden_after else "")
                        + f'><h{level}><a href="{target}">{esc(actor["title"])}</a></h{level}><p>{esc(actor["description"])}</p><p class="row-meta">{"".join(meta)}</p></li>')
        return '<ul class="catalog" role="list">' + "".join(rows) + "</ul>"

    def compare_table(self, actors, caption):
        """The decision table of a hub: what each tool needs, returns and costs."""
        rows = []
        for actor in actors:
            schema = actor.get("input_schema") or {}
            required = [k for k in (schema.get("required") or []) if k in (schema.get("properties") or {})]
            needs = ", ".join(f"<code>{esc(k)}</code>" for k in required[:3]) or "Nothing required"
            fields = len(facts.dataset_fields(actor))
            price = self.price_phrase(actor) or "See the Store page"
            rows.append(f'<tr><th scope="row"><a href="{self.link(self.doc_path(actor))}">{esc(actor["title"])}</a></th>'
                        f'<td data-label="What it collects">{esc(actor["description"])}</td><td data-label="You provide">{needs}</td>'
                        f'<td data-label="Declared output fields">{fields if fields else "Described in the README"}</td><td data-label="Price on the Free plan">{esc(price)}</td></tr>')
        return (f'<div class="table-wrap compare"><table class="stack"><caption>{esc(caption)}</caption><thead><tr><th scope="col">Actor</th><th scope="col">What it collects</th>'
                '<th scope="col">You provide</th><th scope="col">Declared output fields</th><th scope="col">Price on the Free plan</th></tr></thead><tbody>'
                + "".join(rows) + "</tbody></table></div>")

    def search_form(self, actors, field_id="actor-search", placeholder="Filter by site, data or keyword"):
        options = "".join(f'<option value="{esc(c)}">{esc(category_name(c))}</option>' for c in sorted({c for a in actors for c in a["categories"]}))
        return (f'<form class="filter" action="{self.link("actors/")}" role="search"><div class="filter-input"><label for="{field_id}">Search Actors</label>'
                f'<input type="search" name="q" id="{field_id}" placeholder="{esc(placeholder)}" autocomplete="off"></div>'
                f'<div class="filter-select"><label for="category-filter">Topic</label><select id="category-filter" name="category"><option value="">All topics</option>{options}</select></div></form>'
                f'<p class="result-count" id="result-count" role="status" aria-live="polite">{len(actors)} Actors</p>')

    # ------------------------------------------------------------------ collection pages

    def copy(self, key, **values):
        text = COPY[self.theme][key]
        return text.format(**values) if values else text

    def home(self):
        headline = self.org.get("site", {}).get("headline", "Web data, ready to build with.")
        sites = sorted(self.platforms, key=lambda s: (-len(self.platforms[s]), s.casefold()))[:4]
        examples = f" for sites such as {join_words(sites)}" if sites else ""
        lead = esc(self.copy("lead", count=len(self.actors), examples=examples))
        index = "".join(f'<li><a href="{self.platform_href(name)}">{esc(name)}</a><span class="count">{len(members)}</span></li>' for name, members in self.platforms.items())
        topics = "".join(f'<li><a href="{self.link("topics/" + category_slug(c) + "/")}">{esc(category_name(c))}</a><span class="count">{sum(1 for a in self.actors if c in a["categories"])}</span></li>' for c in self.categories)
        featured = self.featured()[:6]
        steps = "".join(f"<li>{step}</li>" for step in COPY[self.theme]["steps"])
        body = (f'<section class="hero"><h1>{esc(headline)}</h1><p class="lead">{lead}</p>'
                f'<form class="hero-search" action="{self.link("actors/")}" role="search" data-search-index="{self.link("search.json")}">'
                f'<label for="home-search">{esc(self.copy("search_label"))}</label><div class="hero-search-row">'
                '<input type="search" role="combobox" id="home-search" name="q" placeholder="Try Airbnb, Google Maps reviews or job listings" autocomplete="off" aria-autocomplete="list" aria-controls="home-search-results" aria-expanded="false">'
                '<button type="submit">Search</button></div><ul id="home-search-results" class="search-results" role="listbox" hidden></ul></form></section>'
                f'<section class="block" aria-labelledby="sites-heading"><div class="block-head"><h2 id="sites-heading">{esc(self.copy("sites_title"))}</h2><p>{esc(self.copy("sites_note", sites=len(self.platforms)))}</p></div>'
                f'<ul class="site-index" role="list">{index}</ul></section>'
                f'<section class="block" aria-labelledby="featured-heading"><div class="block-head"><h2 id="featured-heading">{esc(self.copy("featured"))}</h2><p><a href="{self.link("actors/")}">See all {len(self.actors)} Actors</a></p></div>'
                f'{self.actor_rows(featured)}</section>'
                f'<section class="block" aria-labelledby="topics-heading"><div class="block-head"><h2 id="topics-heading">Browse by topic</h2><p>Topics are the categories each Actor declares on Apify.</p></div>'
                f'<ul class="topic-index" role="list">{topics}</ul></section>'
                f'<section class="block how" aria-labelledby="how-heading"><h2 id="how-heading">{esc(self.copy("how_title"))}</h2><ol class="steps">{steps}</ol></section>')
        description = f"{self.brand} documents {len(self.actors)} Apify Actors: output fields, input examples, Free-plan prices and API code in Python, JavaScript and cURL."
        self.page("", self.brand + " Apify Actor documentation", description, body, kind="CollectionPage", search=False,
                  extra_nodes=[self.item_list(featured, self.base + "#featured")])

    def item_list(self, actors, node_id):
        return {"@type": "ItemList", "@id": node_id, "itemListElement": [
            {"@type": "ListItem", "position": i, "url": self.base + self.doc_path(a), "name": a["title"]} for i, a in enumerate(actors, start=1)]}

    def catalog(self):
        body = (f'<section class="intro"><h1>All {len(self.actors)} Actors</h1><p class="lead">Every public Actor {esc(self.brand)} publishes on Apify, A to Z. '
                'Filter by the site you need, the data you want or a topic.</p></section>'
                + self.search_form(self.actors) + self.actor_rows(self.actors, level=2)
                + '<p id="empty-results" class="empty" hidden>No Actor matches. Try the site name alone, such as "Amazon", or clear the topic.</p>')
        description = f"Browse all {len(self.actors)} Apify Actors from {self.brand}, with what each one collects and its price per 1,000 results on the Free plan."
        self.page("actors/", "All Apify Actors", description, body, active="actors", search=False, crumbs=[("Actors", "actors/")],
                  extra_nodes=[self.item_list(self.actors, self.base + "actors/#list")])

    def topic(self, category):
        actors = [a for a in self.actors if category in a["categories"]]
        name = category_name(category)
        path = "topics/" + category_slug(category) + "/"
        sites = sorted({self.platform[a["id"]] for a in actors if self.platform[a["id"]]}, key=str.casefold)
        chips = "".join(f'<li><a href="{self.platform_href(s)}">{esc(s)}</a></li>' for s in sites)
        body = (f'<section class="intro"><h1>{esc(name)} Actors</h1><p class="lead">{len(actors)} {esc(self.brand)} Actors declare the {esc(name)} category on Apify'
                + (f", reading {len(sites)} different sites" if len(sites) > 1 else "") + '. Compare what each collects, what it needs from you and what it costs.</p></section>'
                + (f'<section class="block"><h2>Sites in this topic</h2><ul class="chips" role="list">{chips}</ul></section>' if chips else "")
                + f'<section class="block"><h2>Compare the {esc(name.lower())} Actors</h2>' + self.compare_table(actors, f"{name} Actors from {self.brand}") + "</section>")
        description = f"{len(actors)} {name.lower()} Apify Actors from {self.brand} compared: what each collects, required inputs, output fields and Free-plan price."
        self.page(path, fit_title(f"{name} Apify Actors", f": {len(actors)} compared"), description, body, active="topics",
                  crumbs=[("Topics", "topics/"), (name, path)], extra_nodes=[self.item_list(actors, self.base + path + "#list")],
                  noindex=len(actors) < INDEX_MINIMUM)

    def topics_index(self):
        items = "".join(f'<li><a href="{self.link("topics/" + category_slug(c) + "/")}">{esc(category_name(c))}</a><span class="count">{sum(1 for a in self.actors if c in a["categories"])}</span></li>' for c in self.categories)
        body = (f'<section class="intro"><h1>Browse by topic</h1><p class="lead">Each Actor declares one or more categories on Apify. '
                f'These {len(self.categories)} topics group the {len(self.actors)} Actors by them; an Actor can appear in several.</p></section>'
                f'<ul class="topic-index" role="list">{items}</ul>')
        self.page("topics/", "Apify Actors by topic", f"{len(self.categories)} topics grouping {self.brand}'s {len(self.actors)} Apify Actors by their declared category.",
                  body, active="topics", crumbs=[("Topics", "topics/")])

    def sites_index(self):
        letters = {}
        for name in self.platforms:
            letter = name[0].upper() if name[0].isalpha() else "0-9"
            letters.setdefault(letter, []).append(name)
        groups = "".join(f'<section class="letter" aria-label="{esc(letter)}"><h2>{esc(letter)}</h2><ul role="list">'
                         + "".join(f'<li><a href="{self.platform_href(n)}">{esc(n)}</a><span class="count">{len(self.platforms[n])}</span></li>' for n in names)
                         + "</ul></section>" for letter, names in letters.items())
        others = [a for a in self.actors if not self.platform[a["id"]]]
        body = (f'<section class="intro"><h1>Find an Actor by site</h1><p class="lead">{len(self.platforms)} sites and the {esc(self.brand)} Actors that read them. '
                'Sites with more than one Actor open a comparison page; the rest go straight to the Actor.</p></section>'
                f'<div class="az">{groups}</div>'
                + (f'<section class="block"><h2>Tools that are not tied to one site</h2>{self.actor_rows(others)}</section>' if others else ""))
        self.page("sites/", "Apify Actors by website", f"Find {self.brand}'s Apify Actors by the website they read: {len(self.platforms)} sites from A to Z.",
                  body, active="sites", crumbs=[("Sites", "sites/")])

    def site_hub(self, name):
        actors = self.platforms[name]
        path = self.hubs[name]
        prices = [(facts.per_thousand(self.pricing[a["id"]], "FREE"), a) for a in actors]
        known = [p for p in prices if p[0] is not None]
        range_text = ""
        if known:
            low, high = min(p[0] for p in known), max(p[0] for p in known)
            range_text = (f" Prices on the Free plan run from {facts.money(low)} to {facts.money(high)} per 1,000 results." if low != high
                          else f" Each costs {facts.money(low)} per 1,000 results on the Free plan.")
        picks = "".join(f'<li><a href="{self.link(self.doc_path(a))}">{esc(a["title"])}</a>: {esc(a["description"])}</li>' for a in actors)
        body = (f'<section class="intro"><h1>{esc(name)} scrapers and data tools</h1><p class="lead">{esc(self.brand)} publishes {len(actors)} Apify Actors that read {esc(name)}. '
                f'Each one answers a different question, so pick by the data you need.{range_text}</p></section>'
                f'<section class="block"><h2>Which {esc(name)} Actor do you need?</h2><ul class="picks">{picks}</ul></section>'
                f'<section class="block"><h2>Side by side</h2>{self.compare_table(actors, f"{name} Actors compared")}</section>'
                f'<p class="source-note">Prices are the Actors\' published pay-per-event prices for the Free plan; paid plans pay less per result, and Apify platform usage is billed separately. '
                f'Field counts come from each Actor\'s declared dataset views.</p>')
        description = f"Compare {len(actors)} {name} scrapers on Apify from {self.brand}: what each collects, required input, output fields and price per 1,000 results."
        self.page(path, fit_title(f"{name} scrapers", f": {len(actors)} Apify Actors compared", " compared"), description, body, active="sites",
                  crumbs=[("Sites", "sites/"), (name, path)], extra_nodes=[self.item_list(actors, self.base + path + "#list")],
                  noindex=len(actors) < INDEX_MINIMUM)

    def featured(self):
        preferred = self.org.get("site", {}).get("featured_actor_ids", [])
        indexed = {a["id"]: a for a in self.actors}
        return [indexed[i] for i in preferred if i in indexed] + [a for a in self.actors if a["id"] not in preferred]

    def guides_index(self):
        rows = "".join(f'<li><a href="{self.link(self.doc_path(a, "guides"))}">{esc(self.guide_title(a))}</a><p>{esc(a["description"])}</p></li>' for a in self.actors)
        body = (f'<section class="intro"><h1>Export tutorials</h1><p class="lead">One tutorial per Actor: run it through the Apify API from Python, JavaScript or one HTTP call, '
                'and save the results as CSV, Excel or JSON with the columns its dataset declares.</p></section>'
                f'<ul class="guide-index" role="list">{rows}</ul>')
        self.page("guides/", "Export Apify Actor data to CSV and Excel", f"Tutorials for exporting the results of {len(self.actors)} {self.brand} Apify Actors to CSV, Excel or JSON from Python, JavaScript or cURL.",
                  body, active="guides", crumbs=[("Guides", "guides/")])

    # ------------------------------------------------------------------ Actor reference

    def facts_list(self, actor):
        schema = actor.get("input_schema") or {}
        properties = schema.get("properties") or {}
        required = [k for k in (schema.get("required") or []) if k in properties]
        rows = []
        if actor.get("build_finished_at"):
            rows.append(("Updated", f'<time datetime="{esc(actor["build_finished_at"][:10])}">{esc(date_text(actor["build_finished_at"]))}</time>'))
        price = self.price_phrase(actor)
        if price:
            rows.append(("Free plan", esc(price)))
        gold = self.price_phrase(actor, "GOLD")
        if gold and gold != price:
            rows.append(("Business plan", esc(gold)))
        rows.append(("Input", f"{len(properties)} field{'s' if len(properties) != 1 else ''}" + (f", {len(required)} required" if required else ", none required")))
        fields = facts.dataset_fields(actor)
        if fields:
            rows.append(("Output", f"{len(fields)} declared fields"))
        platform = self.platform[actor["id"]]
        if platform:
            rows.append(("Site", f'<a href="{self.platform_href(platform)}">{esc(platform)}</a>'))
        return '<dl class="facts">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows) + "</dl>"

    def summary(self, actor):
        """An answer-first paragraph built only from the published definition: what it is,
        what you give it, what comes back, and what it costs."""
        schema = actor.get("input_schema") or {}
        properties = schema.get("properties") or {}
        required = [k for k in (schema.get("required") or []) if k in properties]
        text = f"{esc(actor['title'])} is an Apify Actor published by {esc(self.brand)}. "
        if properties:
            text += f"It accepts {len(properties)} input field{'s' if len(properties) != 1 else ''}"
            if required:
                names = [f"<code>{esc(k)}</code>" for k in required]
                text += ", and " + join_words(names) + (" is" if len(names) == 1 else " are") + " required. "
            else:
                text += ", none of them required at the top level. "
        fields = facts.dataset_fields(actor)
        if fields:
            shown = [f"<code>{esc(f)}</code>" for f, _, _ in fields[:6]]
            text += f"Each result can carry up to {len(fields)} declared fields, including {join_words(shown)}. "
        else:
            text += "Its build declares no dataset fields; the published README describes the output. "
        summary = self.pricing.get(actor["id"])
        free = facts.per_thousand(summary, "FREE")
        if free is not None:
            noun = facts.result_noun(summary)
            text += f"It costs {facts.money(free)} per 1,000 {esc(noun)}s on Apify's Free plan"
            gold = facts.per_thousand(summary, "GOLD")
            if gold is not None and gold != free:
                text += f" and {facts.money(gold)} on the Business plan"
            text += "."
        else:
            text += "Runs happen on Apify, where the Store page lists the current price."
        return f'<p class="summary" id="summary">{text}</p>'

    def code_samples(self, actor, prefix, run_input):
        ident = f"{actor['username']}/{actor['name']}"
        api_id = f"{actor['username']}~{actor['name']}"
        body = json.dumps(run_input, indent=2, ensure_ascii=False)
        python = ("# pip install apify-client\nimport os\nfrom apify_client import ApifyClient\n\n"
                  f'ACTOR = "{ident}"\nclient = ApifyClient(os.environ["APIFY_TOKEN"])\n'
                  f"run_input = {py_literal(run_input)}\n\n"
                  f'run = client.actor(ACTOR).call(run_input=run_input)\n'
                  'for item in client.dataset(run["defaultDatasetId"]).iterate_items():\n    print(item)\n')
        javascript = ("// npm install apify-client\nimport { ApifyClient } from 'apify-client';\n\n"
                      f"const ACTOR = '{ident}';\nconst client = new ApifyClient({{ token: process.env.APIFY_TOKEN }});\n"
                      f"const input = {body};\n\n"
                      "const run = await client.actor(ACTOR).call(input);\n"
                      "const { items } = await client.dataset(run.defaultDatasetId).listItems();\nconsole.log(items);\n")
        curl = (f'curl -X POST "https://api.apify.com/v2/acts/{api_id}/run-sync-get-dataset-items?format=json" \\\n'
                '  -H "Authorization: Bearer $APIFY_TOKEN" \\\n  -H "Content-Type: application/json" \\\n'
                f"  -d {shell_quote(json.dumps(run_input, ensure_ascii=False))}\n")
        mcp = json.dumps({"mcpServers": {"apify": {"url": f"https://mcp.apify.com?tools={ident}"}}}, indent=2)
        tabs = [("python", "Python", python, "python"), ("javascript", "JavaScript", javascript, "javascript"),
                ("curl", "cURL", curl, "bash"), ("mcp", "MCP", mcp, "json")]
        # The final tab state is rendered here (first panel active, the rest hidden by CSS), so the
        # script changes nothing visible at load: hiding panels from script forced a full relayout of
        # long pages after first paint (1.1-1.6 s long tasks in Lighthouse). Tabs are links, so
        # without JavaScript the :target rule still switches panels.
        buttons = "".join(f'<a role="tab" href="#{prefix}-panel-{k}" id="{prefix}-tab-{k}" aria-controls="{prefix}-panel-{k}" aria-selected="{"true" if i == 0 else "false"}"'
                          + ("" if i == 0 else ' tabindex="-1"') + f'>{label}</a>' for i, (k, label, _, _) in enumerate(tabs))
        panels = "".join(f'<div role="tabpanel" id="{prefix}-panel-{k}" aria-labelledby="{prefix}-tab-{k}" class="tab-panel{" active" if i == 0 else ""}">'
                         f'{code_block(code, f"{prefix}-{k}", lang)}</div>' for i, (k, label, code, lang) in enumerate(tabs))
        return f'<div class="tabs" data-tabs><div class="tab-list" role="tablist" aria-label="Language">{buttons}</div>{panels}</div>'

    def cost_section(self, actor):
        summary = self.pricing.get(actor["id"])
        if not summary or not summary["primary"]:
            return ""
        noun = facts.result_noun(summary)
        rows = []
        for tier, label in facts.TIERS:
            per = facts.event_price(summary["primary"], tier)
            if per is None:
                continue
            start = facts.event_price(summary["start"], tier) if summary["start"] else None
            cells = [facts.money(per), facts.money(per * 1000)]
            cells.append(facts.money(start) if start is not None else "None")
            for count in (100, 1000, 10000):
                cells.append(facts.money2(facts.run_cost(summary, tier, count)))
            heads = [f"Per {noun}", "Per 1,000", "Start fee", f"100 {noun}s", f"1,000 {noun}s", f"10,000 {noun}s"]
            rows.append(f'<tr><th scope="row">{label}</th>' + "".join(f'<td data-label="{esc(h)}">{c}</td>' for h, c in zip(heads, cells)) + "</tr>")
        if not rows:
            return ""
        memory = summary["memory_mb"]
        start_note = ""
        if summary["start"]:
            start_note = (f" The start fee is charged once per GB of run memory (at least once); the default run uses {memory // 1024 if memory >= 1024 else memory} "
                          f"{'GB' if memory >= 1024 else 'MB'}, so a run starts with {summary['start_events']} start event{'s' if summary['start_events'] != 1 else ''}, as the run totals include."
                          if memory else " The start fee is charged once per GB of run memory, at least once.")
        others = "".join(f'<li><strong>{esc(e["title"])}</strong>: {esc(facts.money(facts.event_price(e, "FREE")))} on the Free plan. {esc(e["description"])}</li>'
                         for e in summary["others"] if facts.event_price(e, "FREE") is not None)
        platform = (" You also pay Apify platform usage (compute and proxy) for the run, which these totals do not include."
                    if summary["platform_extra"] else " Platform usage is included in these prices.")
        return (f'<section id="cost"><h2>What it costs</h2><p>{esc(actor["title"])} uses pay-per-event pricing: a fee for each {esc(noun)} saved to the dataset, '
                f'plus a start fee per run. Paid Apify plans pay less per {esc(noun)}.{start_note}{platform}</p>'
                f'<div class="table-wrap"><table class="price-table stack"><caption>Published prices and run totals by Apify plan</caption><thead><tr><th scope="col">Plan</th>'
                f'<th scope="col">Per {esc(noun)}</th><th scope="col">Per 1,000</th><th scope="col">Start fee</th><th scope="col">100 {esc(noun)}s</th>'
                f'<th scope="col">1,000 {esc(noun)}s</th><th scope="col">10,000 {esc(noun)}s</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
                + (f'<p>Other events this Actor can charge:</p><ul>{others}</ul>' if others else "")
                + f'<p class="fine">Run totals are the Actor\'s charges at the default memory: start fees plus the per-{esc(noun)} price. Check the <a href="{actor["url"]}">Store page</a> before a large run; prices can change with notice.</p></section>')

    def input_reference(self, actor, notes_html=""):
        schema = actor.get("input_schema") or {}
        properties = schema.get("properties") or {}
        if not properties:
            return '<section id="input"><h2>Input</h2><p>The published input schema declares no fields.</p>' + notes_html + "</section>"
        required = set(schema.get("required") or [])
        rows = []
        for field, prop in properties.items():
            prop = prop if isinstance(prop, dict) else {}
            kind = prop.get("type", "any")
            kind = " or ".join(kind) if isinstance(kind, list) else kind
            default = facts.describe_value(prop["default"]) if "default" in prop else ""
            example = facts.describe_value(prop["prefill"]) if "prefill" in prop and not facts.SECRET_FIELD.search(field) else ""
            allowed = facts.allowed_values(prop)
            details = []
            if default:
                details.append(f"Default <code>{esc(default)}</code>")
            if example and example != default:
                details.append(f"Example <code>{esc(example)}</code>")
            if allowed:
                details.append(f"Allowed {esc(allowed)}")
            title = prop.get("title") or ""
            description = prop.get("description") or ""
            rows.append(f'<tr><th scope="row"><code>{esc(field)}</code>' + (f'<span class="field-title">{esc(title)}</span>' if title else "") + "</th>"
                        f'<td data-label="Type">{esc(kind)}' + (' <span class="req">required</span>' if field in required else "") + "</td>"
                        f'<td data-label="Description">{inline_md(description) if description else ""}' + (f'<span class="field-meta">{"; ".join(details)}</span>' if details else "") + "</td></tr>")
        table = split_table("input-table", "Input fields in the published schema", ["Field", "Type", "Description"], rows, 12, "input fields")
        return (f'<section id="input"><h2>Input reference</h2><p>All {len(properties)} fields of the published input schema, in the publisher\'s order. '
                + ("Required fields are marked. " if required else "No field is required at the top level, but the README can describe conditions. ")
                + f'Download the <a href="input-schema.json">input schema</a> as JSON.</p>{table}{notes_html}</section>')

    def output_section(self, actor, readme_html, notes):
        """The output contract as one table: every field the dataset views declare, with the
        publisher's label and what the README says about it, then fields only the README names."""
        fields = facts.dataset_fields(actor)
        views = facts.dataset_views(actor)
        record = facts.sample_record(actor)
        declared = {f for f, _, _ in fields}
        extra = [f for f in notes if f not in declared]
        parts = [f'<section id="output"><h2>What you get</h2>']
        if fields or notes:
            sentence = "The Actor saves one record per result to an Apify dataset. "
            if fields:
                sentence += f'Its build declares {len(fields)} field{"s" if len(fields) != 1 else ""} in {len(views)} dataset view{"s" if len(views) != 1 else ""}'
                sentence += f", and the README documents {len(extra)} more" if extra else ""
                sentence += ". "
            else:
                sentence += f"The build declares no dataset view; the README documents {len(notes)} fields. "
            sentence += "Fields without a value can be left out of a record."
            parts.append(f"<p>{sentence}</p>")
            rows = []
            for field, label, description in fields + [(f, "", "") for f in extra]:
                note = notes.get(field) or description
                rows.append(f'<tr><th scope="row"><code>{esc(field)}</code></th><td data-label="Label">{esc(label)}</td>'
                            f'<td data-label="What it holds">{inline_md(note) if note else ""}</td></tr>')
            parts.append(split_table("output-table", "Output fields", ["Field", "Label", "What it holds"], rows, 20, "output fields"))
        else:
            parts.append('<p>The build declares no dataset fields. The publisher\'s notes below describe the records.</p>')
        if record:
            parts.append(code_block(json.dumps(record["record"], indent=2, ensure_ascii=False), "sample-record", "json",
                                    "Sample record from the publisher's README" + (f" ({record['heading']})" if record["heading"] else "")))
        if readme_html and notes:
            parts.append(f'<details class="publisher-notes"><summary>The publisher\'s output notes</summary>{readme_html}</details>')
        else:
            parts.append(readme_html)
        if actor.get("output_schema") is None:
            parts.append('<p class="fine">The output schema is not present in the default published build.</p>')
        parts.append("</section>")
        return "".join(parts)

    def actor_page(self, actor):
        actor_id = actor["id"]
        path = self.doc_path(actor)
        intro, sections = facts.split_sections(actor["readme"])
        used = {}
        anchors = {}
        kinds = {}
        for section in sections:
            kinds.setdefault(section["kind"], []).append(section)
            anchors[re.sub(r"[^a-z0-9]+", "-", section["title"].casefold()).strip("-")] = anchor_id(section["title"])

        def render(section, our_heading=None):
            heading = esc(our_heading if our_heading is not None else section["title"])
            section_id = anchor_id(section["title"])
            used[section_id] = used.get(section_id, 0) + 1
            if used[section_id] > 1:
                section_id += "-" + str(used[section_id])
            return f'<h3 id="{section_id}">{heading}</h3>' + readme_html(markdown(section["body"], used, anchors, shift=1))

        toc = [("summary", "In short")]
        content = self.summary(actor)
        what = "".join(render(s) for s in kinds.get("what", []) + kinds.get("usecases", []))
        if intro.strip() or what:
            content += '<section id="about"><h2>What it does</h2>' + (readme_html(markdown(intro, used, anchors, shift=1)) if intro.strip() else "") + what + "</section>"
            toc.append(("about", "What it does"))
        content += self.output_section(actor, "".join(render(s) for s in kinds.get("output", [])), facts.readme_field_notes(sections))
        toc.append(("output", "What you get"))
        run_input, label = facts.best_input(actor)
        examples = "".join(render(s) for s in kinds.get("examples", []))
        content += (f'<section id="run"><h2>Run it</h2><p>Set <code>APIFY_TOKEN</code> to your <a href="https://console.apify.com/settings/integrations">Apify API token</a>, '
                    f'then run the Actor with the input below ({esc(label.lower() if label[0].isupper() and not label[1:2].isupper() else label)}). Each run is billed to your Apify account. '
                    f'The <a href="{self.link(self.doc_path(actor, "guides"))}">export tutorial</a> turns the results into a CSV file or an Excel workbook.</p>'
                    + self.code_samples(actor, "run", run_input)
                    + (f'<div class="examples" id="example-inputs"><p class="examples-intro">More inputs from the publisher\'s README:</p>{examples}</div>' if examples else "") + "</section>")
        toc.append(("run", "Run it"))
        cost = self.cost_section(actor)
        if cost:
            cost = cost.replace("</section>", "".join(render(s) for s in kinds.get("cost", [])) + "</section>") if kinds.get("cost") else cost
            content += cost
            toc.append(("cost", "What it costs"))
        notes = "".join(render(s) for s in kinds.get("input", []))
        notes_html = f'<details class="publisher-notes"><summary>The publisher\'s input notes</summary>{notes}</details>' if notes else ""
        content += self.input_reference(actor, notes_html)
        toc.append(("input", "Input reference"))
        faq = facts.faq_items(sections)
        faq_nodes = []
        if faq:
            questions = []
            for question, answer in faq:
                qid = anchor_id(question, "faq-")
                used[qid] = used.get(qid, 0) + 1
                if used[qid] > 1:
                    qid += "-" + str(used[qid])
                questions.append(f'<div class="qa"><h3 id="{qid}">{inline_md(question)}</h3>{readme_html(markdown(answer, used, anchors, shift=2))}</div>')
                faq_nodes.append({"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": plain(answer)[:500]}})
            content += f'<section id="faq"><h2>Questions</h2>{"".join(questions)}</section>'
            toc.append(("faq", "Questions"))
        elif kinds.get("faq"):
            content += '<section id="faq"><h2>Questions</h2>' + "".join(render(s) for s in kinds["faq"]) + "</section>"
            toc.append(("faq", "Questions"))
        rest = kinds.get("limits", []) + kinds.get("other", [])
        rest.sort(key=lambda s: sections.index(s))
        if rest:
            content += '<section id="notes"><h2>Limits and notes</h2>' + "".join(render(s) for s in rest) + "</section>"
            toc.append(("notes", "Limits and notes"))
        related = self.related(actor)
        if related:
            content += related
            toc.append(("related", "Related Actors"))
        content += (f'<section id="files"><h2>Source files</h2><p>This page is rebuilt from the default published build <code>{esc(actor["build_id"])}</code>. '
                    'Download what it was built from: '
                    f'<a href="README.md">README</a>, <a href="input-schema.json">input schema</a>, <a href="output-schema.json">output schema</a>, '
                    f'<a href="dataset-schema.json">dataset schema</a>, <a href="key-value-schema.json">key-value store schema</a>.</p></section>')
        contents = '<nav class="toc" aria-label="On this page"><h2 class="toc-title">On this page</h2><ol>' + "".join(f'<li><a href="#{k}">{v}</a></li>' for k, v in toc) + "</ol></nav>"
        cta = (f'<div class="cta"><a class="button" href="{actor["url"]}">Open in Apify Store</a>'
               f'<a class="button secondary" href="#run">Copy the API call</a></div>')
        head = (f'<div class="doc-head"><h1>{esc(actor["title"])}</h1><p class="lead">{esc(actor["description"])}</p>'
                f'{self.facts_list(actor)}{cta}</div>')
        page_body = f'<div class="doc">{head}<div class="doc-body">{contents}<article class="prose">{content}</article></div></div>'
        platform = self.platform[actor_id]
        crumbs = ([("Sites", "sites/"), (platform, self.hubs[platform])] if platform in self.hubs
                  else [("Topics", "topics/"), (category_name(self.primary_category(actor)), "topics/" + category_slug(self.primary_category(actor)) + "/")])
        crumbs.append((actor["title"], path))
        extra = [self.software_node(actor)]
        if faq_nodes:
            extra.append({"@type": "FAQPage", "@id": self.base + path + "#faq", "mainEntity": faq_nodes, "isPartOf": {"@id": self.base + path + "#webpage"}})
        price = self.price_phrase(actor)
        description = actor["description"]
        if price and len(description) + len(price) < 190:
            description += f" From {price} on the Free plan."
        title = fit_title(actor["title"], " – docs, price and API", " – docs and price", " docs")
        self.page(path, title, description, page_body, "TechArticle", active="actors", modified=actor.get("build_finished_at"),
                  image=actor.get("picture_url"), crumbs=crumbs, extra_nodes=extra)
        for key in ("input_schema", "output_schema", "dataset_schema", "key_value_schema"):
            self.files[path + key.replace('_', '-') + ".json"] = json_text(actor.get(key))
        self.files[path + "README.md"] = actor["readme"]

    def software_node(self, actor):
        node = {"@type": "SoftwareApplication", "@id": self.base + self.doc_path(actor) + "#software", "name": actor["title"],
                "description": actor["description"], "url": actor["url"], "applicationCategory": "DeveloperApplication",
                "operatingSystem": "Apify platform (web)", "publisher": {"@id": self.base + "#organization"}}
        if actor.get("picture_url"):
            node["image"] = actor["picture_url"]
        summary = self.pricing.get(actor["id"])
        per = facts.event_price(summary["primary"], "FREE") if summary and summary["primary"] else None
        if per is not None:
            node["offers"] = {"@type": "Offer", "url": actor["url"], "priceCurrency": "USD", "price": "0",
                              "priceSpecification": {"@type": "UnitPriceSpecification", "price": per, "priceCurrency": "USD",
                                                     "unitText": facts.result_noun(summary), "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitText": facts.result_noun(summary)}},
                              "description": "Pay per event: the price per result on Apify's Free plan; a start fee and platform usage are billed separately."}
        return node

    def related(self, actor):
        platform = self.platform[actor["id"]]
        same_site = [a for a in self.platforms.get(platform, []) if a["id"] != actor["id"]] if platform else []
        category = self.primary_category(actor)
        same_topic = [a for a in self.actors if a["id"] != actor["id"] and category in a["categories"] and a not in same_site]
        picks = (same_site + same_topic)[:6]
        if not picks:
            return ""
        items = "".join(f'<li><a href="{self.link(self.doc_path(a))}">{esc(a["title"])}</a><p>{esc(a["description"])}</p></li>' for a in picks)
        more = []
        if platform in self.hubs:
            more.append(f'<a href="{self.link(self.hubs[platform])}">Compare all {len(self.platforms[platform])} {esc(platform)} Actors</a>')
        more.append(f'<a href="{self.link("topics/" + category_slug(category) + "/")}">All {esc(category_name(category).lower())} Actors</a>')
        return f'<section id="related"><h2>Related Actors</h2><ul class="related" role="list">{items}</ul><p class="more">{" ".join(more)}</p></section>'

    # ------------------------------------------------------------------ export tutorial

    def guide_title(self, actor):
        return fit_title(actor["title"], ": export to CSV, Excel or JSON", ": CSV and Excel export", " export", limit=78)

    def export_columns(self, actor, limit=8):
        """The columns a reader exports by default: the first dataset view's fields with their
        display labels (the publisher's own table layout), topped up from the other views."""
        views = facts.dataset_views(actor)
        columns = []
        for view in views:
            for field, label in view["fields"]:
                if field not in [c[0] for c in columns]:
                    columns.append((field, label or field))
            if len(columns) >= limit:
                break
        return columns[:limit]

    def guide_indexable(self, actor):
        # Indexed only when the tutorial is specific to this Actor: real declared columns to export.
        return len(facts.dataset_fields(actor)) >= 3 and bool(self.export_columns(actor))

    def guide_page(self, actor):
        path = self.doc_path(actor, "guides")
        reference = self.link(self.doc_path(actor))
        ident = f"{actor['username']}/{actor['name']}"
        api_id = f"{actor['username']}~{actor['name']}"
        schema = actor.get("input_schema") or {}
        properties = schema.get("properties") or {}
        required = [k for k in (schema.get("required") or []) if k in properties]
        run_input, label = facts.best_input(actor)
        sample, missing = facts.schema_example(actor)
        limits = facts.limit_fields(actor)
        summary = self.pricing.get(actor["id"])
        columns = self.export_columns(actor)
        views = facts.dataset_views(actor)
        title = self.guide_title(actor)
        noun = facts.result_noun(summary)
        body = [f'<article class="prose guide"><h1>{esc(title)}</h1><p class="lead">{esc(actor["description"])}</p>'
                f'<p class="summary" id="summary">This tutorial runs {esc(actor["title"])} through the Apify API and saves what it returns as a CSV file, an Excel workbook or JSON'
                + (f', keeping the {len(columns)} columns its publisher puts first: ' + join_words(f"<code>{esc(f)}</code>" for f, _ in columns) + "." if columns else ".")
                + "</p>"]
        steps = [("columns", "See the columns"), ("token", "Get an API token"), ("input", "Choose the input"), ("csv", "Run it and write a CSV"),
                 ("excel", "Download Excel or JSON"), ("javascript", "The same in JavaScript"), ("trouble", "Fix common problems")]
        if not columns:
            steps = steps[1:]
        body.append('<nav class="toc inline" aria-label="Steps"><h2 class="toc-title">Steps</h2><ol>' + "".join(f'<li><a href="#{k}">{v}</a></li>' for k, v in steps) + "</ol></nav>")
        intro_text, sections = facts.split_sections(actor["readme"])
        notes = facts.readme_field_notes(sections)
        page_ids = {}  # one ID space for every README fragment on this page

        def here(fragment):
            # README links to its own sections live on the reference page, not on this guide.
            return re.sub(r'href="#[^"]*"', f'href="{reference}"', fragment)
        if columns:
            rows = "".join(f'<tr><td><code>{esc(f)}</code></td><td data-label="Column header">{esc(l)}</td><td data-label="What it holds">{inline_md(notes[f]) if notes.get(f) else ""}</td></tr>'
                           for f, l in columns)
            view_names = join_words(f'"{esc(v["title"])}"' for v in views)
            body.append(f'<section id="columns"><h2>The columns you can export</h2><p>The Actor\'s build declares {len(facts.dataset_fields(actor))} output fields '
                        f'in {len(views)} dataset view{"s" if len(views) != 1 else ""} ({view_names}). The export below keeps these, under the labels the publisher gave them:</p>'
                        f'<div class="table-wrap"><table><caption>Default export columns</caption><thead><tr><th scope="col">Field</th><th scope="col">Column header</th><th scope="col">What it holds</th></tr></thead>'
                        f'<tbody>{rows}</tbody></table></div><p>Swap in any field from the <a href="{reference}#output">output reference</a> to export it too.</p></section>')
        uses = [x for x in sections if x["kind"] == "usecases"]
        if uses:
            body.append('<section id="uses"><h2>What people export it for</h2>' + readme_html(here(markdown(uses[0]["body"], page_ids, {}, shift=1))) + "</section>")
        body.append('<section id="token"><h2>Get an API token</h2><p>Copy it from '
                    '<a href="https://console.apify.com/settings/integrations">Console, Settings, API and Integrations</a>.</p>'
                    + code_block('export APIFY_TOKEN="your-token"', "token-export", "bash") + "</section>")
        input_text = '<section id="input"><h2>Choose the input</h2>'
        if required:
            described = []
            for key in required:
                prop = properties.get(key) or {}
                note = prop.get("description") or prop.get("title") or ""
                described.append(f"<li><code>{esc(key)}</code>" + (f": {inline_md(note)}" if note else "") + "</li>")
            input_text += f'<p>{len(required)} field{"s are" if len(required) != 1 else " is"} required:</p><ul>{"".join(described)}</ul>'
        else:
            input_text += '<p>No field is required at the top level, so the input below runs as it is. Change it to point at your own data.</p>'
        if missing:
            input_text += '<p class="note">The schema gives no example for ' + join_words(f"<code>{esc(x)}</code>" for x in missing) + '; supply a value before you run it.</p>'
        input_text += f'<p>Save this as <code>input.json</code> ({esc(label[0].lower() + label[1:] if label[:1].isupper() and not label[1:2].isupper() else label)}):</p>' + code_block(json.dumps(run_input, indent=2, ensure_ascii=False), "guide-input", "json", "input.json")
        if limits:
            items = []
            for item in limits:
                bits = []
                if item["default"] is not None:
                    bits.append(f"default {esc(item['default'])}")
                if item["maximum"] is not None:
                    bits.append(f"maximum {esc(item['maximum'])}")
                items.append(f"<li><code>{esc(item['field'])}</code>" + (f" ({', '.join(bits)})" if bits else "") + "</li>")
            input_text += f'<p>Keep the first export small. These fields cap how many {esc(noun)}s a run collects, and so what it costs:</p><ul>{"".join(items)}</ul>'
        input_text += f'<p>The <a href="{reference}#input">input reference</a> lists every field.</p></section>'
        body.append(input_text)
        if columns:
            column_lines = "".join(f"    {json.dumps(f, ensure_ascii=False)}: {json.dumps(l, ensure_ascii=False)},\n" for f, l in columns)
            python = ("# pip install apify-client\nimport csv\nimport json\nimport os\n\nfrom apify_client import ApifyClient\n\n"
                      "# Field -> column header, from the Actor's dataset view.\nCOLUMNS = {\n" + column_lines + "}\n\n"
                      f'ACTOR = "{ident}"\nclient = ApifyClient(os.environ["APIFY_TOKEN"])\n'
                      'with open("input.json", encoding="utf-8") as f:\n    run_input = json.load(f)\n\n'
                      f'run = client.actor(ACTOR).call(run_input=run_input)\n'
                      'print("Run", run["id"], run["status"])\n\n\n'
                      "def cell(value):\n    # Lists and objects become JSON text so they fit in one cell.\n"
                      "    return json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value\n\n\n"
                      'with open("results.csv", "w", newline="", encoding="utf-8") as f:\n    writer = csv.writer(f)\n    writer.writerow(COLUMNS.values())\n'
                      '    for item in client.dataset(run["defaultDatasetId"]).iterate_items():\n        writer.writerow([cell(item.get(field)) for field in COLUMNS])\n')
        else:
            python = ("# pip install apify-client\nimport json\nimport os\n\nfrom apify_client import ApifyClient\n\n"
                      f'ACTOR = "{ident}"\nclient = ApifyClient(os.environ["APIFY_TOKEN"])\n'
                      'with open("input.json", encoding="utf-8") as f:\n    run_input = json.load(f)\n\n'
                      f'run = client.actor(ACTOR).call(run_input=run_input)\n'
                      'items = list(client.dataset(run["defaultDatasetId"]).iterate_items())\n'
                      'with open("results.json", "w", encoding="utf-8") as f:\n    json.dump(items, f, ensure_ascii=False, indent=2)\n')
        body.append(f'<section id="csv"><h2>Run it and write a CSV</h2><p><code>call()</code> waits for the run to finish; the loop then reads the {esc(noun)}s page by page.</p>'
                    + code_block("pip install apify-client", "py-install", "bash") + code_block(python, "py-run", "python", "export.py") + "</section>")
        fields_param = ("&fields=" + ",".join(quote(f, safe="") for f, _ in columns)) if columns else ""
        one_call = (f'curl -X POST "https://api.apify.com/v2/acts/{api_id}/run-sync-get-dataset-items?format=xlsx{fields_param}" \\\n'
                    '  -H "Authorization: Bearer $APIFY_TOKEN" \\\n  -H "Content-Type: application/json" \\\n  -d @input.json -o results.xlsx\n')
        later = (f'curl -H "Authorization: Bearer $APIFY_TOKEN" \\\n  "https://api.apify.com/v2/datasets/DATASET_ID/items?format=json{fields_param}" -o results.json\n')
        body.append('<section id="excel"><h2>Download Excel or JSON</h2><p>One request runs it and returns the file'
                    + (' with just these columns' if columns else "")
                    + '. It waits at most 300 seconds (then HTTP 408 while the run carries on).</p>'
                    + code_block(one_call, "curl-xlsx", "bash")
                    + '<p>A finished run, by its dataset ID:</p>'
                    + code_block(later, "curl-dataset", "bash") + "</section>")
        js_fields = ("[" + ", ".join(json.dumps(f, ensure_ascii=False) for f, _ in columns) + "]") if columns else None
        javascript = ("// npm install apify-client   (Node.js 18+, save as export.mjs)\nimport { readFile, writeFile } from 'node:fs/promises';\nimport { ApifyClient } from 'apify-client';\n\n"
                      f"const ACTOR = '{ident}';\nconst client = new ApifyClient({{ token: process.env.APIFY_TOKEN }});\n"
                      "const input = JSON.parse(await readFile('input.json', 'utf8'));\n\n"
                      "const run = await client.actor(ACTOR).call(input);\n"
                      + (f"const csv = await client.dataset(run.defaultDatasetId).downloadItems('csv', {{ fields: {js_fields} }});\nawait writeFile('results.csv', csv);\n"
                         if js_fields else "const { items } = await client.dataset(run.defaultDatasetId).listItems();\nawait writeFile('results.json', JSON.stringify(items, null, 2));\n"))
        body.append('<section id="javascript"><h2>The same in JavaScript</h2>' + code_block("npm install apify-client", "js-install", "bash")
                    + code_block(javascript, "js-run", "javascript", "export.mjs") + "</section>")
        trouble = facts.troubleshooting(facts.faq_items(facts.split_sections(actor["readme"])[1]))
        answers = "".join(f'<div class="qa"><h3>{inline_md(q)}</h3>{readme_html(here(markdown(a, page_ids, {}, shift=2)))}</div>' for q, a in trouble[:3])
        more = "".join(f'<li><a href="{reference}#{anchor_id(q, "faq-")}">{inline_md(q)}</a></li>' for q, _ in trouble[3:8])
        body.append('<section id="trouble"><h2>Fix common problems</h2>' + answers + (f"<p>More from the publisher:</p><ul>{more}</ul>" if more else "")
                    + '<p>HTTP 401 means the token is missing; an empty file usually means the input matched nothing, which the run log in Console names.</p></section>')
        if summary and summary["primary"]:
            free = facts.per_thousand(summary, "FREE")
            body.append(f'<p>An export of 1,000 {esc(noun)}s costs {facts.money2(facts.run_cost(summary, "FREE", 1000))} in Actor charges on the Free plan, plus platform usage '
                        f'(<a href="{reference}#cost">all plans</a>).</p>')
        body.append(f'<div class="cta"><a class="button" href="{actor["url"]}">Open in Apify Store</a><a class="button secondary" href="{reference}">Read the full reference</a></div>')
        body.append(f'<p class="source-note">Built from the published build <code>{esc(actor["build_id"])}</code>: its README, input schema, dataset views and Store pricing.</p></article>')
        self.page(path, title, f"Export {actor['title']} results to CSV, Excel or JSON from Python, JavaScript or one API call, with the columns its dataset declares.",
                  "".join(body), "TechArticle", "guides", modified=actor.get("build_finished_at"), image=actor.get("picture_url"),
                  crumbs=[("Guides", "guides/"), (actor["title"], path)], noindex=not self.guide_indexable(actor))
        self.files[path + "input.example.json"] = json_text(sample)

    # ------------------------------------------------------------------ legacy addresses, indexes

    def legacy_paths(self, previous):
        """Addresses that were published before keep answering: an Actor's ID path (the
        original URL scheme) and an old name redirect to its readable page; an Actor that left
        the listing keeps a noindex notice. A current page always wins a path."""
        current = {a["id"]: a for a in self.actors}
        unavailable = ('<article class="prose"><h1>Actor unavailable</h1><p>This Actor is absent from the current public listing. '
                       'Browse the current catalog for available documentation.</p><p><a href="' + self.link("actors/") + '">View the current catalog</a></p></article>')
        for kind in ("actors", "guides"):
            moves = [(actor["id"], actor) for actor in self.actors]
            for old in previous:
                name = str(old.get("name") or "").lower()
                if old.get("id") in current and SLUG.fullmatch(name):
                    moves.append((name, current[old["id"]]))
            for path, actor in moves:
                target = self.doc_path(actor, kind)
                source = f"{kind}/{path}/"
                if source == target or source + "index.html" in self.files:
                    continue
                url = self.base + target
                self.page(source, "Moved: " + actor["title"], "This page moved to " + url,
                          f'<article class="prose"><h1>This page has moved</h1><p><a href="{self.link(target)}">{esc(actor["title"])}</a> has a new address.</p></article>',
                          active=kind, redirect=url)
            for old in previous:
                if old.get("id") in current or not ACTOR_ID.fullmatch(str(old.get("id", ""))):
                    continue
                name = str(old.get("name") or "").lower()
                for path in [old["id"]] + ([name] if SLUG.fullmatch(name) else []):
                    if f"{kind}/{path}/index.html" not in self.files:
                        self.page(f"{kind}/{path}/", "Actor unavailable", "This Actor is not in the current public listing.", unavailable, noindex=True)

    def llms(self):
        """llms.txt: what this site is and how it stays true, then every Actor with its reference
        and guide, grouped by topic so a model can find the right one by task."""
        lines = [f"# {self.brand} Actor documentation", "",
                 f"> Reference pages and API tutorials for the {len(self.actors)} public Apify Actors published by {self.brand}. "
                 "Every page is generated from the Actor's published README, input schema, output definitions and Store pricing, "
                 "and regenerated when the published build changes. Prices are the published pay-per-event prices; runs happen on Apify.", "",
                 f"- Catalog: {self.base}actors/", f"- Sites A to Z: {self.base}sites/", f"- Topics: {self.base}topics/", f"- Guides: {self.base}guides/",
                 f"- Machine-readable index: {self.base}actors.json", f"- Publisher on Apify: {self.apify}", ""]
        by_topic = {}
        for actor in self.actors:
            by_topic.setdefault(category_name(self.primary_category(actor)), []).append(actor)
        for topic in sorted(by_topic):
            lines += [f"## {topic}", ""]
            for a in by_topic[topic]:
                price = self.price_phrase(a)
                lines.append(f"- [{a['title']}]({self.base}{self.doc_path(a)}): {a['description']}"
                             + (f" Price: {price} on the Free plan." if price else "") + f" Export tutorial: {self.base}{self.doc_path(a, 'guides')}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def demote_similar(self):
        """Near-duplicate pages (publisher stubs, say) are consolidated, not published as scaled
        copies: of any indexable pair over SIMILARITY_LIMIT, the page with less of its own text
        becomes noindex and leaves the sitemap. The page stays reachable for readers."""
        import itertools
        self.demoted = []
        for kind in ("actors/", "guides/"):
            pages = sorted(n for n, t in self.files.items() if n.startswith(kind) and n.count("/") == 2 and n.endswith("/index.html") and INDEX_ROBOTS in t)
            if len(pages) < SCALED_MINIMUM:
                continue
            sets = {n: shingles(self.files[n]) for n in pages}
            gone = set()
            for a, b in itertools.combinations(pages, 2):
                if a in gone or b in gone:
                    continue
                if len(sets[a] & sets[b]) / max(1, len(sets[a] | sets[b])) > SIMILARITY_LIMIT:
                    loser = a if (len(sets[a]), b) < (len(sets[b]), a) else b
                    gone.add(loser)
                    self.files[loser] = self.files[loser].replace(INDEX_ROBOTS, '<meta name="robots" content="noindex,follow">', 1)
                    self.indexed.remove(self.base + loser[:-len("index.html")])
                    self.demoted.append(loser)

    def search_index(self):
        return json.dumps([{"t": a["title"], "u": self.link(self.doc_path(a)), "d": a["description"][:160],
                            "s": self.platform[a["id"]] or "", "c": category_name(self.primary_category(a))} for a in self.actors],
                          ensure_ascii=False, separators=(",", ":")) + "\n"

    def build(self, previous=None):
        accent = self.org.get("site", {}).get("accent", "#155dfb")
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
            raise SyncError("Invalid brand accent color")
        theme_css = "" if self.theme == "classic" else (ASSETS / ("theme-" + self.theme + ".css")).read_text(encoding="utf-8")
        # One render-blocking stylesheet: the base, the brand accent, then the theme.
        self.files["assets/site.css"] = (ASSETS / "site.css").read_text(encoding="utf-8") + f"\n:root{{--accent:{accent}}}\n" + theme_css
        self.files["assets/site.js"] = (ASSETS / "site.js").read_text(encoding="utf-8")
        initial = esc(self.brand[0].upper())
        self.files["assets/mark.svg"] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="5" fill="{accent}"/><text x="16" y="23" text-anchor="middle" font-family="Arial,sans-serif" font-size="23" font-weight="700" fill="white">{initial}</text></svg>'
        if self.theme == "studio":
            self.files["assets/mark.svg"] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><circle cx="20" cy="20" r="19" fill="{accent}"/><text x="20" y="28" text-anchor="middle" font-family="Arial,sans-serif" font-size="26" font-weight="700" fill="white">{initial}</text></svg>'
        elif self.theme == "editorial":
            self.files["assets/mark.svg"] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect x="1.5" y="1.5" width="37" height="37" fill="white" stroke="{accent}" stroke-width="1.5"/><text x="20" y="30" text-anchor="middle" font-family="Georgia,serif" font-size="33" fill="{accent}">{initial}</text></svg>'
        self.home()
        self.catalog()
        self.topics_index()
        for category in self.categories:
            self.topic(category)
        self.sites_index()
        for name in self.hubs:
            self.site_hub(name)
        self.guides_index()
        self.page("blog/", "Technical guides", "Browse the API tutorials.", '<section class="intro"><h1>Technical guides</h1><p class="lead">The tutorials moved to the guides section.</p>'
                  f'<p><a href="{self.link("guides/")}">Open the API tutorials</a></p></section>', active="guides", noindex=True)
        for actor in self.actors:
            self.actor_page(actor)
            self.guide_page(actor)
        self.demote_similar()
        self.legacy_paths(previous or [])
        self.page("sources/", "How these pages are made", "How the published Apify data keeps this documentation current, and what it does not cover.",
                  f'<article class="prose"><h1>How these pages are made</h1><p>{esc(self.brand)} maintains this site. Actor descriptions, READMEs, input schemas, output schemas, '
                  'dataset definitions, default run memory and pay-per-event prices are read from its public Apify organization and each Actor\'s successful default build.</p>'
                  '<h2>What updates automatically</h2><p>New public Actors get a reference page and an API tutorial. Published changes regenerate the affected pages; the "Updated" date '
                  'on a page is the finish time of the build it was made from. Incomplete reads from Apify block publication instead of publishing a partial catalog.</p>'
                  '<h2>What these pages do not claim</h2><p>Nothing here comes from running the Actors: the example inputs and sample records are the ones the publisher wrote in the README, '
                  'and the run totals are arithmetic on the published prices, not measured runs. Results depend on the source site and on your input. Check the Store page for the price '
                  'in force before a large run.</p>'
                  f'<h2>Machine-readable files</h2><ul><li><a href="{self.link("actors.json")}">Actor index (JSON)</a></li><li><a href="{self.link("source-manifest.json")}">Source content hashes</a></li>'
                  f'<li><a href="{self.link("llms.txt")}">Documentation index for language models (llms.txt)</a></li><li><a href="{self.link("sitemap.xml")}">Sitemap</a></li></ul>'
                  f'<p><a href="{self.apify}">{esc(self.brand)} on Apify</a> and the <a href="{self.repo}">project repository</a>.</p></article>', "AboutPage", crumbs=[("How these pages are made", "sources/")])
        self.page("404.html", "Page not found", "The requested documentation page was not found.", '<article class="prose"><h1>Page not found</h1><p>The address may have changed. '
                  f'Search above, or <a href="{self.link("actors/")}">browse all Actors</a>.</p></article>', noindex=True)
        metadata = [{k: a[k] for k in ("id", "username", "name", "title", "description", "categories", "url", "build_id")} | {"documentation": self.base + self.doc_path(a), "guide": self.base + self.doc_path(a, "guides")} for a in self.actors]
        self.files["actors.json"] = json_text({"brand": self.brand, "actors": metadata})
        self.files["search.json"] = self.search_index()
        self.files["source-manifest.json"] = json_text({"schema_version": 2, "organization": self.org["apify_username"], "actors": [{"id": a["id"], "build_id": a["build_id"], "hashes": {key: digest(a["readme"]) if key == "readme" else digest(json_text(a.get(key))) for key in ("readme", "input_schema", "output_schema", "dataset_schema", "key_value_schema")}} for a in self.actors]})
        modified = {}
        for actor in self.actors:
            if actor.get("build_finished_at"):
                for kind in ("actors", "guides"):
                    modified[self.base + self.doc_path(actor, kind)] = actor["build_finished_at"][:10]
        self.files["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                     + "".join("<url><loc>" + xml_escape(u) + "</loc>" + (f"<lastmod>{modified[u]}</lastmod>" if u in modified else "") + "</url>" for u in sorted(self.indexed))
                                     + "</urlset>\n")
        # A project site's /robots.txt is not authoritative for the github.io host.
        self.files["robots.txt"] = "User-agent: *\nAllow: /\nSitemap: " + self.base + "sitemap.xml\n"
        self.files["llms.txt"] = self.llms()
        # RSS permits omitted dates: never stamp polling time as publication time.
        self.files["feed.xml"] = ('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>' + xml_escape(self.brand + " export tutorials") + '</title><link>'
                                  + xml_escape(self.base + "guides/") + '</link><description>Export tutorials for each Actor</description>'
                                  + "".join('<item><title>' + xml_escape(self.guide_title(a)) + '</title><link>' + xml_escape(self.base + self.doc_path(a, "guides")) + '</link><guid isPermaLink="true">'
                                            + xml_escape(self.base + self.doc_path(a, "guides")) + '</guid><description>' + xml_escape(a["description"]) + '</description></item>' for a in self.actors if self.base + self.doc_path(a, "guides") in self.indexed)
                                  + '</channel></rss>\n')
        self.files[".nojekyll"] = ""
        for name in self.verification_files:
            self.files[name] = "google-site-verification: " + name + "\n"
        key = self.org.get("site", {}).get("indexnow_key")
        if key:
            if not INDEXNOW_KEY.fullmatch(key):
                raise SyncError("Invalid IndexNow key")
            self.files[key + ".txt"] = key
        validate_site(self.files, self.org, self.prefix)
        return self.files


class LinkAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.ids = set()
        self.links = []
        self.duplicate_ids = []
        self.titles = 0
        self.description = None
        self.canonical = None
        self.ld = []
        self._in_ld = False
        self._stack = []
        self.empty_headings = 0
        self._heading_text = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.titles += 1
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content") or ""
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._in_ld = True
            self.ld.append("")
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading_text = ""
        if attrs.get("id"):
            if attrs["id"] in self.ids:
                self.duplicate_ids.append(attrs["id"])
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_ld = False
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading_text is not None:
            if not self._heading_text.strip():
                self.empty_headings += 1
            self._heading_text = None

    def handle_data(self, data):
        if self._in_ld:
            self.ld[-1] += data
        if self._heading_text is not None:
            self._heading_text += data


# Generated text never claims a run, a test or experience: nothing here comes from running Actors.
UNSOURCED_CLAIM = re.compile(r"\b(we tested|we've tested|our tests?|in our testing|in our experience|we ran|we measured|tested by us)\b", re.I)
GARBAGE = re.compile(r"\bundefined\b|\bNaN\b|\[object Object\]|>None<|\$None|\bNone per\b|\{[a-z_]+\}|\{\{|&amp;[a-z]+;")


def visible_text(page):
    """Rendered text without code, preformatted blocks, scripts and tags: where interpolation
    leftovers (undefined, NaN, [object Object], a Python None, an unfilled {placeholder}) show.
    Publisher README text is fenced out: it may legitimately quote such words."""
    page = re.sub(r"<!--readme-->.*?<!--/readme-->", " ", page, flags=re.S)
    page = re.sub(r"<script\b.*?</script>|<pre\b.*?</pre>|<code\b.*?</code>|<style\b.*?</style>", " ", page, flags=re.S)
    page = re.sub(r"<head>.*?</head>", " ", page, flags=re.S)
    return re.sub(r"<[^>]+>", " ", page)


def validate_page(name, page, audit):
    """Critical checks for one rendered page; a failure blocks that brand's publication."""
    problems = []
    if audit.h1 != 1:
        problems.append("has %d H1 headings" % audit.h1)
    if audit.duplicate_ids:
        problems.append("duplicate IDs " + ", ".join(sorted(set(audit.duplicate_ids))[:3]))
    if audit.titles != 1 or re.search(r"<title>\s*</title>", page):
        problems.append("missing or repeated title")
    if not audit.description:
        problems.append("missing meta description")
    if not audit.canonical:
        problems.append("missing canonical link")
    if re.search(r"<[a-z][^>]*\sstyle=", page):
        problems.append("an inline style attribute (the CSP blocks it)")
    if audit.empty_headings:
        problems.append("%d empty headings" % audit.empty_headings)
    for block in audit.ld:
        try:
            json.loads(block)
        except ValueError:
            problems.append("structured data is not valid JSON")
    if 'http-equiv="refresh"' not in page:
        text = visible_text(page)
        match = GARBAGE.search(text)
        if match:
            problems.append("interpolation leftover " + repr(match.group()))
        claim = UNSOURCED_CLAIM.search(text)
        if claim:
            problems.append("an unsourced first-hand claim " + repr(claim.group()))
        if re.search(r'<section[^>]*>\s*<h2[^>]*>[^<]*</h2>\s*</section>', page):
            problems.append("a section with a heading and no content")
    return problems


SIMILARITY_LIMIT = 0.6
SCALED_MINIMUM = 10  # page sets smaller than this are not "scaled": no similarity rule
INDEX_ROBOTS = '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">'


def shingles(page, size=5):
    """Five-word shingles of a page's prose (no chrome, code or scripts)."""
    page = re.sub(r'<header class="masthead">.*?</header>|<footer.*?</footer>|<nav\b.*?</nav>', " ", page, flags=re.S)
    page = page.replace("<!--readme-->", "").replace("<!--/readme-->", "")
    words = re.findall(r"[a-z0-9$.,']+", visible_text(page).lower())
    return {" ".join(words[i:i + size]) for i in range(len(words) - size + 1)}


def similarity_check(files):
    """Scaled pages must each carry their own substance: no two indexable Actor pages, and no
    two indexable guides, may share more than SIMILARITY_LIMIT of their 5-word shingles."""
    import itertools
    worst = {}
    for kind in ("actors/", "guides/"):
        pages = sorted(n for n, t in files.items() if n.startswith(kind) and n.count("/") == 2 and n.endswith("/index.html") and INDEX_ROBOTS in t)
        if len(pages) < SCALED_MINIMUM:
            continue
        sets = {n: shingles(files[n]) for n in pages}
        for a, b in itertools.combinations(pages, 2):
            score = len(sets[a] & sets[b]) / max(1, len(sets[a] | sets[b]))
            if score > worst.get(kind, (0,))[0]:
                worst[kind] = (score, a, b)
    for kind, (score, a, b) in worst.items():
        if score > SIMILARITY_LIMIT:
            raise SyncError(f"Pages are too similar ({score:.2f} > {SIMILARITY_LIMIT}): {a} and {b}")
    return {kind: round(value[0], 3) for kind, value in worst.items()}


def validate_site(files, org, prefix):
    audits = {}
    for name, content in files.items():
        check_brand(content, org)
        if name.endswith(".html") and not GOOGLE_FILE.fullmatch(name):
            audit = LinkAudit()
            audit.feed(content)
            if audit.h1 != 1 or audit.duplicate_ids:
                raise SyncError("Rendered page has invalid heading or duplicate ID structure: " + name)
            problems = validate_page(name, content, audit)
            if problems:
                raise SyncError("Rendered page fails the page checks: " + name + ": " + "; ".join(problems))
            audits[name] = audit
        elif name.endswith(".json"):
            try:
                json.loads(content)
            except ValueError:
                raise SyncError("Published JSON file does not parse: " + name) from None
    for name, audit in audits.items():
        for link in audit.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or link.startswith("#") and not link[1:]:
                continue
            if link.startswith("#"):
                if link[1:] not in audit.ids:
                    raise SyncError("Broken internal anchor in " + name + ": " + link)
                continue
            target = unquote(parsed.path)
            if target.startswith(prefix):
                target = target[len(prefix):]
            elif target.startswith("/"):
                raise SyncError("Link escapes this brand's Pages project: " + name)
            else:
                target = urljoin(name, target)
            target = target + "index.html" if not target or target.endswith("/") else target
            if target not in files:
                raise SyncError("Broken internal link in " + name + ": " + link)
            if parsed.fragment and target in audits and parsed.fragment not in audits[target].ids:
                raise SyncError("Broken internal anchor in " + name + ": " + link)
    return {"pages": len(audits), "files": len(files), "similarity": similarity_check(files)}
