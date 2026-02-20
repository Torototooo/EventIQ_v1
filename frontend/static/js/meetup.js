let meetups = [];
let meetupBST = null;

/* =============================
   BINARY SEARCH TREE CLASS
============================= */
class MeetupBSTNode {
  constructor(meetup) {
    this.meetup = meetup;
    this.left = null;
    this.right = null;
  }
}

class MeetupBST {
  constructor() {
    this.root = null;
  }

  // Insert meetup into BST (sorted by title)
  insert(meetup) {
    if (this.root === null) {
      this.root = new MeetupBSTNode(meetup);
    } else {
      this._insertNode(this.root, meetup);
    }
  }

  _insertNode(node, meetup) {
    const comparison = meetup.title.toLowerCase().localeCompare(node.meetup.title.toLowerCase());

    if (comparison < 0) {
      if (node.left === null) {
        node.left = new MeetupBSTNode(meetup);
      } else {
        this._insertNode(node.left, meetup);
      }
    } else {
      if (node.right === null) {
        node.right = new MeetupBSTNode(meetup);
      } else {
        this._insertNode(node.right, meetup);
      }
    }
  }

  // Search for meetups matching the search term
  search(searchTerm) {
    const results = [];
    const searchLower = searchTerm.toLowerCase();
    this._searchNode(this.root, searchLower, results);
    return results;
  }

  _searchNode(node, searchTerm, results) {
    if (node === null) return;

    const titleMatch = node.meetup.title.toLowerCase().includes(searchTerm);
    const descMatch = node.meetup.description.toLowerCase().includes(searchTerm);
    const cityMatch = (node.meetup.city || "").toLowerCase().includes(searchTerm);
    const locationMatch = (node.meetup.location || "").toLowerCase().includes(searchTerm);

    // If matched, add to results
    if (titleMatch || descMatch || cityMatch || locationMatch) {
      results.push(node.meetup);
    }

    // Search both subtrees (since we're matching substrings, not exact comparisons)
    this._searchNode(node.left, searchTerm, results);
    this._searchNode(node.right, searchTerm, results);
  }

  // Get all meetups in sorted order (in-order traversal)
  getAllSorted() {
    const results = [];
    this._inOrderTraversal(this.root, results);
    return results;
  }

  _inOrderTraversal(node, results) {
    if (node === null) return;
    this._inOrderTraversal(node.left, results);
    results.push(node.meetup);
    this._inOrderTraversal(node.right, results);
  }
}

/* ----------------------------
   LOAD MEETUPS FROM API
---------------------------- */
document.addEventListener("DOMContentLoaded", loadMeetups);

function loadMeetups() {
  fetch("/api/meetups")
    .then(res => res.json())
    .then(data => {
      meetups = data;
      
      // Build Binary Search Tree
      meetupBST = new MeetupBST();
      meetups.forEach(meetup => {
        meetupBST.insert(meetup);
      });
      
      renderMeetups(meetups);
    })
    .catch(err => {
      console.error("Failed to load meetups:", err);
    });
}

/* ----------------------------
   RENDER MEETUPS
---------------------------- */

function renderMeetups(filtered = meetups) {
  const container = document.getElementById("meetupsContainer");
  container.innerHTML = "";

  if (!filtered.length) {
    container.innerHTML = "<p class='text-muted'>No meetups found.</p>";
    return;
  }

  filtered.forEach(m => {
    const dateObj = new Date(m.start_date);
    const meetupDate = dateObj.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric"
    });

    const timeText = getMeetupTime(m.start_time, m.end_time);

    const locationText =
      m.mode === "online"
        ? "Online"
        : (m.city || m.location || "TBA");

    const card = `
      <div class="col-12 meetup-card-wrapper">
          <div class="meetup-card">
            <span class="meetup-tag">MEETUP</span>
            <span class="meetup-date">${meetupDate}</span>

            <h5>${m.title}</h5>
            <p class="meetup-desc">${m.description}</p>

            <ul class="meetup-info">
              <li>📍 ${locationText}</li>
              <li>👥 ${m.attending} attending</li>
              <li>⏰ ${timeText}</li>
            </ul>

            <a href="/event/meetup/${m.id}">
                <button class="meetup-btn">Join Meetup</button>
            </a>
          </div>
      </div>
    `;
    container.insertAdjacentHTML("beforeend", card);
  });
}

/* ----------------------------
   FILTER MEETUPS (using BST)
---------------------------- */
function filterMeetups() {
  const search = document.getElementById("searchInput").value.toLowerCase();
  const city = document.getElementById("cityFilter").value;
  const topic = document.getElementById("topicFilter").value;

  // Use BST for search term filtering
  let filtered = search && meetupBST ? meetupBST.search(search) : meetups;

  // Apply additional filters
  filtered = filtered.filter(m => {
    const matchesCity =
      !city || m.city === city || (m.location && m.location.toLowerCase() === city.toLowerCase()) || (m.mode === "online" && city === "online");

    const matchesTopic =
      !topic ||
      (m.skills && m.skills.toLowerCase().includes(topic.toLowerCase()));

    return matchesCity && matchesTopic;
  });

  renderMeetups(filtered);
}

/* -----------------------------
   EVENT LISTENERS
------------------------------ */
document.getElementById("searchInput").addEventListener("input", filterMeetups);
document.getElementById("cityFilter").addEventListener("change", filterMeetups);
document.getElementById("topicFilter").addEventListener("change", filterMeetups);

/* -----------------------------
   HELPERS
------------------------------ */
function getMeetupTime(start, end) {
  if (!start || !end) return "Flexible";

  const startTime = new Date(`1970-01-01T${start}`);
  const endTime = new Date(`1970-01-01T${end}`);

  return `${formatTime(startTime)} – ${formatTime(endTime)}`;
}

function formatTime(date) {
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit"
  });
}
