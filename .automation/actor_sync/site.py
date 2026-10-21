"""Build a complete, isolated, static documentation site from published evidence."""

import base64
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote, urljoin, urlsplit, unquote
from xml.sax.saxutils import escape as xml_escape

from markdown_it import MarkdownIt

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
    schema = actor["input_schema"]
    result = {}
    required = set(schema.get("required") or [])
    for key, prop in schema.get("properties", {}).items():
        if re.search(r"password|secret|token|cookie|api.?key", key, re.I):
            continue
        if "prefill" in prop:
            result[key] = prop["prefill"]
        elif key in required and "default" in prop:
            result[key] = prop["default"]
    return result, sorted(required - set(result))


def markdown(text):
    """CommonMark with tables; raw HTML is escaped, body H1s become H2s."""
    parser = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table").enable("strikethrough")
    tokens = parser.parse(text)
    used = {}
    for index, token in enumerate(tokens):
        if token.type in ("heading_open", "heading_close") and token.tag == "h1":
            token.tag = "h2"
        if token.type == "heading_open" and index + 1 < len(tokens):
            title = tokens[index + 1].content
            heading_id = "readme-" + (re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-") or "section")
            used[heading_id] = used.get(heading_id, 0) + 1
            if used[heading_id] > 1:
                heading_id += "-" + str(used[heading_id])
            token.attrSet("id", heading_id)
        if token.children:
            for child in token.children:
                if child.type == "link_open" and (child.attrGet("href") or "").startswith("#"):
                    child.attrSet("href", "#readme-" + child.attrGet("href")[1:])
    rendered = parser.renderer.render(tokens, parser.options, {})
    return rendered.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")


def schema_table(schema, limit=None):
    if not schema or not schema.get("properties"):
        return ""
    required = set(schema.get("required") or [])
    rows = []
    for field, prop in list(schema["properties"].items())[:limit]:
        kind = prop.get("type", "unspecified")
        if isinstance(kind, list):
            kind = " / ".join(kind)
        description = prop.get("description") or prop.get("title") or ""
        row = f'<tr><td><code>{esc(field)}</code></td><td>{esc(kind)}</td><td>{"required" if field in required else "optional"}</td><td>{esc(description)}</td></tr>'
        rows.append(row)
    return '<div class="table-wrap"><table><thead><tr><th scope="col">Field</th><th scope="col">Type</th><th scope="col">Required</th><th scope="col">Description</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>"


def code_block(text, block_id, language="json"):
    return f'<button type="button" class="copy-button" data-copy="{esc(block_id)}" aria-label="Copy {esc(language)} code">Copy</button><pre><code id="{esc(block_id)}" class="language-{esc(language)}">{esc(text)}</code></pre>'


class Site:
    def __init__(self, org, actors):
        check_snapshot(actors, org)
        self.org = org
        self.actors = sorted(actors, key=lambda a: (a["title"].casefold(), a["id"]))
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

    def link(self, path=""):
        return self.prefix + path

    def asset(self, path):
        return self.link(path) + "?v=" + digest(self.files.get(path, ""))[:12]

    def page(self, path, title, description, body, kind="CollectionPage", active="actors", noindex=False):
        canonical = self.base + path
        organization_id = self.base + "#organization"
        website_id = self.base + "#website"
        page_id = canonical + "#webpage"
        organization = {"@type": "Organization", "@id": organization_id, "name": self.brand,
                        "url": self.base, "sameAs": [self.apify]}
        website = {"@type": "WebSite", "@id": website_id, "name": self.brand,
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
        if path.startswith(("actors/", "guides/", "topics/")) and path.count("/") > 1:
            section = path.split("/", 1)[0]
            breadcrumb_id = canonical + "#breadcrumb"
            web_page["breadcrumb"] = {"@id": breadcrumb_id}
            nodes.append({"@type": "BreadcrumbList", "@id": breadcrumb_id, "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": self.brand, "item": self.base},
                {"@type": "ListItem", "position": 2, "name": section.title(), "item": self.base + section + "/"},
                {"@type": "ListItem", "position": 3, "name": title, "item": canonical}]})
        structured = {"@context": "https://schema.org", "@graph": nodes}
        # Escape script delimiters in source-controlled metadata.
        ld = json.dumps(structured, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
        ld_hash = base64.b64encode(hashlib.sha256(ld.encode()).digest()).decode()
        csp = f"default-src 'self'; script-src 'self' 'sha256-{ld_hash}'; style-src 'self'; img-src 'self' https: data:; base-uri 'self'; form-action 'self'; object-src 'none'"
        full_title = title if self.brand in title else title + " | " + self.brand
        navigation = "".join(f'<a href="{self.link(route)}"' + (' aria-current="page"' if label == active else "") + f'>{label.title()}</a>' for label, route in [("actors", "actors/"), ("guides", "guides/")])
        content = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="{esc(csp)}"><title>{esc(full_title)}</title><meta name="description" content="{esc(description[:180])}"><meta name="robots" content="{"noindex,follow" if noindex else "index,follow"}"><link rel="canonical" href="{esc(canonical)}"><meta property="og:title" content="{esc(full_title)}"><meta property="og:description" content="{esc(description[:180])}"><meta property="og:type" content="website"><meta property="og:url" content="{esc(canonical)}"><meta property="og:site_name" content="{esc(self.brand)}"><meta name="twitter:card" content="summary"><link rel="icon" href="{self.asset('assets/mark.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{self.asset('assets/site.css')}"><link rel="stylesheet" href="{self.asset('assets/brand.css')}"><link rel="alternate" type="application/rss+xml" title="{esc(self.brand)} guides" href="{self.link('feed.xml')}"><script type="application/ld+json">{ld}</script><script src="{self.asset('assets/site.js')}" defer></script></head><body class="theme-{self.theme}"><a href="#main" class="skip-link">Skip to content</a><header><div class="inner"><a href="{self.link()}" class="brand"><img src="{self.asset('assets/mark.svg')}" alt="" width="29" height="29">{esc(self.brand)}</a><nav aria-label="Main navigation">{navigation}<a href="{self.repo}">GitHub</a></nav></div></header><main id="main">{body}</main><footer class="footer"><strong>{esc(self.brand)}</strong><div class="footer-links"><a href="{self.link('topics/')}">Topics</a><a href="{self.link('sources/')}">Documentation sources</a><a href="{self.apify}">Apify</a><a href="{self.repo}">GitHub</a></div></footer></body></html>'''
        filename = path + "index.html" if path.endswith("/") or not path else path
        self.files[filename] = content
        if not noindex:
            self.indexed.append(canonical)

    def actor_rows(self, actors, home=False):
        rows = []
        for index, actor in enumerate(actors):
            category = next((c for c in actor["categories"] if c != "AUTOMATION"), "AUTOMATION")
            target = self.link(f"actors/{actor['id']}/")
            rows.append(f'<article class="actor-row" data-actor-row data-search="{esc((actor["title"] + " " + actor["description"]).casefold())}" data-categories="{esc("|".join(actor["categories"]))}"' + (' hidden' if home and index >= 5 else "") + f'><div><a class="category-label" href="{self.link("topics/" + category_slug(category) + "/")}">{esc(category_name(category))}</a></div><h2><a href="{target}">{esc(actor["title"])}</a></h2><p>{esc(actor["description"])}</p><a class="arrow" href="{target}" aria-label="Read {esc(actor["title"])}">→</a></article>')
        return '<div class="catalog-head"><span>Category</span><span>Actor</span><span>Description</span><span></span></div>' + "".join(rows)

    def directory(self, path="", category=None):
        home = not path
        actors = self.featured() if home else [a for a in self.actors if not category or category in a["categories"]]
        title = self.org.get("site", {}).get("headline", "Web data, ready to build with.") if home else category_name(category) + " Actors" if category else "Explore the Actor catalog"
        if home:
            description = f"Explore {len(actors)} published Apify Actors from {self.brand}, with reference documentation, schemas, and practical Python guides."
        elif category:
            description = f"Browse {len(actors)} {category_name(category).lower()} Apify Actors from {self.brand}. Compare published capabilities, input schemas, and Python usage guides."
        else:
            description = f"Browse all {len(actors)} Apify Actors from {self.brand}. Find published READMEs, input and output schemas, and source-based Python guides."
        options = "".join(f'<option value="{esc(c)}">{esc(category_name(c))}</option>' for c in sorted({c for a in actors for c in a["categories"]}))
        heading = esc(title).replace(", ", ", <br>", 1) if home and self.theme == "studio" else esc(title)
        intro_class = "intro intro-home" if home else "intro"
        body = f'<section class="{intro_class}"><h1>{heading}</h1><p>{description}</p></section><form class="controls" action="{self.link("actors/")}" role="search"><div class="search"><span aria-hidden="true">⌕</span><label class="sr-only" for="actor-search">Search Actors</label><input type="search" name="q" id="actor-search" placeholder="Search Actors" autocomplete="off"></div><div><label class="sr-only" for="category-filter">Filter by category</label><select id="category-filter" name="category"><option value="">All categories</option>{options}</select></div></form><p class="result-count" id="result-count" role="status">{len(actors)} Actors</p><section class="catalog" aria-label="Actor catalog"' + (' data-home-limit="5"' if home else '') + f'>{self.actor_rows(actors, home)}</section><p id="empty-results" class="empty" hidden>No Actors match this search. Try another keyword or category.</p>'
        if home:
            body += f'<p><a href="{self.link("actors/")}">Browse all {len(actors)} Actors →</a></p><h2 class="section-title">Start with a guide</h2>' + self.guide_rows(self.featured()[:3])
        else:
            body += '<h2 class="section-title">Browse by topic</h2><div class="topic-list">' + "".join(f'<a href="{self.link("topics/" + category_slug(c) + "/")}">{esc(category_name(c))}</a>' for c in sorted({c for a in self.actors for c in a["categories"]})) + "</div>"
        self.page(path, self.brand + " Apify Actor documentation" if home else title, description, body)

    def featured(self):
        preferred = self.org.get("site", {}).get("featured_actor_ids", [])
        indexed = {a["id"]: a for a in self.actors}
        return [indexed[i] for i in preferred if i in indexed] + [a for a in self.actors if a["id"] not in preferred]

    def guide_rows(self, actors):
        return '<div class="guide-list">' + "".join(f'<article class="guide-row"><div><a href="{self.link("guides/" + a["id"] + "/")}">Use {esc(a["title"])} with Python</a><p>Published inputs, result schemas, and a source-based API recipe.</p></div><span class="arrow" aria-hidden="true">→</span></article>' for a in actors) + "</div>"

    def schema_section(self, actor, key, heading, text):
        slug = key.replace("_", "-")
        schema = actor.get(key)
        body = f'<section class="schema-section" id="{slug}"><h2>{heading}</h2><p>{esc(text)}</p>'
        if schema is None:
            return body + '<p>This definition is not present in the default published build. See the published README for available documentation.</p></section>'
        body += schema_table(schema, 3 if key == "input_schema" else None)
        if key == "input_schema" and len(schema.get("properties", {})) > 3:
            body += '<details><summary>Show all input fields</summary>' + schema_table(schema) + '</details>'
        body += f'<p><a href="{slug}.json">Download the published {heading.lower()}</a></p><details><summary>View complete JSON</summary><pre><code>{esc(json_text(schema))}</code></pre></details></section>'
        return body

    def python_code(self, actor, complete=True):
        sample, missing = source_example(actor)
        return f'''import json
import os
import urllib.request

# Save the schema-derived example as input.json; review and edit it first.
with open("input.json", encoding="utf-8") as stream:
    actor_input = json.load(stream)

token = os.environ["APIFY_TOKEN"]
request = urllib.request.Request(
    "https://api.apify.com/v2/acts/{actor['id']}/runs?timeout=120&maxTotalChargeUsd=0.50",
    data=json.dumps(actor_input).encode("utf-8"),
    headers={{"Authorization": "Bearer " + token, "Content-Type": "application/json"}},
    method="POST",
)
# This starts a potentially billable run. Do not automatically retry this POST.
with urllib.request.urlopen(request, timeout=40) as response:
    run = json.load(response)["data"]
print("Run ID:", run["id"])
print("Status:", run["status"])
# Inspect and download results in Apify Console once the run succeeds.
'''

    def actor_page(self, actor):
        actor_id = actor["id"]
        sidebar = '<aside class="contents" aria-label="On this page"><strong>Contents</strong>' + "".join(f'<a href="#{key}">{label}</a>' for key, label in [("overview", "Overview"), ("published-readme", "Published README"), ("input-schema", "Input schema"), ("output-schema", "Output schema"), ("dataset-schema", "Dataset schema"), ("python-quickstart", "Python quickstart")]) + "</aside>"
        content = f'<div class="breadcrumb"><a href="{self.link("actors/")}">Actors</a><span>/</span><span>{esc(actor["title"])}</span></div><section id="overview"><h1 class="doc-title">{esc(actor["title"])}</h1><p class="lede">{esc(actor["description"])}</p><div class="actions"><a class="button" href="{actor["url"]}">Open on Apify</a><a class="text-link" href="{self.repo}/blob/main/docs/actors/{actor_id}/README.md">GitHub source</a></div></section>'
        content += self.schema_section(actor, "input_schema", "Input schema", "Input fields, types, required flags, descriptions, defaults, and prefills come from the published definition. Prefill examples are distinct from defaults.")
        content += self.schema_section(actor, "output_schema", "Output schema", "Published result links and storage locations. This schema is not an exhaustive contract for every field in a dataset record.")
        content += self.schema_section(actor, "dataset_schema", "Dataset schema", "Published dataset views and any declared field definitions. A view can select only a subset of the returned record fields.")
        content += self.schema_section(actor, "key_value_schema", "Key-value schema", "Published key-value store definitions, when provided by this build.")
        content += '<section id="published-readme"><h2>Published README</h2><details><summary>Read the full published documentation</summary>' + markdown(actor["readme"]) + "</details></section>"
        content += f'<section id="python-quickstart"><h2>Python quickstart</h2><p>Use a schema-derived input and the Python standard library to start a run. An Apify account and token are required for execution.</p><p><a href="{self.link("guides/" + actor_id + "/")}">Open the step-by-step Python guide →</a></p></section>'
        content += f'<p class="source-note">Source build <code>{esc(actor["build_id"])}</code>. Documentation is regenerated from the default published build; private drafts are not included.</p>'
        self.page(f"actors/{actor_id}/", actor["title"], actor["description"], '<div class="doc-layout">' + sidebar + '<article class="prose">' + content + "</article></div>", "TechArticle")
        for key in ("input_schema", "output_schema", "dataset_schema", "key_value_schema"):
            self.files[f"actors/{actor_id}/{key.replace('_', '-')}.json"] = json_text(actor.get(key))
        self.files[f"actors/{actor_id}/README.md"] = actor["readme"]

    def guide_page(self, actor):
        actor_id = actor["id"]
        sample, missing = source_example(actor)
        title = "Use " + actor["title"] + " with Python"
        body = f'<div class="breadcrumb"><a href="{self.link("guides/")}">Guides</a><span>/</span><a href="{self.link("actors/" + actor_id + "/")}">{esc(actor["title"])}</a></div><article class="prose"><h1 class="doc-title">{esc(title)}</h1><p class="lede">{esc(actor["description"])}</p><h2>1. Choose the data you need</h2><p>Review the <a href="{self.link("actors/" + actor_id + "/#published-readme")}">published README</a> for supported collection modes, examples, and limits. The recipe below uses the current published input definition.</p><h2>2. Prepare a source-based input</h2><p>This JSON contains published prefills and required-field defaults. Review every value for your task before running it; it is not a promise of successful collection.</p>'
        if missing:
            body += '<p class="note">The published schema does not supply an example for these required fields: ' + ", ".join(f"<code>{esc(x)}</code>" for x in missing) + '. Supply them using the reference documentation before execution.</p>'
        body += code_block(json_text(sample), "example-input") + f'<p><a href="input.example.json" download>Download input.example.json</a> and save your reviewed copy as <code>input.json</code>.</p>'
        body += schema_table(actor["input_schema"])
        body += '<h2>3. Start an Actor run</h2><p>Set <code>APIFY_TOKEN</code> in your environment. Python 3.10 or newer is sufficient; this recipe uses no third-party packages.</p><p class="note">Execution may incur charges. Review current pricing on Apify. The request asks for a 120-second timeout and a charge limit; these settings are subject to Apify’s pricing and do not guarantee an all-inclusive spending cap.</p>'
        body += code_block(self.python_code(actor), "python-recipe", "python")
        body += f'<h2>4. Inspect the actual results</h2><p>Open the run in Apify Console and wait for a successful completion. Use the published <a href="{self.link("actors/" + actor_id + "/#output-schema")}">output schema</a> to locate results and the <a href="{self.link("actors/" + actor_id + "/#dataset-schema")}">dataset schema</a> to understand declared views. Missing or optional record fields must not be treated as guaranteed values.</p>'
        if actor.get("output_schema", {}).get("description") if actor.get("output_schema") else False:
            body += '<p>' + esc(actor["output_schema"]["description"]) + "</p>"
        body += '<h2>Questions before you run</h2><div class="faq"><details><summary>Which inputs are required?</summary><p>' + ("The published required fields are " + ", ".join(f"<code>{esc(k)}</code>" for k in actor["input_schema"].get("required", [])) if actor["input_schema"].get("required") else "No top-level fields are marked required in the published schema. Conditional requirements can still apply; check the README.") + '</p></details><details><summary>What does this guide verify?</summary><p>The fields, prefills, and schema links are rendered from the published build. This is a usage recipe, not a paid live extraction test. Source availability and collection results can vary.</p></details><details><summary>What if the run request times out?</summary><p>Check Apify Console before retrying. The first request may already have created a run. Do not automatically repeat a run-creation POST.</p></details></div>'
        body += f'<div class="actions"><a class="button" href="{actor["url"]}">Open on Apify</a><a href="{self.link("actors/" + actor_id + "/")}">Full Actor reference</a></div><p class="source-note">Generated from source build <code>{esc(actor["build_id"])}</code> and its README and schemas. Source changes regenerate this guide; no third-party editorial claims are inferred.</p></article>'
        self.page(f"guides/{actor_id}/", title, "Python usage recipe for " + actor["title"] + ", grounded in its published input and output definitions.", body, "TechArticle", "guides")
        self.files[f"guides/{actor_id}/input.example.json"] = json_text(sample)

    def build(self, previous=None):
        accent = self.org.get("site", {}).get("accent", "#155dfb")
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
            raise SyncError("Invalid brand accent color")
        self.files["assets/site.css"] = (ASSETS / "site.css").read_text(encoding="utf-8") + f"\n:root{{--accent:{accent}}}\n"
        self.files["assets/site.js"] = (ASSETS / "site.js").read_text(encoding="utf-8")
        self.files["assets/brand.css"] = "" if self.theme == "classic" else (ASSETS / ("theme-" + self.theme + ".css")).read_text(encoding="utf-8")
        initial = esc(self.brand[0].upper())
        self.files["assets/mark.svg"] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="5" fill="{accent}"/><text x="16" y="23" text-anchor="middle" font-family="Arial,sans-serif" font-size="23" font-weight="700" fill="white">{initial}</text></svg>'
        if self.theme == "studio":
            self.files["assets/mark.svg"] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><circle cx="20" cy="20" r="19" fill="{accent}"/><text x="20" y="28" text-anchor="middle" font-family="Arial,sans-serif" font-size="26" font-weight="700" fill="white">{initial}</text></svg>'
        elif self.theme == "editorial":
            self.files["assets/mark.svg"] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect x="1.5" y="1.5" width="37" height="37" fill="white" stroke="{accent}" stroke-width="1.5"/><text x="20" y="30" text-anchor="middle" font-family="Georgia,serif" font-size="33" fill="{accent}">{initial}</text></svg>'
        self.directory()
        self.directory("actors/")
        categories = sorted({c for a in self.actors for c in a["categories"]})
        self.page("topics/", "Browse by topic", "Find published Actors by their declared Apify categories.", '<section class="intro"><h1>Browse by topic</h1><p>Categories come from the current public Actor listings.</p></section><div class="topic-list">' + "".join(f'<a href="{self.link("topics/" + category_slug(c) + "/")}">{esc(category_name(c))}</a>' for c in categories) + "</div>")
        for category in categories:
            self.directory("topics/" + category_slug(category) + "/", category)
        guide_body = '<section class="intro"><h1>Practical Python guides</h1><p>Source-based recipes for configuring Actors, starting runs, and locating results.</p></section>' + self.guide_rows(self.featured())
        self.page("guides/", "Practical Python guides", "Python usage guides grounded in published Actor READMEs and schemas.", guide_body, active="guides")
        self.page("blog/", "Technical guides", "Browse source-based technical guides and usage recipes.", '<section class="intro"><h1>Technical guides</h1><p>Practical recipes generated from published Actor definitions.</p></section>' + self.guide_rows(self.featured()), active="guides", noindex=True)
        for actor in self.actors:
            self.actor_page(actor)
            self.guide_page(actor)
        current = {a["id"] for a in self.actors}
        for old in previous or []:
            if old["id"] not in current:
                for kind in ("actors", "guides"):
                    self.page(f"{kind}/{old['id']}/", "Actor unavailable", "This Actor is not in the current public listing.", '<article class="prose"><h1>Actor unavailable</h1><p>This Actor is absent from the current public organization listing. Browse the current catalog for available documentation.</p><p><a href="' + self.link("actors/") + '">View the current catalog</a></p></article>', noindex=True)
        self.page("sources/", "Documentation sources", "How published Apify data keeps this documentation current.", f'<article class="prose"><h1>Documentation sources</h1><p>This site is maintained by {esc(self.brand)}. Actor descriptions, READMEs, input schemas, output schemas, and dataset definitions are read from its public Apify organization and successful default builds.</p><h2>What updates automatically</h2><p>New public Actors receive reference pages and Python recipes. Published source changes regenerate affected content. Generated-file drift is repaired from the current source, while incomplete API reads block publication.</p><h2>Scope and limitations</h2><p>Drafts and alternate build tags are not included. Schema-derived examples are usage recipes, not live execution verification. Pricing and source-site availability must be checked on Apify. Absent definitions are identified explicitly.</p><h2>Machine-readable references</h2><p><a href="{self.link("actors.json")}">Actor index</a> · <a href="{self.link("source-manifest.json")}">Source content hashes</a> · <a href="{self.link("llms.txt")}">Documentation index</a></p><p><a href="{self.apify}">Apify organization</a> · <a href="{self.repo}">Project repository</a></p></article>', "AboutPage")
        self.page("404.html", "Page not found", "The requested documentation page was not found.", '<article class="prose"><h1>Page not found</h1><p><a href="' + self.link("actors/") + '">Browse the Actor catalog</a></p></article>', noindex=True)
        metadata = [{k: a[k] for k in ("id", "username", "name", "title", "description", "categories", "url", "build_id")} | {"documentation": self.base + f"actors/{a['id']}/", "guide": self.base + f"guides/{a['id']}/"} for a in self.actors]
        self.files["actors.json"] = json_text({"brand": self.brand, "actors": metadata})
        self.files["source-manifest.json"] = json_text({"schema_version": 2, "organization": self.org["apify_username"], "actors": [{"id": a["id"], "build_id": a["build_id"], "hashes": {key: digest(a["readme"]) if key == "readme" else digest(json_text(a.get(key))) for key in ("readme", "input_schema", "output_schema", "dataset_schema", "key_value_schema")}} for a in self.actors]})
        self.files["sitemap.xml"] = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join("<url><loc>" + xml_escape(u) + "</loc></url>" for u in sorted(self.indexed)) + "</urlset>\n"
        # A project site's /robots.txt is not authoritative for the github.io host.
        self.files["robots.txt"] = "User-agent: *\nAllow: /\nSitemap: " + self.base + "sitemap.xml\n"
        self.files["llms.txt"] = "# " + self.brand + " documentation\n\nPublished Actor references and Python usage recipes.\n\n" + "\n".join(f"- [{a['title']}]({self.base}actors/{a['id']}/): {a['description']}" for a in self.actors) + "\n"
        # RSS permits omitted dates: never stamp polling time as publication time.
        self.files["feed.xml"] = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>' + xml_escape(self.brand + " technical guides") + '</title><link>' + xml_escape(self.base + "guides/") + '</link><description>Source-based Actor usage guides</description>' + "".join('<item><title>' + xml_escape("Use " + a["title"] + " with Python") + '</title><link>' + xml_escape(self.base + f"guides/{a['id']}/") + '</link><guid isPermaLink="true">' + xml_escape(self.base + f"guides/{a['id']}/") + '</guid><description>' + xml_escape(a["description"]) + '</description></item>' for a in self.actors) + '</channel></rss>\n'
        self.files[".nojekyll"] = ""
        validate_site(self.files, self.org, self.prefix)
        return self.files


class LinkAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.ids = set()
        self.links = []
        self.duplicate_ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if attrs.get("id"):
            if attrs["id"] in self.ids:
                self.duplicate_ids.append(attrs["id"])
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])


def validate_site(files, org, prefix):
    audits = {}
    for name, content in files.items():
        check_brand(content, org)
        if name.endswith(".html"):
            audit = LinkAudit()
            audit.feed(content)
            if audit.h1 != 1 or audit.duplicate_ids:
                raise SyncError("Rendered page has invalid heading or duplicate ID structure: " + name)
            audits[name] = audit
    for name, audit in audits.items():
        for link in audit.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or link.startswith("#"):
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
    return {"pages": len(audits), "files": len(files)}
