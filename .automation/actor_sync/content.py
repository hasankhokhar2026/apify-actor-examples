"""Facts for the documentation pages, taken only from what the publisher published.

Everything here is derived from an Actor's published README, input schema, dataset
definition, and Store pricing. Nothing is invented: when a fact is missing, the
helper returns nothing and the page leaves that part out.
"""

import json
import math
import re

# ---------------------------------------------------------------------------
# README structure
# ---------------------------------------------------------------------------

FENCE = re.compile(r"^(```|~~~)")

SECTION_KINDS = [
    ("faq", re.compile(r"\b(faq|frequently asked|common questions|questions)\b", re.I)),
    ("input", re.compile(r"^(input|inputs|input reference|input parameters|input fields|configuration|parameters)\b", re.I)),
    ("examples", re.compile(r"^(example|examples|sample input|how to use|quick ?start|usage)\b", re.I)),
    ("output", re.compile(r"(output|what you get|sample record|what each record contains|record fields|data fields|fields returned|result fields)", re.I)),
    ("usecases", re.compile(r"(use cases|who is it for|who it is for|use it for)", re.I)),
    ("what", re.compile(r"^(what this actor does|what it does|what you can collect|features|key features|how it works|modes|services|data source)", re.I)),
    ("limits", re.compile(r"(limitation|limits|reliability|responsible use|pagination|known issues|notes)", re.I)),
    ("cost", re.compile(r"(usage cost|pricing|cost|how much)", re.I)),
]


def heading_kind(title):
    for kind, pattern in SECTION_KINDS:
        if pattern.search(title):
            return kind
    return "other"


def split_sections(readme):
    """Split a README into (intro, [section]) at level-2 headings, ignoring code fences.
    The leading level-1 title is dropped (the page has its own H1)."""
    intro, sections, current, fenced = [], [], None, False
    for line in readme.split("\n"):
        if FENCE.match(line.strip()):
            fenced = not fenced
        if not fenced:
            if re.match(r"^#\s+\S", line) and current is None and not any(x.strip() for x in intro):
                continue
            match = re.match(r"^##\s+(.+?)\s*#*\s*$", line)
            if match:
                current = {"title": clean_heading(match.group(1)), "lines": []}
                current["kind"] = heading_kind(current["title"])
                sections.append(current)
                continue
        (current["lines"] if current else intro).append(line)
    for section in sections:
        section["body"] = "\n".join(section.pop("lines")).strip()
    return "\n".join(intro).strip(), [s for s in sections if s["body"]]


def clean_heading(text):
    return re.sub(r"[*_`]", "", text).strip()


def subsections(body):
    """Split a section body at level-3 headings: [(heading or None, text)]."""
    parts, current, lines, fenced = [], None, [], False
    for line in body.split("\n"):
        if FENCE.match(line.strip()):
            fenced = not fenced
        match = None if fenced else re.match(r"^###\s+(.+?)\s*#*\s*$", line)
        if match:
            if current is not None or "\n".join(lines).strip():
                parts.append((current, "\n".join(lines).strip()))
            current, lines = clean_heading(match.group(1)), []
        else:
            lines.append(line)
    if current is not None or "\n".join(lines).strip():
        parts.append((current, "\n".join(lines).strip()))
    return parts


def faq_items(sections):
    """Question/answer pairs from the README's FAQ section: H3 questions, or bold
    question paragraphs. Only real questions (ending in '?') count."""
    items = []
    for section in sections:
        if section["kind"] != "faq":
            continue
        for heading, text in subsections(section["body"]):
            if heading and heading.rstrip().endswith("?") and text:
                items.append((heading, text))
        if not items:
            # Bold question paragraphs, scanned line by line (no backtracking pattern).
            question, answer = None, []
            for line in section["body"].split("\n") + ["**end?**"]:
                # '**Question?**' on its own line, or followed by the answer on the same line.
                bold = re.match(r"\*\*([^*\n]{3,300}\?)\*\*[ \t]*(.*)$", line.strip())
                if bold:
                    if question and "\n".join(answer).strip():
                        items.append((question, "\n".join(answer).strip()))
                    question, answer = bold.group(1).strip(), [bold.group(2)]
                elif question:
                    answer.append(line)
    return items


