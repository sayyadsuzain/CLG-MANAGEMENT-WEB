// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Sample notices data (in a real application, this would come from a backend)
    const notices = [
        {
            title: 'Mid-Term Examination Schedule',
            date: '2024-03-15',
            content: 'Mid-term examinations will begin from March 25th. Check the detailed schedule in your student portal.'
        },
        {
            title: 'Annual Sports Day',
            date: '2024-03-20',
            content: 'Annual Sports Day will be held on April 5th. All students are encouraged to participate.'
        },
        {
            title: 'Faculty Development Program',
            date: '2024-03-22',
            content: 'A week-long faculty development program on "Modern Teaching Methods" starts from April 1st.'
        }
    ];

    // Function to display notices
    function displayNotices() {
        const noticeBoard = document.querySelector('.notice-board');
        if (!noticeBoard) return;

        notices.forEach(notice => {
            const noticeElement = document.createElement('div');
            noticeElement.className = 'notice-item bg-white p-3 mb-3 rounded shadow-sm';
            noticeElement.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="mb-0">${notice.title}</h5>
                    <small class="text-muted">${formatDate(notice.date)}</small>
                </div>
                <p class="mb-0">${notice.content}</p>
            `;
            noticeBoard.appendChild(noticeElement);
        });
    }

    // Format date function
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }

    // Handle login forms
    const studentLoginForm = document.getElementById('studentLoginForm');
    const facultyLoginForm = document.getElementById('facultyLoginForm');

    if (studentLoginForm) {
        studentLoginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleLogin('student', this);
        });
    }

    if (facultyLoginForm) {
        facultyLoginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleLogin('faculty', this);
        });
    }

    // Login handler function
    function handleLogin(userType, form) {
        const formData = new FormData(form);
        // In a real application, this would make an API call to the backend
        console.log(`${userType} login:`, Object.fromEntries(formData));
        
        // Show success message (temporary)
        const alert = document.createElement('div');
        alert.className = 'alert alert-success mt-3';
        alert.textContent = 'Login successful! Redirecting...';
        form.appendChild(alert);
        
        // Remove alert after 3 seconds
        setTimeout(() => {
            alert.remove();
        }, 3000);
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Initialize notice board
    displayNotices();

    // Add animation to feature cards on scroll
    const observerOptions = {
        threshold: 0.2
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease-out';
        observer.observe(card);
    });
}); 