import os
import csv
import io
import logging
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify, Response, send_file,
    session, redirect, url_for, flash, g
)
from sqlalchemy import or_, and_, desc, asc
from config import Config
from database import (
    get_db, init_db, active_db_type,
    Scheme, Helpline, GrievanceAuthority, AccessibilityResource, FeedbackReport,
    User, UserBookmark
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AccessMitra.App")

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database is initialized on app startup
try:
    init_db(seed=True)
except Exception as e:
    logger.error("Database startup init warning: %s", e)

@app.before_request
def load_logged_in_user():
    """Load current authenticated user into flask.g"""
    user_id = session.get('user_id')
    if user_id is None:
        g.current_user = None
    else:
        db = get_db()
        try:
            g.current_user = db.query(User).filter(User.id == user_id).first()
        except Exception as ex:
            logger.error("Error loading user from session: %s", ex)
            g.current_user = None
        finally:
            db.close()

def login_required(view):
    """Decorator to protect routes requiring authentication"""
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.current_user is None:
            flash("Please sign in or create an account to view your profile and saved schemes.", "info")
            return redirect(url_for('login_page', next=request.url))
        return view(**kwargs)
    return wrapped_view

@app.context_processor
def inject_global_data():
    """Inject database mode, current user, and year across all templates"""
    from database import active_db_type
    return {
        "active_db_type": active_db_type,
        "current_year": 2026,
        "portal_name": "AccessMitra (एक्सेस मित्र)",
        "current_user": g.get('current_user', None)
    }

# ==========================================
# PAGE ROUTES
# ==========================================

@app.route('/')
def index():
    """Clean AccessMitra landing page."""
    db = get_db()
    try:
        return render_template(
            'landing.html',
            total_schemes=db.query(Scheme).count(),
            total_helplines=db.query(Helpline).count(),
            total_resources=db.query(AccessibilityResource).count()
        )
    finally:
        db.close()

@app.route('/schemes')
def schemes_page():
    """Main Portal Scheme Explorer."""
    db = get_db()
    try:
        featured_schemes = db.query(Scheme).filter(Scheme.is_featured == True).all()
        categories = db.query(Scheme.category).distinct().all()
        categories = sorted([c[0] for c in categories])
        helplines = db.query(Helpline).order_by(Helpline.priority_order.asc()).limit(4).all()
        resources = db.query(AccessibilityResource).all()

        total_schemes = db.query(Scheme).count()
        total_helplines = db.query(Helpline).count()

        return render_template(
            'index.html',
            featured_schemes=featured_schemes,
            categories=categories,
            helplines=helplines,
            resources=resources,
            total_schemes=total_schemes,
            total_helplines=total_helplines
        )
    finally:
        db.close()

@app.route('/dashboard')
@login_required
def dashboard_page():
    """Authenticated AccessMitra dashboard/home page."""
    db = get_db()
    try:
        saved_bookmarks = db.query(UserBookmark).filter(
            UserBookmark.user_id == g.current_user.id
        ).order_by(UserBookmark.id.desc()).all()
        saved_schemes = [bookmark.scheme for bookmark in saved_bookmarks if bookmark.scheme]
        return render_template(
            'profile.html',
            user=g.current_user,
            saved_schemes=saved_schemes
        )
    finally:
        db.close()

@app.route('/scheme/<slug_or_id>')
def scheme_detail(slug_or_id):
    """Detailed Individual Scheme Page"""
    db = get_db()
    try:
        if slug_or_id.isdigit():
            scheme = db.query(Scheme).filter(Scheme.id == int(slug_or_id)).first()
        else:
            scheme = db.query(Scheme).filter(Scheme.slug == slug_or_id).first()

        if not scheme:
            return render_template('404.html', message="The requested government scheme could not be found."), 404

        # Related schemes in the same category
        related_schemes = db.query(Scheme).filter(
            Scheme.category == scheme.category,
            Scheme.id != scheme.id
        ).limit(3).all()

        return render_template('scheme_detail.html', scheme=scheme, related_schemes=related_schemes)
    finally:
        db.close()

@app.route('/helplines')
def helplines_page():
    """Dedicated Emergency & Verified Helplines Directory"""
    db = get_db()
    try:
        helplines = db.query(Helpline).order_by(Helpline.priority_order.asc()).all()
        authorities = db.query(GrievanceAuthority).all()
        return render_template('helplines.html', helplines=helplines, authorities=authorities)
    finally:
        db.close()

@app.route('/wizard')
def wizard_page():
    """Interactive Scheme Eligibility Calculator & Wizard"""
    return render_template('wizard.html')

@app.route('/rights')
def rights_page():
    """RPwD Act 2016, Citizen Legal Rights, and Grievance Redressal"""
    db = get_db()
    try:
        authorities = db.query(GrievanceAuthority).all()
        return render_template('rights.html', authorities=authorities)
    finally:
        db.close()

@app.route('/bookmarks')
def bookmarks_page():
    """Saved Schemes ('Mera Pitara') User Page"""
    return render_template('bookmarks.html')

@app.route('/register', methods=['GET', 'POST'])
@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    """Sign up for an AccessMitra personal welfare account"""
    if g.current_user:
        return redirect(url_for('dashboard_page'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        phone = request.form.get('phone', '').strip()

        error = None
        if not name:
            error = "Full Name is required."
        elif not email or '@' not in email:
            error = "Please provide a valid email address."
        elif not password or len(password) < 6:
            error = "Password must be at least 6 characters long."

        if error is None:
            db = get_db()
            try:
                existing_user = db.query(User).filter(User.email == email).first()
                if existing_user:
                    error = f"An account with email '{email}' already exists. Please login instead."
                else:
                    new_user = User(
                        name=name,
                        email=email,
                        phone=phone
                    )
                    new_user.set_password(password)
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)

                    session.clear()
                    session['user_id'] = new_user.id
                    flash(f"Welcome to AccessMitra, {new_user.name}! Your account has been created.", "success")
                    return redirect(url_for('dashboard_page'))
            except Exception as e:
                db.rollback()
                logger.error("Signup database error: %s", e)
                error = "An error occurred while creating your account. Please try again."
            finally:
                db.close()

        if error:
            flash(error, "danger")

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Log in to existing AccessMitra account"""
    if g.current_user:
        return redirect(url_for('dashboard_page'))

    next_url = request.args.get('next') or request.form.get('next') or url_for('dashboard_page')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash("Please enter both your email and password.", "danger")
        else:
            db = get_db()
            try:
                user = db.query(User).filter(User.email == email).first()
                if user and user.check_password(password):
                    session.clear()
                    session['user_id'] = user.id
                    flash(f"Welcome back, {user.name}!", "success")
                    return redirect(next_url)
                else:
                    flash("Invalid email or password. Please verify your credentials and try again.", "danger")
            except Exception as e:
                logger.error("Login database error: %s", e)
                flash("Login service temporarily unavailable. Please retry.", "danger")
            finally:
                db.close()

    return render_template('login.html', next_url=next_url)

@app.route('/logout')
def logout():
    """Log out of the current user session"""
    session.clear()
    flash("You have been securely logged out. Thank you for visiting AccessMitra.", "info")
    return redirect(url_for('login_page'))

@app.route('/profile')
@login_required
def profile_page():
    """User Profile with Saved Schemes and Accessibility Preferences"""
    db = get_db()
    try:
        saved_bookmarks = db.query(UserBookmark).filter(UserBookmark.user_id == g.current_user.id).order_by(UserBookmark.id.desc()).all()
        saved_schemes = [b.scheme for b in saved_bookmarks if b.scheme]
        return render_template(
            'profile.html',
            user=g.current_user,
            saved_schemes=saved_schemes
        )
    finally:
        db.close()

# ==========================================
# API ROUTES (RESTful)
# ==========================================

@app.route('/api/schemes', methods=['GET'])
def api_schemes():
    """
    Search and filter government schemes.
    Query parameters:
      - q: search keyword
      - category: filter by category
      - disability: filter by target disability
      - level: filter by level ('Central', 'State', 'Both')
      - max_income: filter by income ceiling
      - min_disability_pct: filter by minimum percentage required
      - sort: 'featured', 'name_asc', 'name_desc', 'newest'
    """
    db = get_db()
    try:
        query = db.query(Scheme)

        q = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        disability = request.args.get('disability', '').strip()
        level = request.args.get('level', '').strip()
        max_income = request.args.get('max_income', type=int)
        min_disability_pct = request.args.get('min_disability_pct', type=int)
        sort_by = request.args.get('sort', 'featured')

        # Text search across multiple fields
        if q:
            search_filter = or_(
                Scheme.name.ilike(f'%{q}%'),
                Scheme.brief_description.ilike(f'%{q}%'),
                Scheme.eligibility.ilike(f'%{q}%'),
                Scheme.benefits.ilike(f'%{q}%'),
                Scheme.ministry.ilike(f'%{q}%'),
                Scheme.tags.ilike(f'%{q}%')
            )
            query = query.filter(search_filter)

        # Category filter
        if category and category.lower() != 'all':
            query = query.filter(Scheme.category == category)

        # Disability filter
        if disability and disability.lower() != 'all':
            disability_filter = or_(
                Scheme.target_disability == 'All Disabilities',
                Scheme.target_disability.ilike(f'%{disability}%'),
                Scheme.tags.ilike(f'%{disability}%')
            )
            query = query.filter(disability_filter)

        # Level filter
        if level and level.lower() != 'all':
            if level.lower() == 'central':
                query = query.filter(or_(Scheme.level == 'Central', Scheme.level == 'Both'))
            elif level.lower() == 'state':
                query = query.filter(or_(Scheme.level == 'State', Scheme.level == 'Both'))

        # Income ceiling filter (schemes where user income satisfies scheme criteria)
        if max_income is not None and max_income > 0:
            query = query.filter(or_(Scheme.max_annual_income == 0, Scheme.max_annual_income >= max_income))

        # Min disability percentage
        if min_disability_pct is not None and min_disability_pct > 0:
            query = query.filter(Scheme.min_disability_pct <= min_disability_pct)

        # Sorting
        if sort_by == 'name_asc':
            query = query.order_by(Scheme.name.asc())
        elif sort_by == 'name_desc':
            query = query.order_by(Scheme.name.desc())
        elif sort_by == 'newest':
            query = query.order_by(Scheme.id.desc())
        else: # 'featured' default
            query = query.order_by(desc(Scheme.is_featured), Scheme.name.asc())

        results = query.all()
        return jsonify({
            "status": "success",
            "count": len(results),
            "data": [s.to_dict() for s in results]
        })
    except Exception as e:
        logger.error("Error in api_schemes: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

@app.route('/api/schemes/<int:scheme_id>', methods=['GET'])
def api_scheme_by_id(scheme_id):
    """Retrieve full details of a single scheme by ID"""
    db = get_db()
    try:
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
        if not scheme:
            return jsonify({"status": "error", "message": "Scheme not found"}), 404
        return jsonify({"status": "success", "data": scheme.to_dict()})
    finally:
        db.close()

@app.route('/api/check-eligibility', methods=['POST'])
def api_check_eligibility():
    """
    Intelligent Eligibility Wizard Engine.
    Analyzes user profile (age, disability type, percentage, annual income, need)
    and returns matched schemes with specific qualification reasons.
    """
    db = get_db()
    try:
        data = request.get_json(silent=True) or {}
        age = int(data.get('age', 25))
        disability_type = data.get('disability_type', 'Locomotor Disability')
        disability_pct = int(data.get('disability_pct', 40))
        annual_income = int(data.get('annual_income', 180000))
        primary_need = data.get('primary_need', 'All')

        all_schemes = db.query(Scheme).all()
        matched = []

        for s in all_schemes:
            reasons = []
            score = 0
            eligible = True

            # 1. Disability match check
            if s.target_disability == 'All Disabilities':
                score += 30
                reasons.append("Covers all certified disabilities.")
            elif disability_type.lower() in s.target_disability.lower() or disability_type.lower() in s.tags.lower():
                score += 40
                reasons.append(f"Specifically designed for {s.target_disability}.")
            else:
                eligible = False

            # 2. Percentage check
            if disability_pct < s.min_disability_pct:
                eligible = False
            else:
                score += 20
                reasons.append(f"Your disability ({disability_pct}%) meets or exceeds the minimum required ({s.min_disability_pct}%).")

            # 3. Age check
            if age < s.min_age or age > s.max_age:
                eligible = False
            else:
                score += 15
                if s.min_age > 0 or s.max_age < 100:
                    reasons.append(f"Your age ({age} yrs) falls within the required range ({s.min_age} - {s.max_age} yrs).")

            # 4. Income check
            if s.max_annual_income > 0:
                if annual_income > s.max_annual_income:
                    eligible = False
                else:
                    score += 25
                    reasons.append(f"Your family income (₹{annual_income:,}) is within the threshold limit (₹{s.max_annual_income:,}).")
            else:
                score += 15
                reasons.append("No upper family income ceiling; open to all income categories.")

            # 5. Primary Need boost
            if primary_need != 'All' and primary_need.lower() in s.category.lower():
                score += 30
                reasons.append(f"Directly satisfies your primary requirement: {s.category}.")

            if eligible:
                scheme_dict = s.to_dict()
                scheme_dict['match_score'] = score
                scheme_dict['eligibility_reasons'] = reasons
                matched.append(scheme_dict)

        # Sort by match score descending
        matched.sort(key=lambda x: x['match_score'], reverse=True)

        return jsonify({
            "status": "success",
            "matched_count": len(matched),
            "data": matched
        })
    except Exception as e:
        logger.error("Error in check_eligibility: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

@app.route('/api/categories', methods=['GET'])
def api_categories():
    """Return categories and scheme counts"""
    db = get_db()
    try:
        schemes = db.query(Scheme.category).all()
        counts = {}
        for (cat,) in schemes:
            counts[cat] = counts.get(cat, 0) + 1
        return jsonify({"status": "success", "data": counts})
    finally:
        db.close()

@app.route('/api/helplines', methods=['GET'])
def api_helplines():
    """Return list of verified helplines"""
    db = get_db()
    try:
        helplines = db.query(Helpline).order_by(Helpline.priority_order.asc()).all()
        return jsonify({"status": "success", "data": [h.to_dict() for h in helplines]})
    finally:
        db.close()

@app.route('/api/grievance-authorities', methods=['GET'])
def api_grievance():
    """Return list of CCPD and state commissioners"""
    db = get_db()
    try:
        authorities = db.query(GrievanceAuthority).all()
        return jsonify({"status": "success", "data": [a.to_dict() for a in authorities]})
    finally:
        db.close()

@app.route('/api/resources', methods=['GET'])
def api_resources():
    """Return digital accessibility resources and screen readers"""
    db = get_db()
    try:
        res = db.query(AccessibilityResource).all()
        return jsonify({"status": "success", "data": [r.to_dict() for r in res]})
    finally:
        db.close()

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Summary portal statistics"""
    db = get_db()
    try:
        total_schemes = db.query(Scheme).count()
        total_helplines = db.query(Helpline).count()
        total_authorities = db.query(GrievanceAuthority).count()
        total_resources = db.query(AccessibilityResource).count()
        central_count = db.query(Scheme).filter(or_(Scheme.level == 'Central', Scheme.level == 'Both')).count()

        from database import active_db_type
        return jsonify({
            "status": "success",
            "data": {
                "total_schemes": total_schemes,
                "central_schemes": central_count,
                "total_helplines": total_helplines,
                "grievance_authorities": total_authorities,
                "digital_resources": total_resources,
                "database_mode": active_db_type
            }
        })
    finally:
        db.close()

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """Accept accessibility feedback or scheme inquiries"""
    db = get_db()
    try:
        data = request.get_json() or {}
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        if not subject or not message:
            return jsonify({"status": "error", "message": "Subject and message are required."}), 400

        report = FeedbackReport(
            user_name=data.get('user_name', 'Anonymous').strip() or 'Anonymous',
            user_email=data.get('user_email', '').strip(),
            feedback_type=data.get('feedback_type', 'General Feedback'),
            subject=subject,
            message=message,
            accessibility_mode=data.get('accessibility_mode', 'Standard')
        )
        db.add(report)
        db.commit()

        return jsonify({
            "status": "success",
            "message": "Thank you! Your feedback has been recorded to make AccessMitra even more accessible."
        })
    except Exception as e:
        db.rollback()
        logger.error("Error saving feedback: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

@app.route('/api/user/preferences', methods=['POST'])
@login_required
def api_update_preferences():
    """Persist user accessibility preferences (contrast mode, font scaling, dyslexia font, ruler)"""
    db = get_db()
    try:
        data = request.get_json(silent=True) or {}
        user = db.query(User).filter(User.id == g.current_user.id).first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        if 'contrast_mode' in data:
            user.contrast_mode = data['contrast_mode']
        if 'font_size' in data:
            user.font_size = data['font_size']
        if 'dyslexia_font' in data:
            user.dyslexia_font = bool(data['dyslexia_font'])
        if 'reading_ruler' in data:
            user.reading_ruler = bool(data['reading_ruler'])
        if 'disability_type' in data:
            user.disability_type = data['disability_type']

        db.commit()
        return jsonify({
            "status": "success",
            "message": "Accessibility preferences saved successfully.",
            "preferences": user.to_dict()
        })
    except Exception as e:
        db.rollback()
        logger.error("Error updating preferences: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

@app.route('/api/user/profile', methods=['POST'])
@login_required
def api_update_profile():
    """Update user personal details (name, phone, password)"""
    db = get_db()
    try:
        data = request.get_json(silent=True) or request.form
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        new_password = data.get('new_password', '').strip()

        user = db.query(User).filter(User.id == g.current_user.id).first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        if name:
            user.name = name
        user.phone = phone

        if new_password:
            if len(new_password) < 6:
                return jsonify({"status": "error", "message": "New password must be at least 6 characters."}), 400
            user.set_password(new_password)

        db.commit()
        return jsonify({
            "status": "success",
            "message": "Profile details updated successfully.",
            "user": user.to_dict()
        })
    except Exception as e:
        db.rollback()
        logger.error("Error updating profile: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

@app.route('/api/bookmarks/toggle', methods=['POST'])
def api_bookmark_toggle():
    """Toggle bookmark for a scheme. Saved in database if authenticated."""
    data = request.get_json(silent=True) or {}
    scheme_id = data.get('scheme_id')
    if not scheme_id:
        return jsonify({"status": "error", "message": "Scheme ID required"}), 400

    if not g.current_user:
        return jsonify({
            "status": "guest",
            "message": "Saved locally in browser. Log in to sync across devices."
        })

    db = get_db()
    try:
        sid = int(scheme_id)
        existing = db.query(UserBookmark).filter(
            UserBookmark.user_id == g.current_user.id,
            UserBookmark.scheme_id == sid
        ).first()

        if existing:
            db.delete(existing)
            db.commit()
            saved = False
        else:
            new_bm = UserBookmark(user_id=g.current_user.id, scheme_id=sid)
            db.add(new_bm)
            db.commit()
            saved = True

        count = db.query(UserBookmark).filter(UserBookmark.user_id == g.current_user.id).count()
        return jsonify({
            "status": "success",
            "saved": saved,
            "count": count,
            "message": "Saved to your account" if saved else "Removed from your account"
        })
    except Exception as e:
        db.rollback()
        logger.error("Error toggling bookmark: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

@app.route('/api/bookmarks/sync', methods=['POST'])
def api_bookmark_sync():
    """Synchronize localStorage bookmarks with the authenticated user's database portfolio"""
    if not g.current_user:
        return jsonify({"status": "guest", "saved_ids": []})

    data = request.get_json(silent=True) or {}
    client_ids = data.get('scheme_ids', [])

    db = get_db()
    try:
        for sid in client_ids:
            if isinstance(sid, int) or (isinstance(sid, str) and sid.isdigit()):
                sid_int = int(sid)
                exists = db.query(UserBookmark).filter(
                    UserBookmark.user_id == g.current_user.id,
                    UserBookmark.scheme_id == sid_int
                ).first()
                if not exists:
                    # Verify scheme exists
                    scheme_exists = db.query(Scheme.id).filter(Scheme.id == sid_int).first()
                    if scheme_exists:
                        db.add(UserBookmark(user_id=g.current_user.id, scheme_id=sid_int))
        db.commit()

        all_bms = db.query(UserBookmark.scheme_id).filter(UserBookmark.user_id == g.current_user.id).all()
        all_ids = [b[0] for b in all_bms]
        return jsonify({"status": "success", "saved_ids": all_ids, "count": len(all_ids)})
    except Exception as e:
        db.rollback()
        logger.error("Error syncing bookmarks: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

@app.route('/api/user/saved-schemes', methods=['GET'])
def api_user_saved_schemes():
    """Retrieve list of schemes bookmarked by the currently logged-in user"""
    if not g.current_user:
        return jsonify({"status": "guest", "data": []})

    db = get_db()
    try:
        bms = db.query(UserBookmark).filter(UserBookmark.user_id == g.current_user.id).order_by(UserBookmark.id.desc()).all()
        schemes = [b.scheme.to_dict() for b in bms if b.scheme]
        return jsonify({"status": "success", "data": schemes, "count": len(schemes)})
    finally:
        db.close()

@app.route('/api/export/csv', methods=['GET'])
def api_export_csv():
    """Export all verified schemes as accessible CSV data"""
    db = get_db()
    try:
        schemes = db.query(Scheme).order_by(Scheme.name.asc()).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Scheme Name", "Ministry", "Category", "Target Disability",
            "Min Disability %", "Max Annual Income (INR)", "Eligibility Criteria",
            "Key Benefits", "Application Process", "Helpline", "Official Portal Link"
        ])

        for s in schemes:
            writer.writerow([
                s.id, s.name, s.ministry, s.category, s.target_disability,
                f"{s.min_disability_pct}%",
                f"Rs. {s.max_annual_income:,}" if s.max_annual_income > 0 else "No Limit",
                s.eligibility.replace('\n', ' '),
                s.benefits.replace('\n', ' '),
                s.application_process.replace('\n', ' '),
                s.helpline_number,
                s.official_portal_url
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=accessmitra_schemes.csv"}
        )
    finally:
        db.close()

@app.route('/api/system-status', methods=['GET'])
def api_system_status():
    """Return database health check and configuration status"""
    from database import active_db_type
    db = get_db()
    try:
        scheme_count = db.query(Scheme).count()
        return jsonify({
            "status": "healthy",
            "database_engine": active_db_type,
            "mysql_host": Config.MYSQL_HOST,
            "mysql_database": Config.MYSQL_DB,
            "total_records": scheme_count
        })
    finally:
        db.close()

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="The page or scheme you are looking for does not exist."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html', message="An unexpected error occurred. Please try again or report to our accessibility cell."), 500

if __name__ == '__main__':
    port = Config.PORT
    debug = Config.FLASK_DEBUG
    print(f"Starting AccessMitra on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
