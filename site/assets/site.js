"use strict";
(() => {
  const search = document.querySelector("#actor-search");
  const category = document.querySelector("#category-filter");
  const rows = Array.from(document.querySelectorAll("[data-actor-row]"));
  const count = document.querySelector("#result-count");
  const empty = document.querySelector("#empty-results");
  const homeLimit = Number(document.querySelector("[data-home-limit]")?.dataset.homeLimit || 0);
  const params = new URLSearchParams(location.search);
  if (search && params.has("q")) search.value = params.get("q");
  if (category && params.has("category")) category.value = params.get("category");
  function filter() {
    const term = (search?.value || "").trim().toLowerCase();
    const selected = category?.value || "";
    let visible = 0;
    for (const row of rows) {
      const matches = (!term || row.dataset.search.includes(term)) && (!selected || row.dataset.categories.split("|").includes(selected)) && (!homeLimit || term || selected || visible < homeLimit);
      row.hidden = !matches;
      if (matches) visible++;
    }
    if (count) count.textContent = homeLimit && !term && !selected ? `Showing ${visible} of ${rows.length} Actors` : `${visible} ${visible === 1 ? "Actor" : "Actors"}`;
    if (empty) empty.hidden = visible !== 0;
  }
  search?.addEventListener("input", filter);
  category?.addEventListener("change", filter);
  if (search || category) filter();
  for (const button of document.querySelectorAll("[data-copy]")) {
    button.addEventListener("click", async () => {
      const target = document.getElementById(button.dataset.copy);
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.textContent);
        button.textContent = "Copied";
      } catch {
        button.textContent = "Select and copy the code below";
      }
    });
  }
})();
