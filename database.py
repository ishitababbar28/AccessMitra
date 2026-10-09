import os
import logging
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean, DateTime, func, or_, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AccessMitra.Database")

Base = declarative_base()

class Scheme(Base):
    __tablename__ = 'schemes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    ministry = Column(String(255), nullable=False)
    implementing_agency = Column(String(255), default='')
    category = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False, default='Central')
    state_name = Column(String(100), default='All India')
    target_disability = Column(String(255), nullable=False)
    min_disability_pct = Column(Integer, default=40)
    min_age = Column(Integer, default=0)
    max_age = Column(Integer, default=120)
    max_annual_income = Column(Integer, default=0) # 0 means no limit
    brief_description = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=False)
    benefits = Column(Text, nullable=False)
    application_process = Column(Text, nullable=False)
    documents_required = Column(Text, nullable=False)
    contact_details = Column(Text, nullable=False)
    helpline_number = Column(String(100), default='')
    official_portal_url = Column(String(500), nullable=False)
    application_url = Column(String(500), nullable=False)
    tags = Column(String(255), default='')
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "ministry": self.ministry,
            "implementing_agency": self.implementing_agency,
            "category": self.category,
            "level": self.level,
            "state_name": self.state_name,
            "target_disability": self.target_disability,
            "min_disability_pct": self.min_disability_pct,
            "min_age": self.min_age,
            "max_age": self.max_age,
            "max_annual_income": self.max_annual_income,
            "brief_description": self.brief_description,
            "eligibility": self.eligibility,
            "benefits": self.benefits,
            "application_process": self.application_process,
            "documents_required": self.documents_required,
            "contact_details": self.contact_details,
            "helpline_number": self.helpline_number,
            "official_portal_url": self.official_portal_url,
            "application_url": self.application_url,
            "tags": self.tags,
            "is_featured": bool(self.is_featured),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Helpline(Base):
    __tablename__ = 'helplines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    phone_number = Column(String(100), nullable=False)
    toll_free = Column(Boolean, default=True)
    operational_hours = Column(String(100), nullable=False)
    languages = Column(String(255), nullable=False)
    services = Column(Text, nullable=False)
    official_url = Column(String(500), nullable=False)
    category = Column(String(100), default='Emergency & Crisis')
    priority_order = Column(Integer, default=10)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "phone_number": self.phone_number,
            "toll_free": bool(self.toll_free),
            "operational_hours": self.operational_hours,
            "languages": self.languages,
            "services": self.services,
            "official_url": self.official_url,
            "category": self.category,
            "priority_order": self.priority_order
        }

class GrievanceAuthority(Base):
    __tablename__ = 'grievance_authorities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    jurisdiction = Column(String(255), nullable=False)
    official_designation = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(100), nullable=False)
    portal_url = Column(String(500), nullable=False)
    address = Column(Text, nullable=False)
    act_reference = Column(String(255), default='RPwD Act 2016')
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "jurisdiction": self.jurisdiction,
            "official_designation": self.official_designation,
            "email": self.email,
            "phone": self.phone,
            "portal_url": self.portal_url,
            "address": self.address,
            "act_reference": self.act_reference
        }

class AccessibilityResource(Base):
    __tablename__ = 'accessibility_resources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    cost = Column(String(50), default='Free / Open Source')
    platform = Column(String(100), nullable=False)
    official_link = Column(String(500), nullable=False)
    developer_organization = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "description": self.description,
            "cost": self.cost,
            "platform": self.platform,
            "official_link": self.official_link,
            "developer_organization": self.developer_organization
        }

