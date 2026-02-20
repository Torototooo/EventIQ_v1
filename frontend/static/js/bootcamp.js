let bootcamps = [];
let bootcampBST = null;


  //BINARY SEARCH TREE CLASS

class BootcampBSTNode {
  constructor(bootcamp) {
    this.bootcamp = bootcamp;
    this.left = null;
    this.right = null;
  }
}

class BootcampBST {
  constructor() {
    this.root = null;
  }

  // Insert bootcamp into BST (sorted by title)
  insert(bootcamp) {
    if (this.root === null) {
      this.root = new BootcampBSTNode(bootcamp);
    } else {
      this._insertNode(this.root, bootcamp);
    }
  }

  _insertNode(node, bootcamp) {
    const comparison = bootcamp.title.toLowerCase().localeCompare(node.bootcamp.title.toLowerCase());

    if (comparison < 0) {
      if (node.left === null) {
        node.left = new BootcampBSTNode(bootcamp);
      } else {
        this._insertNode(node.left, bootcamp);
      }
    } else {
      if (node.right === null) {
        node.right = new BootcampBSTNode(bootcamp);
      } else {
        this._insertNode(node.right, bootcamp);
      }
    }
  }

  // Search for bootcamps matching the search term
  search(searchTerm) {
    const results = [];
    const searchLower = searchTerm.toLowerCase();
    this._searchNode(this.root, searchLower, results);
    return results;
  }

  _searchNode(node, searchTerm, results) {
    if (node === null) return;

    const titleMatch = node.bootcamp.title.toLowerCase().includes(searchTerm);
    const descMatch = node.bootcamp.description.toLowerCase().includes(searchTerm);

    // If matched, add to results
    if (titleMatch || descMatch) {
      results.push(node.bootcamp);
    }

    // Search both subtrees 
    this._searchNode(node.left, searchTerm, results);
    this._searchNode(node.right, searchTerm, results);
  }

  // Get all bootcamps in sorted order (in-order traversal)
  getAllSorted() {
    const results = [];
    this._inOrderTraversal(this.root, results);
    return results;
  }

  _inOrderTraversal(node, results) {
    if (node === null) return;
    this._inOrderTraversal(node.left, results);
    results.push(node.bootcamp);
    this._inOrderTraversal(node.right, results);
  }
}


   //LOAD BOOTCAMPS FROM DB

document.addEventListener("DOMContentLoaded", loadBootcamps);

function loadBootcamps() {
  fetch("/api/bootcamps")
    .then(res => {
      if (!res.ok) throw new Error("Failed to fetch bootcamps");
      return res.json();
    })
    .then(data => {
      bootcamps = data;
      
      
      bootcampBST = new BootcampBST();
      bootcamps.forEach(bootcamp => {
        bootcampBST.insert(bootcamp);
      });
      
      renderBootcamps(bootcamps);
    })
    .catch(err => {
      console.error("Failed to load bootcamps:", err);
    });
}


  // RENDER BOOTCAMPS

function renderBootcamps(filtered = bootcamps) {
  const container = document.getElementById("bootcampsContainer");
  if (!container) return;

  container.innerHTML = "";

  if (!filtered.length) {
    container.innerHTML = "<p class='text-muted'>No bootcamps found.</p>";
    return;
  }

  filtered.forEach(b => {
    
    const priceText =
      b.registration_fee && Number(b.registration_fee) > 0
        ? `₹${b.registration_fee}`
        : "Free";

    
    let durationText = "Flexible";
    if (b.duration_days) {
      durationText =
        b.duration_days >= 7
          ? `${Math.round(b.duration_days / 7)} weeks`
          : `${b.duration_days} days`;
    }

    const card = `
      <div class="col-12 bootcamp-card-wrapper">
        <div class="workshop-card">
          <span class="workshop-tag">BOOTCAMP</span>
          <span class="workshop-price">${priceText}</span>

          <h5>${b.title}</h5>
          <p class="workshop-desc">${b.description}</p>

          <ul class="workshop-info">
            <li>⏱ ${durationText}</li>
            <li>👤 ${b.instructor || "TechHub"}</li>
          </ul>

            <a href="/event/bootcamp/${b.id}">
                <button class="workshop-btn">View Details</button>
            </a>

        </div>
      </div>
    `;
    container.insertAdjacentHTML("beforeend", card);
  });
}


   //FILTER BOOTCAMPS (using BST)

function filterBootcamps() {
  const search = document.getElementById("searchInput").value.toLowerCase();
  const price = document.getElementById("priceFilter").value;
  const skill = document.getElementById("skillFilter").value;
  const duration = document.getElementById("durationFilter").value;

  // Use BST for search term filtering
  let filtered = search ? bootcampBST.search(search) : bootcamps;

  // Apply additional filters
  filtered = filtered.filter(b => {
    const matchesPrice =
      !price ||
      (price === "Free"
        ? !b.registration_fee || b.registration_fee === 0
        : b.registration_fee > 0);

    const matchesSkill =
      !skill ||
      (b.skills && b.skills.toLowerCase().includes(skill.toLowerCase()));

    const matchesDuration =
      !duration ||
      (b.duration_days &&
        (duration.includes("weeks")
          ? Math.round(b.duration_days / 7) + " weeks" === duration
          : b.duration_days + " days" === duration));

    return matchesPrice && matchesSkill && matchesDuration;
  });

  renderBootcamps(filtered);
}


   // EVENT LISTENERS

["searchInput", "priceFilter", "skillFilter", "durationFilter"]
  .forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("input", filterBootcamps);
    el.addEventListener("change", filterBootcamps);
  });
