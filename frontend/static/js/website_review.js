const range = document.getElementById("ratingRange");
const stars = document.querySelectorAll("#ratingStars span");
const valueText = document.getElementById("ratingValue");

function updateRating(val) {
    valueText.textContent = val;
    document.documentElement.style.setProperty("--val", val);

    stars.forEach((star, index) => {
        star.classList.toggle("active", index < val);
    });
}

range.addEventListener("input", (e) => {
    updateRating(e.target.value);
});

// Init
updateRating(range.value);