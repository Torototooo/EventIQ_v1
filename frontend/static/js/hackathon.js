let debounceTimer;
let allHackathons = [];
let hackathonBST = null;

/* =============================
   BINARY SEARCH TREE CLASS
============================= */
class HackathonBSTNode {
  constructor(hackathon) {
    this.hackathon = hackathon;
    this.left = null;
    this.right = null;
  }
}

class HackathonBST {
  constructor() {
    this.root = null;
  }

  // Insert hackathon into BST (sorted by title)
  insert(hackathon) {
    if (this.root === null) {
      this.root = new HackathonBSTNode(hackathon);
    } else {
      this._insertNode(this.root, hackathon);
    }
  }

  _insertNode(node, hackathon) {
    const comparison = hackathon.title.toLowerCase().localeCompare(node.hackathon.title.toLowerCase());

    if (comparison < 0) {
      if (node.left === null) {
        node.left = new HackathonBSTNode(hackathon);
      } else {
        this._insertNode(node.left, hackathon);
      }
    } else {
      if (node.right === null) {
        node.right = new HackathonBSTNode(hackathon);
      } else {
        this._insertNode(node.right, hackathon);
      }
    }
  }

  // Search for hackathons matching the search term
  search(searchTerm) {
    const results = [];
    const searchLower = searchTerm.toLowerCase();
    this._searchNode(this.root, searchLower, results);
    return results;
  }

  _searchNode(node, searchTerm, results) {
    if (node === null) return;

    const titleMatch = node.hackathon.title.toLowerCase().includes(searchTerm);
    const descMatch = node.hackathon.description.toLowerCase().includes(searchTerm);
    const cityMatch = (node.hackathon.city || "").toLowerCase().includes(searchTerm);
    const locationMatch = (node.hackathon.location || "").toLowerCase().includes(searchTerm);

    // If matched, add to results
    if (titleMatch || descMatch || cityMatch || locationMatch) {
      results.push(node.hackathon);
    }

    // Search both subtrees (since we're matching substrings, not exact comparisons)
    this._searchNode(node.left, searchTerm, results);
    this._searchNode(node.right, searchTerm, results);
  }

  // Get all hackathons in sorted order (in-order traversal)
  getAllSorted() {
    const results = [];
    this._inOrderTraversal(this.root, results);
    return results;
  }

  _inOrderTraversal(node, results) {
    if (node === null) return;
    this._inOrderTraversal(node.left, results);
    results.push(node.hackathon);
    this._inOrderTraversal(node.right, results);
  }
}

function loadHackathons() {
  clearTimeout(debounceTimer);

  debounceTimer = setTimeout(() => {
    const search = document.getElementById("searchInput").value.trim().toLowerCase();
    const status = document.getElementById("statusFilter").value;
    const city = document.getElementById("cityFilter").value;
    const skill = document.getElementById("skillFilter").value;
    const skillLevel = document.getElementById("skillLevelFilter").value;

    // Use BST for search term filtering
    let filtered = search && hackathonBST ? hackathonBST.search(search) : allHackathons;

    // Apply additional filters
    filtered = filtered.filter(h => {
      const matchesStatus = !status || h.status === status;
      const matchesCity =!city || h.city === city || (h.location && h.location.toLowerCase() === city.toLowerCase()) || (h.mode === "online" && city === "online");
      const matchesSkill = !skill || (h.skills && h.skills.toLowerCase().includes(skill.toLowerCase()));
      const matchesSkillLevel = !skillLevel || h.skill_level === skillLevel;

      return matchesStatus && matchesCity && matchesSkill && matchesSkillLevel;
    });

    renderHackathons(filtered);
  }, 300);
}

function renderHackathons(hackathons) {
  const container = document.getElementById("hackathonsContainer");
  container.innerHTML = "";

  if (!hackathons.length) {
    container.innerHTML =
      `<p class="text-center text-muted">No hackathons found.</p>`;
    return;
  }

  hackathons.forEach(h => {
    const card = `
      <div class="hackathon-card">
        <span class="hackathon-tag">HACKATHON</span>

        <h5>${h.title}</h5>
        <p class="hackathon-desc">${h.description}</p>

        <ul class="hackathon-info">
          <li>📅 ${new Date(h.start_date).toDateString()}</li>
          <li>📍 ${h.mode === "online" ? "Online" : (h.city || h.location)}</li>
          <li>🎯 Level: ${h.skill_level.toUpperCase()}</li>
        </ul>

        <a href="event/hackathon/${h.id}">
          <button class="hackathon-btn">Register Now</button>
        </a>
      </div>
    `;
    container.insertAdjacentHTML("beforeend", card);
  });
}

/* Initialize with data from API */
function initializeHackathons() {
  fetch("/api/hackathons")
    .then(res => res.json())
    .then(data => {
      allHackathons = data;
      
      // Build Binary Search Tree
      hackathonBST = new HackathonBST();
      allHackathons.forEach(hackathon => {
        hackathonBST.insert(hackathon);
      });
      
      renderHackathons(allHackathons);
    })
    .catch(() => {
      document.getElementById("hackathonsContainer").innerHTML =
        `<p class="text-center text-muted">Failed to load hackathons.</p>`;
    });
}

["searchInput", "statusFilter", "cityFilter", "skillFilter", "skillLevelFilter"]
  .forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      element.addEventListener("input", loadHackathons);
      element.addEventListener("change", loadHackathons);
    }
  });

// Initialize on page load
document.addEventListener("DOMContentLoaded", initializeHackathons);