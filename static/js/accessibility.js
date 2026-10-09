/**
 * AccessMitra - Accessibility Controller
 * Manages Contrast Modes, Font Scaling, Dyslexia Font, Reading Ruler,
 * Keyboard Navigation Shortcuts, and Text-to-Speech (Web Speech API).
 */

(function () {
  'use strict';

  const STORAGE_KEY_CONTRAST = 'accessmitra_contrast_mode';
  const STORAGE_KEY_FONT = 'accessmitra_font_size';
  const STORAGE_KEY_DYSLEXIA = 'accessmitra_dyslexia_mode';

  // 1. Contrast Controller
  function initContrast() {
    const savedMode = localStorage.getItem(STORAGE_KEY_CONTRAST) || 'standard';
    applyContrastMode(savedMode);

    document.querySelectorAll('[data-contrast-mode]').forEach(btn => {
      btn.addEventListener('click', function () {
        const mode = this.getAttribute('data-contrast-mode');
        applyContrastMode(mode);
        localStorage.setItem(STORAGE_KEY_CONTRAST, mode);
        announceScreenReader(`Contrast mode set to ${mode}`);
      });
    });
  }

  function applyContrastMode(mode) {
    document.body.classList.remove('theme-dark-contrast', 'theme-yellow-contrast');
    document.querySelectorAll('[data-contrast-mode]').forEach(b => b.classList.remove('active'));

    if (mode === 'dark') {
      document.body.classList.add('theme-dark-contrast');
    } else if (mode === 'yellow') {
      document.body.classList.add('theme-yellow-contrast');
    }

    const activeBtn = document.querySelector(`[data-contrast-mode="${mode}"]`);
    if (activeBtn) activeBtn.classList.add('active');
  }

  // 2. Font Size Scaling Controller
  function initFontScaling() {
    const savedFont = localStorage.getItem(STORAGE_KEY_FONT) || 'base';
    applyFontSize(savedFont);

    document.querySelectorAll('[data-font-size]').forEach(btn => {
      btn.addEventListener('click', function () {
        const size = this.getAttribute('data-font-size');
        applyFontSize(size);
        localStorage.setItem(STORAGE_KEY_FONT, size);
        announceScreenReader(`Font size set to ${size}`);
      });
    });
  }

  function applyFontSize(size) {
    document.documentElement.classList.remove('font-base', 'font-lg', 'font-xl');
    document.querySelectorAll('[data-font-size]').forEach(b => b.classList.remove('active'));

    if (size === 'lg') {
      document.documentElement.classList.add('font-lg');
    } else if (size === 'xl') {
      document.documentElement.classList.add('font-xl');
    } else {
      document.documentElement.classList.add('font-base');
    }

    const activeBtn = document.querySelector(`[data-font-size="${size}"]`);
    if (activeBtn) activeBtn.classList.add('active');
  }

  // 3. Dyslexia Font Toggle
  function initDyslexiaFont() {
    const isDyslexia = localStorage.getItem(STORAGE_KEY_DYSLEXIA) === 'true';
    if (isDyslexia) {
      document.body.classList.add('font-dyslexia');
    }

    const toggleBtn = document.getElementById('btn-dyslexia-font');
    if (toggleBtn) {
      if (isDyslexia) toggleBtn.classList.add('active');
      toggleBtn.addEventListener('click', function () {
        const active = document.body.classList.toggle('font-dyslexia');
        toggleBtn.classList.toggle('active', active);
        localStorage.setItem(STORAGE_KEY_DYSLEXIA, active ? 'true' : 'false');
        announceScreenReader(active ? 'Dyslexia-friendly reading font enabled' : 'Default font restored');
      });
    }
  }

  // 4. Reading Guide Ruler (Horizontal tracking line)
  function initReadingRuler() {
    let ruler = document.getElementById('reading-guide-ruler');
    if (!ruler) {
      ruler = document.createElement('div');
      ruler.id = 'reading-guide-ruler';
      ruler.setAttribute('aria-hidden', 'true');
      document.body.appendChild(ruler);
    }

    const toggleBtn = document.getElementById('btn-reading-ruler');
    let isRulerActive = false;

    function handleMouseMove(e) {
      if (isRulerActive && ruler) {
        ruler.style.top = `${e.clientY}px`;
      }
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        isRulerActive = !isRulerActive;
        ruler.classList.toggle('active', isRulerActive);
        toggleBtn.classList.toggle('active', isRulerActive);

        if (isRulerActive) {
          window.addEventListener('mousemove', handleMouseMove);
          announceScreenReader('Reading guide ruler enabled. Move pointer over text.');
        } else {
          window.removeEventListener('mousemove', handleMouseMove);
          announceScreenReader('Reading guide ruler disabled');
        }
      });
    }
  }

  // 5. Text-To-Speech (TTS) Engine
  let currentUtterance = null;
  let ttsPanel = null;

  function initTTS() {
    if (!('speechSynthesis' in window)) {
      console.warn('AccessMitra: Speech Synthesis is not supported in this browser.');
      return;
    }

    // Create floating playback controls panel
    ttsPanel = document.createElement('div');
    ttsPanel.className = 'tts-floating-panel';
    ttsPanel.style.display = 'none';
    ttsPanel.innerHTML = `
      <div class="tts-panel-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
        </svg>
        <span>AccessMitra Voice Reader</span>
      </div>
      <button class="tts-btn" id="tts-btn-pause" title="Pause reading" aria-label="Pause Voice">⏸</button>
      <button class="tts-btn" id="tts-btn-resume" title="Resume reading" aria-label="Resume Voice" style="display:none;">▶</button>
      <button class="tts-btn" id="tts-btn-stop" title="Stop reading" aria-label="Stop Voice">⏹</button>
    `;
    document.body.appendChild(ttsPanel);

    document.getElementById('tts-btn-pause').addEventListener('click', () => {
      window.speechSynthesis.pause();
      document.getElementById('tts-btn-pause').style.display = 'none';
      document.getElementById('tts-btn-resume').style.display = 'flex';
      announceScreenReader('Speech paused');
    });

    document.getElementById('tts-btn-resume').addEventListener('click', () => {
      window.speechSynthesis.resume();
      document.getElementById('tts-btn-resume').style.display = 'none';
      document.getElementById('tts-btn-pause').style.display = 'flex';
      announceScreenReader('Speech resumed');
    });

    document.getElementById('tts-btn-stop').addEventListener('click', () => {
      stopTTS();
      announceScreenReader('Speech stopped');
    });
  }

  function speakText(text, title = '') {
    if (!('speechSynthesis' in window)) {
      alert('Text-to-speech is not supported on this device/browser.');
      return;
    }

    window.speechSynthesis.cancel();

    const cleanText = text.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    if (!cleanText) return;

    currentUtterance = new SpeechSynthesisUtterance(cleanText);
    currentUtterance.rate = 0.95; // slightly slower for enhanced clarity
    currentUtterance.pitch = 1.0;

    // Pick Indian English or Hindi voice if available
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.lang === 'en-IN' || v.name.includes('India')) ||
                           voices.find(v => v.lang.startsWith('en')) ||
                           voices[0];
    if (preferredVoice) currentUtterance.voice = preferredVoice;

    if (ttsPanel) {
      ttsPanel.style.display = 'flex';
      document.getElementById('tts-btn-pause').style.display = 'flex';
      document.getElementById('tts-btn-resume').style.display = 'none';
    }

    currentUtterance.onend = () => {
      if (ttsPanel) ttsPanel.style.display = 'none';
    };

    currentUtterance.onerror = (e) => {
      console.warn('TTS Error:', e);
      if (ttsPanel) ttsPanel.style.display = 'none';
    };

    window.speechSynthesis.speak(currentUtterance);
    announceScreenReader(`Reading aloud: ${title || 'Selected content'}`);
  }

  function stopTTS() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    if (ttsPanel) ttsPanel.style.display = 'none';
  }

  // 6. Screen Reader Announcer (aria-live region)
  let liveRegion = null;
  function announceScreenReader(message) {
    if (!liveRegion) {
      liveRegion = document.getElementById('global-live-region');
      if (!liveRegion) {
        liveRegion = document.createElement('div');
        liveRegion.id = 'global-live-region';
        liveRegion.className = 'sr-only';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        document.body.appendChild(liveRegion);
      }
    }
    liveRegion.textContent = message;
  }

  // 7. Keyboard Navigation Shortcuts Handler
  function initKeyboardShortcuts() {
    window.addEventListener('keydown', function (e) {
      // Escape closes any open modal or drawer
      if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal-backdrop.active');
        if (activeModal) {
          activeModal.classList.remove('active');
          stopTTS();
          announceScreenReader('Dialog closed');
        }
        return;
      }

      // If user is inside an input/textarea, skip single key triggers (except escape)
      const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);

      // Alt + S: Focus Search Input
      if (e.altKey && e.key.toLowerCase() === 's') {
        e.preventDefault();
        const searchInput = document.getElementById('scheme-search-input');
        if (searchInput) {
          searchInput.focus();
          announceScreenReader('Search box focused');
        }
      }

      // Alt + F: Focus Category Filters
      if (e.altKey && e.key.toLowerCase() === 'f') {
        e.preventDefault();
        const categoryFilter = document.getElementById('filter-category');
        if (categoryFilter) {
          categoryFilter.focus();
          announceScreenReader('Category filter focused');
        }
      }

      // Alt + H: Go to Helplines
      if (e.altKey && e.key.toLowerCase() === 'h') {
        e.preventDefault();
        const helplineLink = document.getElementById('nav-helplines');
        if (helplineLink) helplineLink.click();
      }

      // Alt + R: Toggle Reading Guide Ruler
      if (e.altKey && e.key.toLowerCase() === 'r') {
        e.preventDefault();
        const rulerBtn = document.getElementById('btn-reading-ruler');
        if (rulerBtn) rulerBtn.click();
      }

      // Shift + ? : Show Shortcuts Modal
      if (e.shiftKey && e.key === '?' && !isInput) {
        e.preventDefault();
        const shortcutsModal = document.getElementById('modal-shortcuts');
        if (shortcutsModal) {
          shortcutsModal.classList.add('active');
          const closeBtn = shortcutsModal.querySelector('.modal-close-btn');
          if (closeBtn) closeBtn.focus();
          announceScreenReader('Keyboard shortcuts dialog opened');
        }
      }
    });
  }

  // Public AccessMitra API for other scripts
  window.AccessMitra = {
    announce: announceScreenReader,
    speak: speakText,
    stopSpeech: stopTTS
  };

  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    initContrast();
    initFontScaling();
    initDyslexiaFont();
    initReadingRuler();
    initTTS();
    initKeyboardShortcuts();
  });
})();
