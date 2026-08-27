const state = { category: "visa_free", region: "", visa: "", query: "" };

const cards = Array.from(document.querySelectorAll(".card"));
const tabs = Array.from(document.querySelectorAll(".tab"));
const chips = Array.from(document.querySelectorAll(".chip"));
const searchInput = document.getElementById("search");
const regionSelect = document.getElementById("region");
const visaFilter = document.getElementById("visa-filter");
const emptyNote = document.getElementById("empty");

function isoToFlag(iso) {
  return Array.from(iso, c => String.fromCodePoint(127397 + c.charCodeAt(0))).join("");
}

function matches(card) {
  const d = card.dataset;
  if (d.category !== state.category) return false;
  if (state.region && d.region !== state.region) return false;
  if (state.category === "special" && state.visa && !d.visas.split(",").includes(state.visa)) return false;
  if (state.query && !d.search.includes(state.query)) return false;
  return true;
}

function setActive(group, active) {
  group.forEach(el => el.classList.toggle("is-active", el === active));
}

function render() {
  let visible = 0;
  for (const card of cards) {
    const show = matches(card);
    card.hidden = !show;
    if (show) visible++;
    else card.open = false;
  }
  emptyNote.hidden = visible > 0;
  visaFilter.hidden = state.category !== "special";
}

tabs.forEach(tab =>
  tab.addEventListener("click", () => {
    state.category = tab.dataset.category;
    state.visa = "";
    setActive(chips, chips[0]);
    setActive(tabs, tab);
    render();
  })
);

chips.forEach(chip =>
  chip.addEventListener("click", () => {
    state.visa = chip.dataset.visa;
    setActive(chips, chip);
    render();
  })
);

searchInput.addEventListener("input", () => {
  state.query = searchInput.value.trim().toLowerCase();
  render();
});

regionSelect.addEventListener("change", () => {
  state.region = regionSelect.value;
  render();
});

document.querySelectorAll(".flag").forEach(el => {
  el.textContent = isoToFlag(el.dataset.iso);
});

render();
