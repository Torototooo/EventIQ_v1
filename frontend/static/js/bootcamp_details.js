// Countdown Timer
function updateCountdown() {
  const targetDate = new Date('2024-01-15T00:00:00').getTime(); // Enrollment opens date
  const now = new Date().getTime();
  const difference = targetDate - now;

  if (difference > 0) {
    const days = Math.floor(difference / (1000 * 60 * 60 * 24));
    const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((difference % (1000 * 60)) / 1000);

    document.getElementById('days').textContent = days.toString().padStart(2, '0');
    document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
    document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
    document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
  } else {
    document.querySelector('.countdown-timer h5').textContent = 'Enrollment Open!';
    document.querySelector('.countdown-display').style.display = 'none';
  }
}

// Update countdown every second
setInterval(updateCountdown, 1000);
updateCountdown();

// Add click handlers for interactive elements
document.querySelectorAll('.skill-badge').forEach(badge => {
  badge.addEventListener('click', function() {
    this.style.transform = 'scale(0.95)';
    setTimeout(() => {
      this.style.transform = 'scale(1.1)';
      setTimeout(() => {
        this.style.transform = 'scale(1)';
      }, 150);
    }, 100);
  });
});

document.querySelectorAll('.interactive-badge').forEach(badge => {
  badge.addEventListener('click', function() {
    this.style.transform = 'scale(0.95)';
    setTimeout(() => {
      this.style.transform = 'scale(1.05)';
      setTimeout(() => {
        this.style.transform = 'scale(1)';
      }, 150);
    }, 100);
  });
});