TROUBLE = re.compile(r"\b(why|missing|fail|failed|error|empty|blocked|block|proxy|captcha|limit|cap|slow|timeout|not work|no results|fewer|wrong)\b", re.I)


def troubleshooting(faq):
    return [(q, a) for q, a in faq if TROUBLE.search(q)]


def json_blocks(readme):
    """Every fenced JSON block with its nearest preceding heading."""
    blocks, heading, fenced, language, buffer = [], "", False, "", []
    for line in readme.split("\n"):
        stripped = line.strip()
        if not fenced:
            match = re.match(r"^#{2,4}\s+(.+?)\s*#*\s*$", line)
            if match:
                heading = clean_heading(match.group(1))
            if FENCE.match(stripped):
                fenced, language, buffer = True, stripped[3:].strip().lower(), []
            continue
        if FENCE.match(stripped):
            fenced = False
            if language in ("json", "jsonc", "json5", ""):
                text = "\n".join(buffer)
                try:
                    value = json.loads(text)
                except ValueError:
                    continue
                blocks.append({"heading": heading, "value": value, "text": text})
            continue
        buffer.append(line)
    return blocks


def example_inputs(actor):
    """Example inputs the publisher wrote in the README: JSON objects whose every key is a
    published input field. Named after their README heading."""
    properties = set(((actor.get("input_schema") or {}).get("properties") or {}).keys())
    examples, seen = [], set()
    if not properties:
        return examples
    for block in json_blocks(actor.get("readme", "")):
        value = block["value"]
        if not isinstance(value, dict) or not value or not set(value) <= properties:
            continue
        key = json.dumps(value, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        name = re.sub(r"^(example|examples|sample)\s*(input)?\s*[:\-–—]?\s*", "", block["heading"], flags=re.I).strip()
        if not name or re.fullmatch(r"(input|inputs|example|examples|usage|quick ?start)", name, re.I):
            name = "Example input" if not examples else f"Example input {len(examples) + 1}"
        examples.append({"name": name[:1].upper() + name[1:], "input": value})
    return examples


def dataset_fields(actor):
    """Fields declared by the dataset views, in view order, with their display labels."""
    views = ((actor.get("dataset_schema") or {}).get("views") or {})
    fields, labels = [], {}
    for view in views.values():
        if not isinstance(view, dict):
            continue
        for field in ((view.get("transformation") or {}).get("fields") or []):
            if isinstance(field, str) and field not in fields:
                fields.append(field)
        for field, prop in (((view.get("display") or {}).get("properties")) or {}).items():
            if isinstance(prop, dict) and isinstance(prop.get("label"), str) and field not in labels:
                labels[field] = prop["label"]
    declared = ((actor.get("dataset_schema") or {}).get("fields") or {}).get("properties") or {}
    for field in declared:
        if field not in fields:
            fields.append(field)
    return [(f, labels.get(f) or (declared.get(f) or {}).get("title") or "", (declared.get(f) or {}).get("description") or "") for f in fields]


def dataset_views(actor):
    views = ((actor.get("dataset_schema") or {}).get("views") or {})
    out = []
    for key, view in views.items():
        if not isinstance(view, dict):
            continue
        fields = [f for f in ((view.get("transformation") or {}).get("fields") or []) if isinstance(f, str)]
        labels = {f: p.get("label") for f, p in (((view.get("display") or {}).get("properties")) or {}).items() if isinstance(p, dict)}
        if fields:
            out.append({"key": key, "title": view.get("title") or key, "fields": [(f, labels.get(f) or "") for f in fields]})
    return out


def sample_record(actor):
    """A sample output record the publisher put in the README: a JSON object (or the first
    object of a list) whose keys are mostly declared dataset fields, never an input."""
    properties = set(((actor.get("input_schema") or {}).get("properties") or {}).keys())
    declared = {f for f, _, _ in dataset_fields(actor)}
    for block in json_blocks(actor.get("readme", "")):
        value = block["value"]
        if isinstance(value, list) and value and isinstance(value[0], dict):
            value = value[0]
        if not isinstance(value, dict) or len(value) < 3:
            continue
        keys = set(value)
        if keys <= properties:
            continue
        overlap = len(keys & declared)
        output_heading = re.search(r"(output|sample|record|result|response)", block["heading"], re.I)
        if (declared and overlap >= max(3, len(keys) // 2)) or (output_heading and not keys & properties):
            return {"heading": block["heading"], "record": value}
    return None


# ---------------------------------------------------------------------------
# Platforms (the site a tool reads)
# ---------------------------------------------------------------------------

MULTIWORD = ["Product Hunt", "Hacker News", "Home Depot", "Best Buy", "App Store", "Uber Eats", "Y Combinator",
             "Trading Economics", "Wayback Machine", "Property Finder", "Rent the Runway", "Google Play",
             "Bing Maps", "Yahoo Finance", "Yahoo News", "Yahoo Auctions", "Trip.com", "Wholesale Central",
             "Wholesale Marine", "Facebook Marketplace", "eBay Motors", "Rent the Runway"]
SUBBRANDS = {"Google": 2, "Yandex": 1, "Naver": 1}
X_ALIASES = re.compile(r"^(X/Twitter|Twitter \(X\)|X \(Twitter\)|Twitter|X)(?=[\s,]|$)")
NOT_A_SITE = {
    "multi-league", "multi-site", "username", "general", "b2b", "brazil", "brazilian", "bulk", "chinese", "company",
    "complete", "domain-scoped", "global", "human-like", "indian", "official", "new", "search", "smtp", "southeast",
    "us", "washington", "we", "website", "welcome", "world", "florida", "bar", "goc", "paste", "the", "a", "an",
    "universal", "local", "public", "free", "email", "web", "site", "news", "job", "jobs", "product", "products",
    "multi", "any", "all", "best", "top", "daily", "weekly", "live", "online", "social", "ai", "seo", "data",
    "lead", "leads", "contact", "domain", "url", "page", "pages", "mena", "eu", "uk", "europe", "asia", "african",
}


def platform_of(title):
    """The site an Actor reads, from its published title: the leading brand name
    ('Airbnb', 'Google Maps', 'X (Twitter)'), or None when the title does not open with one."""
    title = title.strip()
    if X_ALIASES.match(title):
        return "X (Twitter)"
    for name in MULTIWORD:
        if title.startswith(name + " ") or title == name:
            return "Google Play" if name == "Google Play" else name
    words = title.split()
    if not words:
        return None
    first = words[0].rstrip(",:")
    if first in SUBBRANDS:
        size = SUBBRANDS[first]
        if size == 2 and len(words) > 1 and re.fullmatch(r"[A-Z][A-Za-z]+", words[1].rstrip(",")):
            return first + " " + words[1].rstrip(",")
        return first
    if first.casefold() in NOT_A_SITE or not re.search(r"[A-Za-z]", first):
        return None
    if not (first[0].isupper() or first[0].isdigit() or re.match(r"^[a-z]+[A-Z]", first) or "." in first):
        return None
    return first


def platform_slug(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.casefold().replace("(twitter)", "twitter")).strip("-")
    return slug or "site"


# ---------------------------------------------------------------------------
# Pricing (Store pay-per-event prices; never estimated beyond the published numbers)
# ---------------------------------------------------------------------------

TIERS = [("FREE", "Free plan"), ("BRONZE", "Starter plan"), ("SILVER", "Scale plan"), ("GOLD", "Business plan")]


def money(value):
    """A published unit price, exactly: $0.10, $0.077, $0.00099, $1.25."""
    if value is None:
        return ""
    if value >= 1:
        return f"${value:,.2f}"
    text = f"{value:.6f}".rstrip("0")
    whole, _, decimals = text.partition(".")
    return "$" + whole + "." + decimals.ljust(2, "0")


def money2(value):
    """Totals for a run: cents, never fewer than two decimals."""
    if value < 0.01 and value > 0:
        return "under $0.01"
    return "$" + f"{value:,.2f}"


def event_price(event, tier):
    tiers = event.get("tiers") or {}
    if tier in tiers:
        return tiers[tier]
    return event.get("flat")


def pricing_summary(actor):
    """Normalised pay-per-event prices: the primary (per-result) event, the start event,
    other events, and memory. None when the Actor has no pay-per-event pricing."""
    pricing = actor.get("pricing")
    if not pricing or pricing.get("model") != "PAY_PER_EVENT":
        return None
    events = pricing.get("events") or []
    primary = next((e for e in events if e.get("primary")), None)
    start = next((e for e in events if e.get("key") == "apify-actor-start"), None)
    others = [e for e in events if e is not primary and e is not start]
    memory_mb = actor.get("memory_mb") or 0
    start_events = max(1, math.ceil(memory_mb / 1024)) if memory_mb else 1
    return {"primary": primary, "start": start, "others": others, "memory_mb": memory_mb,
            "start_events": start_events, "platform_extra": bool(pricing.get("platform_usage_paid_by_user"))}


def run_cost(summary, tier, results):
    """Actor charges for one run that returns `results` items at the default memory:
    start events plus the per-result event. Platform usage is not included."""
    if not summary or not summary["primary"]:
        return None
    per = event_price(summary["primary"], tier)
    if per is None:
        return None
    total = per * results
    if summary["start"]:
        start = event_price(summary["start"], tier)
        if start is not None:
            total += start * summary["start_events"]
    return total


def per_thousand(summary, tier):
    if not summary or not summary["primary"]:
        return None
    per = event_price(summary["primary"], tier)
    return None if per is None else per * 1000


def result_noun(summary):
    title = ((summary or {}).get("primary") or {}).get("title") or "result"
    title = title.strip().casefold()
    return title if re.fullmatch(r"[a-z][a-z \-]{0,30}", title) else "result"


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

SECRET_FIELD = re.compile(r"password|secret|token|cookie|api.?key", re.I)


def schema_example(actor):
    """Published prefills, then defaults for required fields: never invented values."""
    schema = actor.get("input_schema") or {}
    result = {}
    required = set(schema.get("required") or [])
    for key, prop in (schema.get("properties") or {}).items():
        if SECRET_FIELD.search(key) or not isinstance(prop, dict):
            continue
        if "prefill" in prop:
            result[key] = prop["prefill"]
        elif key in required and "default" in prop:
            result[key] = prop["default"]
    return result, sorted(required - set(result))


def best_input(actor):
    """The input used in code samples: the README's first example when it covers every
    required field, else the schema prefills. Returns (input, label)."""
    required = set((actor.get("input_schema") or {}).get("required") or [])
    for example in example_inputs(actor):
        if required <= set(example["input"]):
            return example["input"], example["name"]
    sample, _ = schema_example(actor)
    return sample, "Prefilled input"


LIMIT_FIELD = re.compile(r"^(max|limit)([A-Z_]|$)")
LIMIT_WORDS = re.compile(r"\b(how many|number of|maximum (number|count)|max(imum)? (results|items|records|rows|pages|posts|reviews|comments)|hard cap|cap(s|ped)? |limit (of|on|the)|up to \d|per (run|query|search|keyword|url|profile|page|input))", re.I)
NOT_A_CAP = re.compile(r"price|rating|salary|date|age|year|distance|radius|size|length|duration|bed|bath|room|score|percent|follower|view|like|budget|cost|amount|zoom|concurren|minute|second|hour|mb$|retr|missing|timeout|memory|wait|delay", re.I)


def limit_fields(actor):
    """Fields that cap how much a run collects (maxItems, maxReviews, limit...), with their
    published default and maximum: the reader's cost control. A `max...` name alone is not
    enough (maxPrice filters, it does not cap): the schema's own words must describe a count."""
    out = []
    for key, prop in ((actor.get("input_schema") or {}).get("properties") or {}).items():
        if not isinstance(prop, dict) or prop.get("type") != "integer" or not LIMIT_FIELD.search(key) or NOT_A_CAP.search(key):
            continue
        words = " ".join(str(prop.get(k) or "") for k in ("title", "description"))
        if LIMIT_WORDS.search(words) and not NOT_A_CAP.search(prop.get("title") or ""):
            out.append({"field": key, "title": prop.get("title") or "", "default": prop.get("default"),
                        "maximum": prop.get("maximum"), "prefill": prop.get("prefill")})
    return out


def describe_value(value):
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 60 else text[:57] + "..."


def allowed_values(prop):
    if not isinstance(prop, dict):
        return ""
    enum = prop.get("enum") or ((prop.get("items") or {}).get("enum") if isinstance(prop.get("items"), dict) else None)
    if isinstance(enum, list) and enum:
        shown = [str(v) for v in enum[:8]]
        return ", ".join(shown) + (f" and {len(enum) - 8} more" if len(enum) > 8 else "")
    low, high = prop.get("minimum"), prop.get("maximum")
    if low is not None and high is not None:
        return f"{low} to {high}"
    if low is not None:
        return f"at least {low}"
    if high is not None:
        return f"up to {high}"
    return ""


BULLET = re.compile(r"^\s*[-*+]\s+")
LEADING_CODE = re.compile(r"`([^`\n]+)`")
JOINER = re.compile(r"[\s,/&]+(?:(?:and|or)\b[\s,/&]*)?")
DASH = re.compile(r"\s*(?:—|–|-|:)\s+")


def field_bullet(line):
    """'- `a`, `b` — text' -> (["a", "b"], "text"). A linear scan: no nested quantifiers,
    because a backtracking pattern here hung the build on long field lists."""
    match = BULLET.match(line)
    if not match:
        return None
    position, fields = match.end(), []
    while True:
        code = LEADING_CODE.match(line, position)
        if not code:
            break
        fields.append(code.group(1))
        position = code.end()
        joiner = JOINER.match(line, position)
        if joiner and LEADING_CODE.match(line, joiner.end()):
            position = joiner.end()
    dash = DASH.match(line, position)
    if not fields or not dash or not line[dash.end():].strip():
        return None
    return fields, line[dash.end():].strip()


def readme_field_notes(sections):
    """What the publisher's README says about each output field: bullet lines that open with
    backticked field names (`a`, `b` — text) and table rows whose first cell is a field."""
    notes = {}
    for section in sections:
        if section["kind"] != "output":
            continue
        for line in section["body"].split("\n"):
            parsed = field_bullet(line)
            if parsed:
                for field in parsed[0]:
                    field = field.strip().removesuffix("[]").strip()
                    if re.fullmatch(r"[A-Za-z_][\w.]*", field) and field not in notes:
                        notes[field] = parsed[1]
                continue
            stripped = line.strip()
            if stripped.startswith("|"):
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                first = re.fullmatch(r"`([A-Za-z_][\w.]*)(?:\[\])?`", cells[0]) if len(cells) >= 2 else None
                if first and cells[-1] and not set(cells[-1]) <= set("-: ") and first.group(1) not in notes:
                    notes[first.group(1)] = cells[-1]
    return notes
