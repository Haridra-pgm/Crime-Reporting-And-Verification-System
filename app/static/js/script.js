console.log("JavaScript is working!");

function validateLoginForm() {
    const isValidUsername = validusername();
    const isValidPassword = validPassword();

    const loginButton = document.getElementById("loginButton");
    
    // Enable or disable the login button based on validation
    if (isValidUsername && isValidPassword) {
        loginButton.disabled = false;
    } else {
        loginButton.disabled = true;
    }
}

function validusername() {
    const username = document.getElementById("username").value.trim();
    const usernameError = document.getElementById("usernameError");
    const usernameLabel = document.getElementById("usernameLabel");
    const phonePattern = /^\d{10}$/;
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    let isValid = true;

    // Reset error message
    usernameError.innerText = "";

    if (username === "") {
        usernameError.innerText = "Phone No or Email-id is required.";
        isValid = false;
    } else if (phonePattern.test(username)) {
        usernameLabel.innerText = "Phone No";
    } else if (emailPattern.test(username)) {
        usernameLabel.innerText = "Email-id";
    } else {
        usernameError.innerText = "Please enter a valid Phone No or Email-id.";
        isValid = false;
    }

    return isValid;
}

function validPassword() {
    const password = document.getElementById("password").value.trim();
    const passwordError = document.getElementById("passwordError");
    const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    let isValid = true;

    // Reset error message
    passwordError.innerText = "";

    if (password.length < 6) {
        passwordError.innerText = "Password must be at least 6 characters long.";
        isValid = false;
    } else if (!passwordPattern.test(password)) {
        passwordError.innerText = "Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.";
        isValid = false;
    }

    return isValid;
}

function validateSignupForm() {
    const isValidPhone = validPhoneNumber();
    const isValidNewPassword = validNewPassword();
    const isValidConfirmPassword = validConfirmPassword();
}

// emergency validation
// 🌍 Auto-detect location
function getLocation() {
    if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        document.getElementById("latitude").value = lat;
        document.getElementById("longitude").value = lon;
        document.getElementById("userLocation").value =
            `Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}`;
        },
    () => {
        document.getElementById("userLocation").value =
            "Unable to fetch location.";
        }
    );
    } else {
    document.getElementById("userLocation").value =
        "Geolocation not supported.";
    }
}

// Run when modal opens
const emergencyModal = document.getElementById("emergencyModal");
emergencyModal.addEventListener("shown.bs.modal", getLocation);

// --------------------------
// ✅ FORM VALIDATION SECTION
// --------------------------

document.getElementById("emergencyForm").addEventListener("submit", (e) => {
    e.preventDefault();

    let errors = [];

        const name = document.querySelector("input[type='text']").value.trim();
        const contact = document.querySelector("input[type='tel']").value.trim();
        const email = document.querySelector("input[type='email']").value.trim();
        const emergencyType = document.getElementById("emergencyType").value;
        const description = document.querySelector("textarea").value.trim();
        const fileInput = document.querySelector("input[type='file']");

  // ⭐ Name Validation
    if (name.length < 3) {
    errors.push("Name must have at least 3 characters.");
    }

  // ⭐ Contact Number Validation (10 digits only)
    if (!/^[0-9]{10}$/.test(contact)) {
    errors.push("Contact number must be a valid 10-digit number.");
    }

  // ⭐ Email Validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.push("Enter a valid email address.");
    }

  // ⭐ Emergency Type Validation
    if (emergencyType === "") {
    errors.push("Please select the type of emergency.");
    }

  // ⭐ Description Validation
    if (description.length < 10) {
    errors.push("Description must be at least 10 characters.");
    }

  // ⭐ File Size Validation (max 10MB)
    if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    if (file.size > 10 * 1024 * 1024) {
        errors.push("Uploaded file must be less than 10MB.");
    }
    }

  // ❌ If errors exist → show alert
    if (errors.length > 0) {
    alert("⚠️ Please fix the following errors:\n\n" + errors.join("\n"));
    return;
    }

  // ✅ If everything is valid
    alert("✅ Emergency Report Submitted Successfully! Authorities have been notified.");

    const modal = bootstrap.Modal.getInstance(emergencyModal);
    modal.hide();
});

