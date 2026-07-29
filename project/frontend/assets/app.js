/* ============================================================================
   VPN Sentinel — shared front-end behaviour
   Previously each page defined its own copy of the nav toggle (and two pages
   used a different implementation and different element ids, so the mobile menu
   behaved inconsistently). One definition, used everywhere.
   ========================================================================== */
(function () {
    'use strict';

    /* ---------- Mobile navigation ---------- */
    function navEl()    { return document.getElementById('navLinks'); }
    function toggleEl() { return document.querySelector('.nav-toggle'); }

    function setNav(open) {
        var links = navEl();
        if (!links) return;
        links.classList.toggle('open', open);
        var btn = toggleEl();
        if (btn) btn.setAttribute('aria-expanded', String(open));
    }

    // Exposed globally because the markup wires it via onclick="toggleNav()".
    window.toggleNav = function (force) {
        var links = navEl();
        if (!links) return;
        setNav(typeof force === 'boolean' ? force : !links.classList.contains('open'));
    };

    /* ---------- Active nav item ----------
       Each page used to hard-code class="active" on its own link, which silently
       went stale whenever routes were renamed. Derive it from the URL instead. */
    function markActiveNav() {
        var path = window.location.pathname.replace(/\/+$/, '') || '/';
        document.querySelectorAll('.nav-links a').forEach(function (a) {
            var href = (a.getAttribute('href') || '').replace(/\/+$/, '') || '/';
            a.classList.toggle('active', href === path);
            if (href === path) a.setAttribute('aria-current', 'page');
        });
    }

    /* ---------- Copy to clipboard ----------
       Any element with data-copy="<selector>" copies that element's text. */
    function wireCopyButtons() {
        document.querySelectorAll('[data-copy]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var target = document.querySelector(btn.getAttribute('data-copy'));
                if (!target) return;
                var text = (target.innerText || '').trim();
                if (!text) return;

                var done = function () {
                    var original = btn.getAttribute('data-label') || 'Copy';
                    btn.classList.add('copied');
                    btn.textContent = 'Copied';
                    setTimeout(function () {
                        btn.classList.remove('copied');
                        btn.textContent = original;
                    }, 1600);
                };

                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(done).catch(function () {});
                } else {
                    // Fallback for non-secure contexts, where the async API is unavailable.
                    var ta = document.createElement('textarea');
                    ta.value = text;
                    ta.style.position = 'fixed';
                    ta.style.opacity = '0';
                    document.body.appendChild(ta);
                    ta.select();
                    try { document.execCommand('copy'); done(); } catch (e) {}
                    document.body.removeChild(ta);
                }
            });
        });
    }

    function init() {
        markActiveNav();
        wireCopyButtons();

        // Close the mobile menu after navigating.
        document.querySelectorAll('.nav-links a').forEach(function (link) {
            link.addEventListener('click', function () { window.toggleNav(false); });
        });

        // Escape closes the menu; it was previously only dismissable by tapping a link.
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') window.toggleNav(false);
        });

        // Tapping outside the menu closes it.
        document.addEventListener('click', function (e) {
            var links = navEl();
            if (!links || !links.classList.contains('open')) return;
            if (links.contains(e.target)) return;
            var btn = toggleEl();
            if (btn && btn.contains(e.target)) return;
            window.toggleNav(false);
        });

        // Reset the menu when resizing up to desktop, otherwise the dropdown can
        // stay flagged open and reappear on the next resize down.
        window.addEventListener('resize', function () {
            if (window.innerWidth > 900) window.toggleNav(false);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
