/**
 * TPC Portal - Custom Vanilla JavaScript
 * Keep this file lightweight and focused on common interactive behaviors.
 * No heavy frameworks — just plain JS + Bootstrap's JS bundle.
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {

    // =============================================
    // 1. Auto-dismiss flash messages after 5 seconds
    // =============================================
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)'); // Keep danger alerts persistent
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click(); // Bootstrap dismisses on click
            } else {
                alert.classList.remove('show');
                alert.classList.add('fade');
                setTimeout(() => alert.remove(), 200);
            }
        }, 5000);
    });


    // =============================================
    // 2. Confirm before critical actions (e.g. logout, apply)
    // =============================================
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });


    // =============================================
    // 3. Enhance all external links to open in new tab safely
    // =============================================
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        if (!link.href.includes(window.location.hostname)) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });


    // =============================================
    // 4. Simple form input validation feedback (visual only)
    // =============================================
    document.querySelectorAll('input[required], textarea[required]').forEach(input => {
        input.addEventListener('invalid', function () {
            this.classList.add('is-invalid');
        });

        input.addEventListener('input', function () {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
            }
        });
    });


    // =============================================
    // 5. Optional: Smooth scroll to top button (if you add one later)
    // =============================================
    const scrollTopBtn = document.createElement('button');
    scrollTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    scrollTopBtn.className = 'btn btn-primary position-fixed bottom-0 end-0 m-4 shadow';
    scrollTopBtn.style.display = 'none';
    scrollTopBtn.style.zIndex = '1000';
    scrollTopBtn.style.borderRadius = '50%';
    scrollTopBtn.style.width = '50px';
    scrollTopBtn.style.height = '50px';
    scrollTopBtn.style.fontSize = '1.5rem';
    document.body.appendChild(scrollTopBtn);

    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            scrollTopBtn.style.display = 'block';
        } else {
            scrollTopBtn.style.display = 'none';
        }
    });

    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });


    // =============================================
    // 6. Optional: Console welcome message (for developers)
    // =============================================
    console.log(
        '%cTPC Portal%c\nBuilt with Flask + Bootstrap 5 + Vanilla JS\nHappy coding, Nitish!',
        'background:#0d6efd;color:white;padding:8px 12px;border-radius:4px;font-weight:bold;font-size:16px;',
        'color:#0d6efd;font-weight:bold;'
    );

});