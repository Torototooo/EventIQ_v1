let workshops = [];
let workshopBST = null;

/* =============================
   BINARY SEARCH TREE CLASS
============================= */
class WorkshopBSTNode {
  constructor(workshop) {
    this.workshop = workshop;
    this.left = null;
    this.right = null;
  }
}

class WorkshopBST {
  constructor() {
    this.root = null;
  }

  insert(workshop) {
    if (this.root === null) {
      this.root = new WorkshopBSTNode(workshop);
    } else {
      this._insertNode(this.root, workshop);
    }
  }

  _insertNode(node, workshop) {
    const a = (workshop.title || "").toLowerCase();
    const b = (node.workshop.title || "").toLowerCase();
    const comparison = a.localeCompare(b);

    if (comparison < 0) {
      if (node.left === null) node.left = new WorkshopBSTNode(workshop);
      else this._insertNode(node.left, workshop);
    } else {
      if (node.right === null) node.right = new WorkshopBSTNode(workshop);
      else this._insertNode(node.right, workshop);
    }
  }

  search(searchTerm) {
    const results = [];
    const term = (searchTerm || "").toLowerCase();
    this._searchNode(this.root, term, results);
    return results;
  }

  _searchNode(node, term, results) {
    if (!node) return;

    const w = node.workshop;
    const title = (w.title || "").toLowerCase();
    const desc = (w.description || "").toLowerCase();
    const skills = (Array.isArray(w.skills) ? w.skills.join(" ") : (w.skills || "")).toLowerCase();

    if (title.includes(term) || desc.includes(term) || skills.includes(term)) {
      results.push(w);
    }

    this._searchNode(node.left, term, results);
    this._searchNode(node.right, term, results);
  }

  getAllSorted() {
    const res = [];
    this._inOrder(this.root, res);
    return res;
  }

  _inOrder(node, res) {
    if (!node) return;
    this._inOrder(node.left, res);
    res.push(node.workshop);
    this._inOrder(node.right, res);
  }
}

// -----------------------------
// LOAD WORKSHOPS FROM API
// -----------------------------
document.addEventListener("DOMContentLoaded", loadWorkshops);

function loadWorkshops() {
  fetch("/api/workshops")
    .then(res => res.json())
    .then(data => {
      workshops = data || [];

      // build BST
      workshopBST = new WorkshopBST();
      workshops.forEach(w => workshopBST.insert(w));

      renderWorkshops(workshops);
    })
    .catch(err => {
      console.error("Failed to load workshops:", err);
    });
}

// -----------------------------
// RENDER WORKSHOPS
// -----------------------------
function renderWorkshops(filtered = workshops) {
  const container = document.getElementById("workshopsContainer");
  container.innerHTML = "";

  if (!filtered.length) {
    container.innerHTML = "<p class='text-muted'>No workshops found.</p>";
    return;
  }

  filtered.forEach(w => {
    const priceText =
      w.registration_fee && Number(w.registration_fee) > 0
        ? `₹${w.registration_fee}`
        : "Free";

    const duration = getDuration(w.start_time, w.end_time);

    const instructor = "Host"; // placeholder (host not sent in API yet)

    const card = `
      <div class="col-12 workshop-card-wrapper">
          <div class="workshop-card">
            <span class="workshop-tag">WORKSHOP</span>
            <span class="workshop-price">${priceText}</span>

            <h5>${w.title}</h5>
            <p class="workshop-desc">${w.description}</p>

            <ul class="workshop-info">
              <li>⏱ ${duration}</li>
              <li>🎯 ${w.skill_level.toUpperCase()}</li>
              <li>👤 ${instructor}</li>
            </ul>

            <a href="/event/workshop/${w.id}">
                <button class="workshop-btn">Enroll Now</button>
            </a>
          </div>
      </div>
    `;
    container.insertAdjacentHTML("beforeend", card);
  });
}

// -----------------------------
// FILTER WORKSHOPS (CLIENT SIDE)
// -----------------------------
function filterWorkshops() {
  const search = document.getElementById("searchInput")?.value?.toLowerCase() || "";
  const skill = document.getElementById("skillFilter")?.value || "";
  const skillLevel = document.getElementById("skillLevelFilter")?.value || "";

  // Use BST for search filtering when there is a search term
  let filtered = search && workshopBST ? workshopBST.search(search) : workshops.slice();

  filtered = filtered.filter(w => {
    const matchesSkill = !skill || (w.skills && (Array.isArray(w.skills) ? w.skills.join(" ") : w.skills).toLowerCase().includes(skill.toLowerCase()));
    const matchesLevel = !skillLevel || (w.skill_level === skillLevel);
    return matchesSkill && matchesLevel;
  });

  renderWorkshops(filtered);
}

// -----------------------------
// EVENT LISTENERS
// -----------------------------
document.getElementById("searchInput")?.addEventListener("input", filterWorkshops);
document.getElementById("skillFilter")?.addEventListener("change", filterWorkshops);
document.getElementById("skillLevelFilter")?.addEventListener("change", filterWorkshops);

// -----------------------------
// HELPERS
// -----------------------------
function getDuration(start, end) {
  if (!start || !end) return "Flexible";

  const startTime = new Date(`1970-01-01T${start}`);
  const endTime = new Date(`1970-01-01T${end}`);
  const diffMs = endTime - startTime;

  const hours = Math.round(diffMs / (1000 * 60 * 60));
  return `${hours} hours`;
}