class FeedbackReport(Base):
    __tablename__ = 'feedback_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(150), default='Anonymous')
    user_email = Column(String(150), default='')
    feedback_type = Column(String(100), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    accessibility_mode = Column(String(100), default='Standard')
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "feedback_type": self.feedback_type,
            "subject": self.subject,
            "message": self.message,
            "accessibility_mode": self.accessibility_mode,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True, default='')
    contrast_mode = Column(String(50), default='standard')  # 'standard', 'dark', 'yellow'
    font_size = Column(String(50), default='base')          # 'base', 'lg', 'xl'
    dyslexia_font = Column(Boolean, default=False)
    reading_ruler = Column(Boolean, default=False)
    disability_type = Column(String(100), default='')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    bookmarks = relationship('UserBookmark', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone or '',
            "contrast_mode": self.contrast_mode or 'standard',
            "font_size": self.font_size or 'base',
            "dyslexia_font": bool(self.dyslexia_font),
            "reading_ruler": bool(self.reading_ruler),
            "disability_type": self.disability_type or '',
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class UserBookmark(Base):
    __tablename__ = 'user_bookmarks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey('schemes.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship('User', back_populates='bookmarks')
    scheme = relationship('Scheme')

    __table_args__ = (
        UniqueConstraint('user_id', 'scheme_id', name='uq_user_scheme_bookmark'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "scheme_id": self.scheme_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scheme": self.scheme.to_dict() if self.scheme else None
        }

# Engine and Session Management
engine = None
SessionLocal = None
active_db_type = "Uninitialized"

def get_engine():
    global engine, active_db_type

    if engine is not None:
        return engine

    if Config.DB_BACKEND == 'mysql':
        try:
            logger.info("Attempting connection to MySQL at %s:%s...", Config.MYSQL_HOST, Config.MYSQL_PORT)
            mysql_uri = Config.get_mysql_uri()
            # Test engine with a short timeout
            test_engine = create_engine(mysql_uri, pool_pre_ping=True, connect_args={"connect_timeout": 3})
            with test_engine.connect() as conn:
                logger.info("Successfully connected to MySQL database: %s", Config.MYSQL_DB)
            engine = test_engine
            active_db_type = "MySQL 8.0 (Active)"
            return engine
        except Exception as e:
            logger.warning("Could not connect to MySQL (%s). Falling back gracefully to SQLite database...", e)
            logger.info("Tip: To use MySQL, ensure MySQL server is running and configure credentials in .env")

    # Fallback to SQLite
    sqlite_uri = Config.get_sqlite_uri()
    logger.info("Connecting to SQLite database: %s", sqlite_uri)
    engine = create_engine(sqlite_uri, echo=False, connect_args={"check_same_thread": False})
    active_db_type = "SQLite (Local Fallback)"
    return engine

def get_db():
    global SessionLocal
    if SessionLocal is None:
        eng = get_engine()
        SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=eng))
    return SessionLocal()

def init_db(seed=True):
    from seed_data import SCHEMES_DATA, HELPLINES_DATA, GRIEVANCE_DATA, RESOURCES_DATA
    eng = get_engine()
    Base.metadata.create_all(bind=eng)
    logger.info("Database tables created successfully under %s.", active_db_type)

    if seed:
        db = get_db()
        try:
            # Check if schemes already exist
            scheme_count = db.query(Scheme).count()
            if scheme_count == 0:
                logger.info("Seeding verified Indian schemes...")
                for item in SCHEMES_DATA:
                    db.add(Scheme(**item))

                for item in HELPLINES_DATA:
                    db.add(Helpline(**item))

                for item in GRIEVANCE_DATA:
                    db.add(GrievanceAuthority(**item))

                for item in RESOURCES_DATA:
                    db.add(AccessibilityResource(**item))

                db.commit()
                logger.info("Seeded %d schemes, %d helplines, %d authorities, %d resources.",
                            len(SCHEMES_DATA), len(HELPLINES_DATA), len(GRIEVANCE_DATA), len(RESOURCES_DATA))
            else:
                logger.info("Database already contains %d schemes. Skipping re-seed.", scheme_count)
        except Exception as ex:
            db.rollback()
            logger.error("Error during seeding: %s", ex)
            raise
        finally:
            db.close()
