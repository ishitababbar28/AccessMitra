/**
 * AccessMitra - Primary Application Logic
 * Dynamic Search, Live Filters, Scheme Cards Rendering, Detail Modal,
 * Bookmarks ("Mera Pitara"), and Screen Reader announcements.
 */

(function () {
  'use strict';

  const STORAGE_KEY_BOOKMARKS = 'accessmitra_saved_schemes';
  let allSchemesCache = [];
  let lastFocusedElement = null;

  // DOM Elements
  const searchInput = document.getElementById('scheme-search-input');
  const searchClearBtn = document.getElementById('search-clear-btn');
  const filterCategory = document.getElementById('filter-category');
  const filterDisability = document.getElementById('filter-disability');
  const filterLevel = document.getElementById('filter-level');
  const filterSort = document.getElementById('filter-sort');
  const schemesContainer = document.getElementById('schemes-container');
  const resultsCounter = document.getElementById('results-counter');
  const detailModal = document.getElementById('modal-scheme-detail');
  const navSavedCounter = document.getElementById('nav-saved-count');

  // 1. Bookmarks Management
  function getBookmarks() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY_BOOKMARKS)) || [];
    } catch {
      return [];
    }
  }

  function saveBookmarks(bookmarks) {
    localStorage.setItem(STORAGE_KEY_BOOKMARKS, JSON.stringify(bookmarks));
    updateBookmarkBadge();
  }

  function isBookmarked(schemeId) {
    return getBookmarks().includes(schemeId);
  }

  function toggleBookmark(schemeId, schemeName) {
    let bookmarks = getBookmarks();
    const idx = bookmarks.indexOf(schemeId);
    let added = false;

    if (idx > -1) {
      bookmarks.splice(idx, 1);
    } else {
      bookmarks.push(schemeId);
      added = true;
    }

    saveBookmarks(bookmarks);
    updateBookmarkButtons(schemeId, added);

    const msg = added
      ? `"${schemeName}" added to My Saved Schemes`
      : `"${schemeName}" removed from My Saved Schemes`;
    showToast(msg);
    if (window.AccessMitra) window.AccessMitra.announce(msg);
  }

  function updateBookmarkBadge() {
    const count = getBookmarks().length;
    if (navSavedCounter) {
      navSavedCounter.textContent = count;
      navSavedCounter.style.display = count > 0 ? 'inline-block' : 'none';
    }
  }

  function updateBookmarkButtons(schemeId, isAdded) {
    document.querySelectorAll(`[data-bookmark-id="${schemeId}"]`).forEach(btn => {
      btn.classList.toggle('active-bookmark', isAdded);
      btn.setAttribute('aria-pressed', isAdded ? 'true' : 'false');
      btn.title = isAdded ? 'Remove from Saved Schemes' : 'Save Scheme';
    });
  }

  // 2. Fetch Schemes API
  async function fetchSchemes() {
    const params = new URLSearchParams();

    if (searchInput && searchInput.value.trim()) {
      params.append('q', searchInput.value.trim());
    }
    if (filterCategory && filterCategory.value !== 'all') {
      params.append('category', filterCategory.value);
    }
    if (filterDisability && filterDisability.value !== 'all') {
      params.append('disability', filterDisability.value);
    }
    if (filterLevel && filterLevel.value !== 'all') {
      params.append('level', filterLevel.value);
    }
    if (filterSort && filterSort.value) {
      params.append('sort', filterSort.value);
    }

    if (schemesContainer) {
      schemesContainer.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--text-muted);">
          <div style="font-size: 2rem; margin-bottom: 12px; animation: spin 1s linear infinite;">⏳</div>
          <p style="font-weight: 600;">Searching verified Indian government schemes...</p>
        </div>
      `;
    }

    try {
      const response = await fetch(`/api/schemes?${params.toString()}`);
      const data = await response.json();

      if (data.status === 'success') {
        allSchemesCache = data.data;
        renderSchemes(data.data);
        updateResultsCounter(data.count);
      } else {
        renderError("Failed to retrieve government schemes. Please refresh.");
      }
    } catch (err) {
      console.error("Fetch error:", err);
      renderError("Network error connecting to AccessMitra database.");
    }
  }

  // 3. Render Scheme Cards
  function renderSchemes(schemes) {
    if (!schemesContainer) return;

    if (schemes.length === 0) {
      schemesContainer.innerHTML = `
        <div style="grid-column: 1/-1; background: var(--surface-white); border: 2px dashed var(--border-strong); border-radius: var(--border-radius-md); padding: 60px 24px; text-align: center;">
          <div style="font-size: 3rem; margin-bottom: 16px;">🔍</div>
          <h3 style="font-size: 1.35rem; color: var(--primary-navy); margin-bottom: 8px;">No matching government schemes found</h3>
          <p style="color: var(--text-muted); max-width: 500px; margin: 0 auto 20px;">
            Try loosening your filters, checking different disability categories, or clearing your keyword search.
          </p>
          <button class="btn-card-details" onclick="window.AccessMitraResetFilters()">Reset All Filters</button>
        </div>
      `;
      return;
    }

    const cardsHtml = schemes.map(s => {
      const bookmarked = isBookmarked(s.id);
      const incomeText = s.max_annual_income > 0
        ? `Annual Income ≤ ₹${(s.max_annual_income).toLocaleString('en-IN')}`
        : 'Open to All Income Groups';

      return `
        <article class="scheme-card" data-scheme-id="${s.id}" aria-labelledby="scheme-title-${s.id}">
          ${s.is_featured ? '<div class="scheme-card-featured-bar" title="Featured Flagship Scheme"></div>' : ''}
          
          <div class="card-top-meta">
            <span class="card-category-badge">${escapeHtml(s.category)}</span>
            <span class="card-level-badge">${escapeHtml(s.level)} Govt</span>
          </div>

          <div class="card-ministry">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 2L1 7v2h22V7L12 2zm10 18H2v2h20v-2zM4 10h3v8H4v-8zm6 0h4v8h-4v-8zm7 0h3v8h-3v-8z"/>
            </svg>
            <span>${escapeHtml(s.ministry)}</span>
          </div>

          <h3 class="card-title" id="scheme-title-${s.id}">
            <a href="/scheme/${s.slug}" onclick="event.preventDefault(); window.AccessMitraOpenModal(${s.id});">
              ${escapeHtml(s.name)}
            </a>
          </h3>

          <p class="card-description">${escapeHtml(s.brief_description)}</p>

          <div class="card-eligibility-summary">
            <div><strong>Disability:</strong> ${escapeHtml(s.target_disability)} (${s.min_disability_pct}%+ min)</div>
            <div><strong>Income:</strong> ${incomeText}</div>
          </div>

          <div class="card-tags-row">
            <span class="card-tag">🎯 ${escapeHtml(s.target_disability)}</span>
            ${s.helpline_number ? `<span class="card-tag" style="background:#ecfdf5; color:#047857; font-weight:700;">📞 ${escapeHtml(s.helpline_number)}</span>` : ''}
          </div>

          <div class="card-actions-row">
            <button class="btn-card-details" onclick="window.AccessMitraOpenModal(${s.id})" aria-label="View complete details of ${escapeHtml(s.name)}">
              View Details
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>

            <div class="card-icon-actions">
              <button class="btn-icon-action" onclick="window.AccessMitraReadCard(${s.id})" title="Listen to scheme details aloud" aria-label="Listen to scheme summary">
                🔊
              </button>

              <button class="btn-icon-action ${bookmarked ? 'active-bookmark' : ''}" 
                      data-bookmark-id="${s.id}" 
                      onclick="window.AccessMitraToggleBookmark(${s.id}, '${escapeQuote(s.name)}')" 
                      title="${bookmarked ? 'Remove from Saved' : 'Save Scheme'}" 
                      aria-pressed="${bookmarked ? 'true' : 'false'}"
                      aria-label="Bookmark scheme">
                🔖
              </button>

              <a href="${s.official_portal_url}" target="_blank" rel="noopener noreferrer" class="btn-icon-action" title="Visit official government portal (opens in new tab)" aria-label="Official Portal for ${escapeHtml(s.name)}">
                ↗
              </a>
            </div>
          </div>
        </article>
      `;
    }).join('');

    schemesContainer.innerHTML = cardsHtml;
  }

  function updateResultsCounter(count) {
    if (resultsCounter) {
      resultsCounter.textContent = `Showing ${count} verified scheme${count === 1 ? '' : 's'}`;
    }
    if (window.AccessMitra) {
      window.AccessMitra.announce(`Found ${count} matching government schemes.`);
    }
  }

  function renderError(message) {
    if (schemesContainer) {
      schemesContainer.innerHTML = `
        <div style="grid-column: 1/-1; background: #fef2f2; border: 1px solid #fecaca; border-radius: var(--border-radius-md); padding: 40px 24px; text-align: center; color: #991b1b;">
          <h3 style="margin-bottom: 8px;">Unable to load data</h3>
          <p>${escapeHtml(message)}</p>
        </div>
      `;
    }
  }

  // 4. Modal View Controller
  window.AccessMitraOpenModal = async function (schemeId) {
    lastFocusedElement = document.activeElement;

    let scheme = allSchemesCache.find(s => s.id === schemeId);
    if (!scheme) {
      try {
        const res = await fetch(`/api/schemes/${schemeId}`);
        const data = await res.json();
        if (data.status === 'success') scheme = data.data;
      } catch (e) {
        console.error("Failed to load scheme:", e);
      }
    }

    if (!scheme || !detailModal) return;

    const modalBody = detailModal.querySelector('.modal-body');
    const modalTitle = detailModal.querySelector('#modal-title');
    const modalCategory = detailModal.querySelector('#modal-category');
    const modalMinistry = detailModal.querySelector('#modal-ministry');
    const modalApplyLink = detailModal.querySelector('#modal-apply-link');
    const modalListenBtn = detailModal.querySelector('#modal-listen-btn');

    modalTitle.textContent = scheme.name;
    modalCategory.textContent = `${scheme.category} • ${scheme.level} Government`;
    modalMinistry.textContent = scheme.ministry;
    modalApplyLink.href = scheme.application_url || scheme.official_portal_url;

    // Build Detailed Modal Content
    modalBody.innerHTML = `
      <div class="modal-section" style="background: #f8fafc; padding: 18px; border-radius: 12px; margin-bottom: 24px; border: 1px solid var(--border-light);">
        <p style="font-size: 1.05rem; font-weight: 500; color: var(--text-main); margin-bottom: 12px;">
          ${escapeHtml(scheme.brief_description)}
        </p>
        <div style="display: flex; flex-wrap: wrap; gap: 12px; font-size: 0.85rem; color: var(--text-muted);">
          <span><strong>Target Group:</strong> ${escapeHtml(scheme.target_disability)} (Min ${scheme.min_disability_pct}%)</span>
          <span><strong>Income Limit:</strong> ${scheme.max_annual_income > 0 ? `₹${scheme.max_annual_income.toLocaleString('en-IN')}/year` : 'No Income Ceiling'}</span>
          <span><strong>Age Eligibility:</strong> ${scheme.min_age === 0 && scheme.max_age >= 100 ? 'All Ages' : `${scheme.min_age} - ${scheme.max_age} Years`}</span>
        </div>
      </div>

      <div class="modal-section">
        <h4 class="modal-section-title">
          <span>🎁</span> Key Benefits & Entitlements
        </h4>
        <div style="white-space: pre-line; color: var(--text-main); font-size: 0.95rem; line-height: 1.7;">
          ${escapeHtml(scheme.benefits)}
        </div>
      </div>

      <div class="modal-section">
        <h4 class="modal-section-title">
          <span>📋</span> Eligibility Criteria Checklist
        </h4>
        <div style="white-space: pre-line; color: var(--text-main); font-size: 0.95rem; line-height: 1.7;">
          ${escapeHtml(scheme.eligibility)}
        </div>
      </div>

      <div class="modal-section">
        <h4 class="modal-section-title">
          <span>📝</span> Step-by-Step Application Process
        </h4>
        <div style="white-space: pre-line; color: var(--text-main); font-size: 0.95rem; line-height: 1.7; background: #fffbeb; padding: 16px; border-radius: 8px; border-left: 4px solid #f59e0b;">
          ${escapeHtml(scheme.application_process)}
        </div>
      </div>

      <div class="modal-section">
        <h4 class="modal-section-title">
          <span>📂</span> Mandatory Documents Required
        </h4>
        <div style="white-space: pre-line; color: var(--text-muted); font-size: 0.95rem; line-height: 1.7;">
          ${escapeHtml(scheme.documents_required)}
        </div>
      </div>

      <div class="modal-section" style="border-top: 1px solid var(--border-light); padding-top: 16px;">
        <h4 class="modal-section-title">
          <span>📞</span> Official Helpdesk & Grievance Contact
        </h4>
        <p style="font-size: 0.95rem; color: var(--text-main); line-height: 1.6;">
          ${escapeHtml(scheme.contact_details)}
        </p>
        ${scheme.helpline_number ? `
          <div style="margin-top: 12px;">
            <a href="tel:${scheme.helpline_number.replace(/[^0-9+]/g, '')}" class="helpline-phone-btn" style="display:inline-flex;">
              📞 Call Helpline: ${escapeHtml(scheme.helpline_number)}
            </a>
          </div>
        ` : ''}
      </div>
    `;

    modalListenBtn.onclick = () => {
      const readText = `${scheme.name}. ${scheme.brief_description}. Key Benefits: ${scheme.benefits}. Eligibility: ${scheme.eligibility}. Application Process: ${scheme.application_process}`;
      if (window.AccessMitra) window.AccessMitra.speak(readText, scheme.name);
    };

    detailModal.classList.add('active');
    detailModal.setAttribute('aria-hidden', 'false');
    const closeBtn = detailModal.querySelector('.modal-close-btn');
    if (closeBtn) closeBtn.focus();

    if (window.AccessMitra) {
      window.AccessMitra.announce(`Opened scheme details for ${scheme.name}`);
    }
  };

  window.AccessMitraCloseModal = function () {
    if (!detailModal) return;
    detailModal.classList.remove('active');
    detailModal.setAttribute('aria-hidden', 'true');
    if (window.AccessMitra) {
      window.AccessMitra.stopSpeech();
      window.AccessMitra.announce('Scheme details closed');
    }
    if (lastFocusedElement) lastFocusedElement.focus();
  };

  // Card Audio Reader
  window.AccessMitraReadCard = function (schemeId) {
    const scheme = allSchemesCache.find(s => s.id === schemeId);
    if (!scheme) return;
    const text = `${scheme.name}. Category: ${scheme.category}. ${scheme.brief_description}. Eligibility: ${scheme.eligibility.slice(0, 200)}...`;
    if (window.AccessMitra) {
      window.AccessMitra.speak(text, scheme.name);
    }
  };

  // Bookmark Toggle
  window.AccessMitraToggleBookmark = function (schemeId, name) {
    toggleBookmark(schemeId, name);
  };

  // Reset Filters
  window.AccessMitraResetFilters = function () {
    if (searchInput) searchInput.value = '';
    if (filterCategory) filterCategory.value = 'all';
    if (filterDisability) filterDisability.value = 'all';
    if (filterLevel) filterLevel.value = 'all';
    if (filterSort) filterSort.value = 'featured';

    document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
    const allChip = document.querySelector('.category-chip[data-category="all"]');
    if (allChip) allChip.classList.add('active');

    if (searchClearBtn) searchClearBtn.classList.remove('visible');
    fetchSchemes();
  };

  // Print Summary
  window.AccessMitraPrintModal = function () {
    window.print();
  };

  // Toast Notification
  function showToast(msg) {
    let toast = document.getElementById('accessmitra-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'accessmitra-toast';
      toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        background: #0f172a;
        color: #ffffff;
        padding: 12px 24px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        z-index: 10000;
        border: 2px solid #ea580c;
        display: none;
      `;
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.display = 'block';
    setTimeout(() => {
      toast.style.display = 'none';
    }, 3200);
  }

  // Helper Escape HTML
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function escapeQuote(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
  }

  // 5. Event Listeners Setup
  function initEventListeners() {
    let debounceTimer = null;

    if (searchInput) {
      searchInput.addEventListener('input', () => {
        if (searchClearBtn) {
          searchClearBtn.classList.toggle('visible', searchInput.value.length > 0);
        }
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          fetchSchemes();
        }, 300);
      });
    }

    if (searchClearBtn) {
      searchClearBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchClearBtn.classList.remove('visible');
        searchInput.focus();
        fetchSchemes();
      });
    }

    [filterCategory, filterDisability, filterLevel, filterSort].forEach(el => {
      if (el) {
        el.addEventListener('change', () => {
          fetchSchemes();
        });
      }
    });

    // Category chips
    document.querySelectorAll('.category-chip').forEach(chip => {
      chip.addEventListener('click', function () {
        document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
        this.classList.add('active');
        const cat = this.getAttribute('data-category');
        if (filterCategory) {
          filterCategory.value = cat;
        }
        fetchSchemes();
      });
    });

    // Close modal on click outside
    if (detailModal) {
      detailModal.addEventListener('click', (e) => {
        if (e.target === detailModal) {
          window.AccessMitraCloseModal();
        }
      });
    }

    // Initialize bookmark count
    updateBookmarkBadge();

    // Initial schemes fetch
    fetchSchemes();
  }

  document.addEventListener('DOMContentLoaded', initEventListeners);
})();
