# AccessMitra (एक्सेस मित्र)
### National Accessibility & Disability Welfare Portal for India

**AccessMitra** is an accessibility-focused, full-stack web application designed to connect Indian citizens with disabilities (*Divyangjan*), their families, caregivers, and social advocates to verified Central and State Government welfare schemes, assistive technologies, digital resources, and 24x7 verified emergency helplines.

---

## 🇮🇳 Verified Government Information Sources

AccessMitra strictly uses **real, authenticated government data** verified against official gazettes, ministerial reports, and portals:
- **myScheme Platform** ([myscheme.gov.in](https://myscheme.gov.in))
- **Department of Empowerment of Persons with Disabilities (DEPwD)** ([disabilityaffairs.gov.in](https://disabilityaffairs.gov.in))
- **Unique Disability ID (UDID) / Swavlamban Card Project** ([swavlambancard.gov.in](https://www.swavlambancard.gov.in))
- **Artificial Limbs Manufacturing Corporation of India (ALIMCO)** ([adip.depwd.gov.in](https://adip.depwd.gov.in))
- **The National Trust for Welfare of Persons with Autism, Cerebral Palsy, Intellectual Disability** ([thenationaltrust.gov.in](https://thenationaltrust.gov.in))
- **Chief Commissioner for Persons with Disabilities (CCPD)** ([ccdisabilities.nic.in](https://ccdisabilities.nic.in))
- **National Scholarship Portal (NSP)** ([scholarships.gov.in](https://scholarships.gov.in))
- **National Handicapped Finance and Development Corporation (NHFDC)** ([nhfdc.nic.in](https://www.nhfdc.nic.in))
- **Sugamya Pustakalaya / Daisy Forum of India** ([sugamyapustakalaya.in](https://sugamyapustakalaya.in))
- **Tele-MANAS & Kiran Mental Health Helplines** ([telemanas.mohfw.gov.in](https://telemanas.mohfw.gov.in))

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13 / Flask 3.1.0, SQLAlchemy 2.0, PyMySQL
- **Database**: 
  - **MySQL 8.0** (Production / Primary)
  - Seamless automatic fallback to **SQLite** (`accessmitra.db`) if MySQL credentials are not yet configured or server is unavailable, ensuring 100% zero-configuration out-of-the-box operation!
- **Frontend**: Semantic HTML5, Vanilla CSS3 (custom responsive design system without utility frameworks), Vanilla Modern JavaScript (ES6+)
- **Speech API**: Web Speech API (`SpeechSynthesis`) with Indian English & Hindi voice prioritization

---

## ♿ Accessibility Features (WCAG 2.1 AA/AAA & GIGW Compliant)

1. **Universal Accessibility Toolbar**:
   - **Text Size Adjustment**: Default (`A`), Large (`A+` / +15%), Extra Large (`A++` / +30%).
   - **Contrast Themes**:
     - *Standard*: Modern warm sapphire, saffron, and crisp off-white.
     - *Dark High Contrast*: Deep slate and glowing blue accents for light sensitivity.
     - *Yellow-on-Black (WCAG AAA)*: Specialized mode for low vision, macular degeneration, and cataract users.
   - **Dyslexia Font Support**: Enhanced letter-spacing (`0.08em`), word-spacing (`0.18em`), and increased line height (`1.9`).
   - **Reading Guide Ruler**: Horizontal guide ruler (toggleable with `Alt + R`) that follows mouse cursor or arrow keys to aid reading tracking.
   - **Text-to-Speech (TTS) Engine**: Integrated voice player to read aloud any scheme card, criteria checklist, or modal summary with pause, resume, and stop controls.
2. **Keyboard Navigation & ARIA**:
   - Skip to main content link (`#main-content`) visible on keyboard focus.
   - High-visibility focus indicator (3px solid orange with 3px offset).
   - Modal focus-trapping and `Escape` key listeners.
   - Dynamic `aria-live="polite"` live regions announcing search result counts to screen readers.
3. **Keyboard Shortcuts**:
   - `Alt + S`: Jump to search box
   - `Alt + F`: Focus category filter
   - `Alt + H`: Open Helplines directory
   - `Alt + R`: Toggle Reading Guide Ruler
   - `Shift + ?`: Open Keyboard Shortcuts cheatsheet
   - `Escape`: Close active dialog or stop speech

---

## 📋 Key Portal Features

1. **Searchable & Filterable Scheme Explorer**:
   - Instant search across scheme name, ministry, target disability, eligibility, and benefits.
   - Multi-criteria filters: Category, Target Disability (Locomotor, Visual, Hearing, Intellectual, Autism/Cerebral Palsy, Multiple), and Level (Central vs State).
   - Detailed modal view with step-by-step application instructions, documents checklist, and official `.gov.in` portal links.
2. **Interactive Scheme Eligibility Calculator**:
   - 4-question wizard calculating matching schemes with personalized match scores and "Why You Qualify" explanations.
3. **Verified Helplines & Statutory Redressal Directory**:
   - One-touch tap-to-call for Kiran (1800-599-0019), Tele-MANAS (14416), ALIMCO (1800-180-5129), Emergency 112, CCPD, etc.
   - Directory of State Commissioners with jurisdiction, email, phone, and office addresses.
4. **RPwD Act 2016 Citizen Rights Guide**:
   - Plain-language explainer of Sections 3, 20, 34, 40-46, the 21 recognized disabilities, and how to file complaints with CCPD.
5. **My Saved Schemes ("Mera Pitara")**:
   - LocalStorage-backed bookmarking feature with print-friendly checklist generation.
6. **Accessible Data Export**:
   - Download all verified schemes as an accessible CSV file (`/api/export/csv`).

---

## 🚀 How to Run AccessMitra

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database (.env)
The portal supports both MySQL 8.0 and SQLite:
```ini
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=accessmitra

# Set to 'mysql' or 'sqlite'
DB_BACKEND=mysql
```
> **Note**: If MySQL server is not running or your password has not been entered yet, AccessMitra **automatically and gracefully activates the built-in SQLite engine** so you can immediately explore the entire portal!

### 3. Initialize / Seed Database
```bash
python init_db.py
```
To run the interactive MySQL setup utility:
```bash
python setup_mysql.py
```

### 4. Start the Application Server
```bash
python app.py
```
Open your browser and navigate to:
**[http://localhost:5000](http://localhost:5000)**

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/schemes` | `GET` | Filter schemes (`q`, `category`, `disability`, `level`, `sort`) |
| `/api/schemes/<id>` | `GET` | Get detailed scheme JSON by ID |
| `/api/check-eligibility` | `POST` | Calculate qualifying schemes for user profile |
| `/api/categories` | `GET` | List categories with scheme counts |
| `/api/helplines` | `GET` | List verified national helplines |
| `/api/grievance-authorities` | `GET` | List CCPD & State Commissioners |
| `/api/resources` | `GET` | List assistive software and guidelines |
| `/api/stats` | `GET` | Summary statistics and active database engine |
| `/api/feedback` | `POST` | Submit accessibility feedback / inquiry |
| `/api/export/csv` | `GET` | Download verified schemes as CSV |
