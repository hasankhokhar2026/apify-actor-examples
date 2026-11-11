"use strict";
(() => {

  // Catalog filter: static rows, filtered in place (the list works without JavaScript).
  const search = document.querySelector("#actor-search");
  const category = document.querySelector("#category-filter");
  const rows = Array.from(document.querySelectorAll("[data-actor-row]"));
  const count = document.querySelector("#result-count");
  const empty = document.querySelector("#empty-results");
  const params = new URLSearchParams(location.search);
  if (search && params.has("q")) search.value = params.get("q");
  if (category && params.has("category")) category.value = params.get("category");
  const words = (text) => text.toLowerCase().split(/\s+/).filter(Boolean);
  function filter() {
    const terms = words(search?.value || "");
    const selected = category?.value || "";
    let visible = 0;
    for (const row of rows) {
      const hay = row.dataset.search || "";
      const matches = terms.every((t) => hay.includes(t)) && (!selected || (row.dataset.categories || "").split("|").includes(selected));
      row.hidden = !matches;
      if (matches) visible++;
    }
    if (count) count.textContent = `${visible} ${visible === 1 ? "Actor" : "Actors"}`;
    if (empty) empty.hidden = visible !== 0;
  }
  if (search && rows.length) {
    search.addEventListener("input", filter);
    category?.addEventListener("change", filter);
    filter();
  }

  // Search suggestions from search.json, loaded on first use.
  let index = null;
  async function load(url) {
    if (!index) {
      try {
        const response = await fetch(url);
        index = response.ok ? await response.json() : [];
      } catch {
        index = [];
      }
    }
    return index;
  }
  function rank(entry, terms) {
    const title = entry.t.toLowerCase();
    const site = (entry.s || "").toLowerCase();
    const hay = `${title} ${site} ${entry.d.toLowerCase()} ${entry.c.toLowerCase()}`;
    if (!terms.every((t) => hay.includes(t))) return -1;
    let score = 0;
    for (const t of terms) {
      if (site.startsWith(t)) score += 4;
      if (title.includes(t)) score += 2;
    }
    return score;
  }
  for (const form of document.querySelectorAll("[data-search-index]")) {
    const input = form.querySelector("input[type=search]");
    const list = form.querySelector(".search-results");
    if (!input || !list) continue;
    let active = -1;
    const close = () => {
      list.hidden = true;
      input.setAttribute("aria-expanded", "false");
      input.removeAttribute("aria-activedescendant");
      active = -1;
    };
    const mark = (next) => {
      const items = list.querySelectorAll("[role=option]");
      if (!items.length) return;
      active = (next + items.length) % items.length;
      items.forEach((item, i) => item.setAttribute("aria-selected", i === active ? "true" : "false"));
      input.setAttribute("aria-activedescendant", items[active].id);
      items[active].scrollIntoView({ block: "nearest" });
    };
    input.addEventListener("focus", () => load(form.dataset.searchIndex), { once: true });
    input.addEventListener("input", async () => {
      const terms = words(input.value);
      if (!terms.length) return close();
      const data = await load(form.dataset.searchIndex);
      const hits = data.map((e) => [rank(e, terms), e]).filter(([s]) => s >= 0).sort((a, b) => b[0] - a[0]).slice(0, 8);
      list.replaceChildren();
      if (!hits.length) {
        const li = document.createElement("li");
        li.className = "none";
        li.textContent = "No Actor matches. Press Enter to search the full catalog.";
        list.append(li);
      }
      hits.forEach(([, entry], i) => {
        const li = document.createElement("li");
        li.setAttribute("role", "option");
        li.id = `${list.id}-${i}`;
        const a = document.createElement("a");
        a.href = entry.u;
        a.textContent = entry.t;
        const span = document.createElement("span");
        span.textContent = entry.d;
        a.append(span);
        li.append(a);
        list.append(li);
      });
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
      active = -1;
    });
    input.addEventListener("keydown", (event) => {
      if (list.hidden) return;
      if (event.key === "ArrowDown") { event.preventDefault(); mark(active + 1); }
      else if (event.key === "ArrowUp") { event.preventDefault(); mark(active - 1); }
      else if (event.key === "Escape") { close(); }
      else if (event.key === "Enter" && active >= 0) {
        const link = list.querySelectorAll("[role=option] a")[active];
        if (link) { event.preventDefault(); location.href = link.href; }
      }
    });
    document.addEventListener("click", (event) => { if (!form.contains(event.target)) close(); });
  }

  // Tabs (ARIA tabs pattern). The page arrives in its final state; the script only switches it.
  for (const tabs of document.querySelectorAll("[data-tabs]")) {
    const links = Array.from(tabs.querySelectorAll("[role=tab]"));
    const select = (link, focus) => {
      for (const l of links) {
        const on = l === link;
        l.setAttribute("aria-selected", on ? "true" : "false");
        l.tabIndex = on ? 0 : -1;
        document.getElementById(l.getAttribute("aria-controls")).classList.toggle("active", on);
      }
      if (focus) link.focus();
    };
    tabs.dataset.ready = "";
    const wanted = links.find((l) => l.getAttribute("href") === location.hash);
    if (wanted) select(wanted, false);
    links.forEach((link, i) => {
      link.addEventListener("click", (event) => { event.preventDefault(); select(link, false); });
      link.addEventListener("keydown", (event) => {
        const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
        if (step) { event.preventDefault(); select(links[(i + step + links.length) % links.length], true); }
      });
    });
  }

  // Copy buttons: on generated blocks, and added to every code block from the README.
  let counter = 0;
  for (const pre of document.querySelectorAll(".prose pre")) {
    if (pre.closest(".code")) continue;
    const code = pre.querySelector("code") || pre;
    if (!code.id) code.id = `readme-code-${++counter}`;
    const wrap = document.createElement("div");
    wrap.className = "code";
    pre.replaceWith(wrap);
    wrap.append(pre);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy";
    button.dataset.copy = code.id;
    button.textContent = "Copy";
    wrap.append(button);
  }
  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy]");
    if (!button) return;
    const target = document.getElementById(button.dataset.copy);
    if (!target) return;
    try {
      await navigator.clipboard.writeText(target.textContent);
      button.textContent = "Copied";
    } catch {
      const range = document.createRange();
      range.selectNodeContents(target);
      const selection = getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = "Selected, press Ctrl+C";
    }
    setTimeout(() => { button.textContent = "Copy"; }, 2500);
  });
})();
