/**
 * AccessMitra - Interactive Scheme Eligibility Wizard
 * Step-by-step guided questionnaire calculating matching government schemes.
 */

(function () {
  'use strict';

  let currentStep = 1;
  const totalSteps = 4;

  const wizardForm = document.getElementById('eligibility-wizard-form');
  const resultsContainer = document.getElementById('wizard-results-container');
  const wizardCard = document.getElementById('wizard-step-card');

  function initWizard() {
    if (!wizardForm) return;

    // Step navigation buttons
    document.querySelectorAll('[data-wizard-next]').forEach(btn => {
      btn.addEventListener('click', () => {
        if (validateStep(currentStep)) {
          goToStep(currentStep + 1);
        }
      });
    });

    document.querySelectorAll('[data-wizard-prev]').forEach(btn => {
      btn.addEventListener('click', () => {
        goToStep(currentStep - 1);
      });
    });

    // Form submit
    wizardForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!validateStep(currentStep)) return;
      await submitEligibilityCheck();
    });

    // Range slider updates
    const pctSlider = document.getElementById('wizard-pct-slider');
    const pctOutput = document.getElementById('wizard-pct-output');
    if (pctSlider && pctOutput) {
      pctSlider.addEventListener('input', () => {
        pctOutput.textContent = `${pctSlider.value}%`;
      });
    }

    // Income presets
    document.querySelectorAll('.income-preset-btn').forEach(btn => {
      btn.addEventListener('click', function () {
        document.querySelectorAll('.income-preset-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        const val = this.getAttribute('data-income');
        const input = document.getElementById('wizard-income');
        if (input) input.value = val;
      });
    });
  }

  function validateStep(step) {
    if (step === 1) {
      const selected = document.querySelector('input[name="disability_type"]:checked') ||
                       document.getElementById('wizard-disability-select');
      if (!selected || !selected.value) {
        alert('Please select your disability type to proceed.');
        return false;
      }
    }
    return true;
  }

  function goToStep(step) {
    if (step < 1 || step > totalSteps) return;

    document.querySelectorAll('.wizard-step-panel').forEach(p => {
      p.style.display = 'none';
    });

    const targetPanel = document.getElementById(`wizard-step-${step}`);
    if (targetPanel) {
      targetPanel.style.display = 'block';
    }

    currentStep = step;
    updateStepIndicator(step);

    if (window.AccessMitra) {
      window.AccessMitra.announce(`Step ${step} of ${totalSteps}`);
    }
  }

  function updateStepIndicator(step) {
    const indicator = document.getElementById('wizard-step-indicator');
    if (indicator) {
      indicator.textContent = `Step ${step} of ${totalSteps}`;
    }

    const progressBar = document.getElementById('wizard-progress-fill');
    if (progressBar) {
      const pct = ((step - 1) / (totalSteps - 1)) * 100;
      progressBar.style.width = `${pct}%`;
    }
  }

  async function submitEligibilityCheck() {
    const disabilityType = document.querySelector('input[name="disability_type"]:checked')?.value ||
                           document.getElementById('wizard-disability-select')?.value || 'All Disabilities';
    const age = parseInt(document.getElementById('wizard-age')?.value || '25', 10);
    const disabilityPct = parseInt(document.getElementById('wizard-pct-slider')?.value || '40', 10);
    const annualIncome = parseInt(document.getElementById('wizard-income')?.value || '180000', 10);
    const primaryNeed = document.querySelector('input[name="primary_need"]:checked')?.value || 'All';

    if (resultsContainer) {
      resultsContainer.style.display = 'block';
      resultsContainer.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--primary-navy);">
          <div style="font-size: 2.5rem; margin-bottom: 12px; animation: spin 1s infinite linear;">⚙️</div>
          <h3 style="font-size: 1.3rem;">Evaluating Scheme Rules & Guidelines...</h3>
          <p style="color: var(--text-muted);">Comparing your criteria against official myScheme & DEPwD rules.</p>
        </div>
      `;
      resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    try {
      const res = await fetch('/api/check-eligibility', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          disability_type: disabilityType,
          age: age,
          disability_pct: disabilityPct,
          annual_income: annualIncome,
          primary_need: primaryNeed
        })
      });

      const data = await res.json();
      if (data.status === 'success') {
        renderResults(data.data, { disabilityType, age, disabilityPct, annualIncome, primaryNeed });
      } else {
        resultsContainer.innerHTML = `<div style="color: red; padding: 20px;">Error calculating eligibility: ${data.message}</div>`;
      }
    } catch (err) {
      console.error(err);
      resultsContainer.innerHTML = `<div style="color: red; padding: 20px;">Network error connecting to calculation engine.</div>`;
    }
  }

  function renderResults(schemes, profile) {
    if (!resultsContainer) return;

    if (schemes.length === 0) {
      resultsContainer.innerHTML = `
        <div style="background: #fffbeb; border: 2px solid #fde68a; border-radius: 16px; padding: 36px; text-align: center;">
          <div style="font-size: 2.5rem; margin-bottom: 12px;">⚠️</div>
          <h3 style="color: #92400e; font-size: 1.3rem; margin-bottom: 8px;">No Direct Scheme Matches Found</h3>
          <p style="color: #78350f; max-width: 550px; margin: 0 auto 20px;">
            Based on your entered disability percentage (${profile.disabilityPct}%) or family income (₹${profile.annualIncome.toLocaleString('en-IN')}),
            certain strict thresholds were not met. However, you are always entitled to Universal UDID identification and CCPD legal protections!
          </p>
          <a href="/rights" class="btn-card-details">Know Your Rights under RPwD Act</a>
        </div>
      `;
      return;
    }

    const html = `
      <div style="background: #ffffff; border: 2px solid #10b981; border-radius: 16px; padding: 32px; box-shadow: var(--shadow-xl); margin-top: 30px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
          <div>
            <span style="background: #ecfdf5; color: #047857; font-weight: 800; font-size: 0.85rem; padding: 6px 14px; border-radius: 9999px;">
              ✓ Verification Complete
            </span>
            <h3 style="font-size: 1.6rem; font-weight: 800; color: var(--primary-navy); margin-top: 8px;">
              You Qualify for ${schemes.length} Government Welfare Scheme${schemes.length === 1 ? '' : 's'}!
            </h3>
          </div>
          <button class="action-pill-btn" onclick="window.print()" style="background: #0f172a; color: #fff;">
            🖨️ Print Eligibility Report
          </button>
        </div>

        <div style="display: grid; gap: 20px;">
          ${schemes.map((s, idx) => `
            <div style="border: 1px solid var(--border-light); border-radius: 12px; padding: 20px; background: #f8fafc; display: flex; flex-direction: column; gap: 12px;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
                <div>
                  <span style="background: #eff6ff; color: #1d4ed8; font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 9999px;">
                    ${s.category}
                  </span>
                  <h4 style="font-size: 1.2rem; font-weight: 700; color: var(--primary-navy); margin-top: 6px;">
                    ${s.name}
                  </h4>
                  <div style="font-size: 0.8rem; color: var(--text-subtle);">${s.ministry}</div>
                </div>
                <div style="text-align: right; flex-shrink: 0;">
                  <span style="background: #dbeafe; color: #1e40af; font-weight: 800; font-size: 0.85rem; padding: 4px 10px; border-radius: 9999px;">
                    Match Score: ${s.match_score} pts
                  </span>
                </div>
              </div>

              <div style="background: #ffffff; padding: 12px; border-radius: 8px; border-left: 4px solid #10b981;">
                <strong style="font-size: 0.82rem; color: #047857; text-transform: uppercase;">Why You Qualify:</strong>
                <ul style="margin-left: 18px; margin-top: 4px; font-size: 0.88rem; color: var(--text-main);">
                  ${(s.eligibility_reasons || []).map(r => `<li>${r}</li>`).join('')}
                </ul>
              </div>

              <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; padding-top: 8px;">
                <a href="${s.application_url || s.official_portal_url}" target="_blank" rel="noopener noreferrer" class="btn-card-details" style="background:#ea580c;">
                  Apply on Official Portal ↗
                </a>
                <button class="btn-card-details" onclick="window.AccessMitraOpenModal(${s.id})">
                  Read Full Rules
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    resultsContainer.innerHTML = html;
    resultsContainer.scrollIntoView({ behavior: 'smooth' });

    if (window.AccessMitra) {
      window.AccessMitra.announce(`You qualify for ${schemes.length} government schemes.`);
    }
  }

  document.addEventListener('DOMContentLoaded', initWizard);
})();
