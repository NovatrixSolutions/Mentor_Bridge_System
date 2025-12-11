// Scroll smoothly to app section when user clicks "Enter Portal"
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("enterPortalBtn");
  
  if (btn) {
    btn.addEventListener("click", () => {
      const student = localStorage.getItem("student_id");
      if (student) {
        window.location.href = "./pages/dashboard.html";
      } else {
        window.location.href = "./pages/login.html";
      }
    });
  }

  // Check login state for navbar
  checkAuthState();
});

function checkAuthState() {
  const student = localStorage.getItem("student_id");
  const studentName = localStorage.getItem("student_name");
  const loginLink = document.getElementById('loginLink');
  const profileBtn = document.getElementById('profileBtn');
  const logoutBtn = document.getElementById('logoutBtn');

  if (student && loginLink && profileBtn && logoutBtn) {
    // User logged in - hide login, show profile/logout
    loginLink.style.display = 'none';
    profileBtn.style.display = 'inline-flex';
    logoutBtn.style.display = 'inline-flex';
    
    // Show student name on profile button
    if (studentName) {
      profileBtn.textContent = studentName;
    }
  } else {
    // User not logged in - show login, hide profile/logout
    if (loginLink) loginLink.style.display = 'inline-flex';
    if (profileBtn) profileBtn.style.display = 'none';
    if (logoutBtn) logoutBtn.style.display = 'none';
  }
}

function showProfile() {
  const studentId = localStorage.getItem('student_id');
  if (studentId) {
    window.location.href = `./pages/profile.html?id=${studentId}`;
  } else {
    // Not logged in - redirect to login
    alert('Please login first');
    window.location.href = './pages/login.html';
  }
}

function logout() {
  // Clear all student data
  localStorage.removeItem('student_id');
  localStorage.removeItem('student_name');
  localStorage.removeItem('student');
  localStorage.removeItem('feedback_alumni_id');
  localStorage.removeItem('feedback_alumni_name');
  localStorage.removeItem('chat_alumni_id');
  localStorage.removeItem('chat_alumni_name');
  
  // Redirect and refresh navbar
  window.location.href = './index.html';
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    e.preventDefault();
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});
