
function togglePassword() {
  const password = document.getElementById('password');
  const icon = document.querySelector('#togglePassword i');
  if (password.type === 'password') {
    password.type = 'text';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
  } else {
    password.type = 'password';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
  }
}

function toggleConfirmPassword() {
  const confirmPassword = document.getElementById('confirmPassword');
  const icon = document.querySelector('#toggleConfirmPassword i');
  if (confirmPassword.type === 'password') {
    confirmPassword.type = 'text';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
  } else {
    confirmPassword.type = 'password';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
  }
}

document.getElementById('togglePassword').addEventListener('click', togglePassword);
document.getElementById('toggleConfirmPassword').addEventListener('click', toggleConfirmPassword);

// Basic form validation
document.getElementById('signupForm').addEventListener('submit', function(event) {
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  if (password !== confirmPassword) {
    alert('Passwords do not match!');
    event.preventDefault();
  }
  // reCAPTCHA validation would be handled server-side
});


document.getElementById("isHost").addEventListener("change", function () {
  const hostFields = document.getElementById("hostFields");
  hostFields.style.display = this.checked ? "block" : "none";
});

const isHost = document.getElementById("isHost");
const hostFields = document.getElementById("hostFields");
const skillsSection = document.getElementById("skillsSection");
const courseYearSection = document.getElementById("courseYearSection");
const collegeSection = document.getElementById("collegeSection");

hostFields.style.display = "none";

isHost.addEventListener("change", () => {
  if (isHost.checked) {
    hostFields.style.display = "block";
    skillsSection.style.display = "none";
    courseYearSection.style.display = "none";
    collegeSection.style.display = "none";
  } else {
    hostFields.style.display = "none";
    skillsSection.style.display = "block";
    courseYearSection.style.display = "flex";
    collegeSection.style.display = "block";
  }
});

// Password validation
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirmPassword");
const signupForm = document.getElementById("signupForm");

function validatePasswordRequirements(password) {
  const requirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
  };

  return requirements;
}

function updateRequirementUI(elementId, isValid) {
  const element = document.getElementById(elementId);
  const icon = element.querySelector("i");

  if (isValid) {
    element.classList.remove("text-muted");
    element.classList.add("text-success");
    icon.classList.remove("fa-circle");
    icon.classList.add("fa-check-circle");
  } else {
    element.classList.remove("text-success");
    element.classList.add("text-muted");
    icon.classList.remove("fa-check-circle");
    icon.classList.add("fa-circle");
  }
}

passwordInput.addEventListener("input", () => {
  const password = passwordInput.value;
  const requirements = validatePasswordRequirements(password);

  updateRequirementUI("req-length", requirements.length);
  updateRequirementUI("req-uppercase", requirements.uppercase);
  updateRequirementUI("req-lowercase", requirements.lowercase);
  updateRequirementUI("req-number", requirements.number);
  updateRequirementUI("req-special", requirements.special);

  // Check confirm password match
  if (confirmPasswordInput.value) {
    checkPasswordMatch();
  }
});

function checkPasswordMatch() {
  const password = passwordInput.value;
  const confirmPassword = confirmPasswordInput.value;
  const matchDiv = document.getElementById("passwordMatch");

  if (confirmPassword === "") {
    matchDiv.innerHTML = "";
    return true;
  }

  if (password === confirmPassword) {
    matchDiv.innerHTML = '<span class="text-success"><i class="fas fa-check-circle"></i> Passwords match</span>';
    return true;
  } else {
    matchDiv.innerHTML = '<span class="text-danger"><i class="fas fa-times-circle"></i> Passwords do not match</span>';
    return false;
  }
}

confirmPasswordInput.addEventListener("input", checkPasswordMatch);

// Form submission validation
signupForm.addEventListener("submit", (e) => {
  const password = passwordInput.value;
  const requirements = validatePasswordRequirements(password);

  // Check all requirements
  const allValid = Object.values(requirements).every(val => val === true);

  if (!allValid) {
    e.preventDefault();
    alert("Please ensure your password meets all requirements.");
    return false;
  }

  // Check password match
  if (!checkPasswordMatch()) {
    e.preventDefault();
    alert("Passwords do not match.");
    return false;
  }
});
