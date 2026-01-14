"""
Module de configuration de la base de données pour l'application Dokira.
COMPATIBLE Python 3.14 - Utilise psycopg (version 3)
"""

import os
import sys
import logging
from dotenv import load_dotenv
from urllib.parse import quote_plus

# ============================================
# FORCER SQLAlchemy à utiliser psycopg au lieu de psycopg2
# ============================================

# IMPORTANT: Ceci doit être au TOUT DÉBUT du fichier
# Désactive le dialecte psycopg2 pour forcer l'utilisation de psycopg
try:
    import sqlalchemy.dialects.postgresql
    # Force SQLAlchemy à ignorer psycopg2
    sqlalchemy.dialects.postgresql.psycopg2 = None
    print("✓ psycopg2 dialect disabled, forcing psycopg usage")
except:
    pass

# ============================================
# Configuration du logging
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# Chargement des variables d'environnement
# ============================================
load_dotenv()

# ============================================
# Configuration de la base de données
# ============================================
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "dokira")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")

logger.info(f"Configuration DB: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ============================================
# IMPORTANT: URL de connexion AVEC psycopg
# ============================================
password_encoded = quote_plus(DB_PASSWORD)

# UTILISEZ postgresql+psycopg:// PAS postgresql://
DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logger.info(f"URL de connexion DB: postgresql+psycopg://{DB_USER}:*****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ============================================
# Import SQLAlchemy APRÈS avoir défini l'URL
# ============================================
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker, declarative_base
    from sqlalchemy.exc import SQLAlchemyError
    
    # ============================================
    # Création du moteur avec configuration simple
    # ============================================
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
            future=True
        )
        logger.info("✓ Moteur SQLAlchemy créé avec psycopg")
        
    except Exception as e:
        logger.error(f"✗ Erreur création moteur avec psycopg: {e}")
        logger.info("⚠ Tentative avec SQLite...")
        
        # Fallback à SQLite
        DATABASE_URL = "sqlite:///./dokira.db"
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        logger.info("✓ Moteur SQLAlchemy créé avec SQLite")
    
    # ============================================
    # Test de connexion
    # ============================================
    def test_connection():
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✓ Connexion à la base de données réussie")
                return True
        except Exception as e:
            logger.warning(f"⚠ Connexion échouée: {e}")
            return False
    
    # ============================================
    # Session SQLAlchemy
    # ============================================
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )
    
    Base = declarative_base()
    
    # ============================================
    # Dépendance FastAPI
    # ============================================
    def get_db():
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur DB: {e}")
            raise
        finally:
            db.close()
    
    # ============================================
    # Initialisation des tables
    # ============================================
    def init_db():
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✓ Tables initialisées")
        except Exception as e:
            logger.error(f"✗ Erreur initialisation tables: {e}")
    
    # ============================================
    # Test au démarrage
    # ============================================
    if __name__ == "__main__":
        test_connection()
    else:
        # Test asynchrone en arrière-plan
        import threading
        def background_test():
            test_connection()
        thread = threading.Thread(target=background_test, daemon=True)
        thread.start()
    
    logger.info("✓ Module database initialisé avec succès")
    
except ImportError as e:
    # ============================================
    # FALLBACK COMPLET si SQLAlchemy n'est pas disponible
    # ============================================
    logger.error(f"✗ SQLAlchemy non disponible: {e}")
    logger.warning("⚠ Création d'objets mock pour permettre le démarrage")
    
    # Créer des objets mock
    class MockEngine:
        def connect(self):
            return self
        def execute(self, *args, **kwargs):
            class MockResult:
                def scalar(self):
                    return "Mock PostgreSQL"
                def fetchone(self):
                    return [1]
                def fetchall(self):
                    return []
            return MockResult()
        def close(self):
            pass
    
    class MockSession:
        def commit(self):
            pass
        def rollback(self):
            pass
        def close(self):
            pass
        def add(self, item):
            pass
        def query(self, *args):
            return self
        def filter(self, *args):
            return self
        def first(self):
            return None
        def all(self):
            return []
    
    class MockBase:
        metadata = type('obj', (object,), {
            'create_all': lambda *args, **kwargs: None
        })()
    
    engine = MockEngine()
    SessionLocal = lambda: MockSession()
    Base = MockBase()
    
    def get_db():
        db = MockSession()
        try:
            yield db
        finally:
            db.close()
    
    def init_db():
        logger.info("Mock: init_db appelé (aucune action)")
    
    logger.warning("⚠ Utilisation d'objets mock - base de données non fonctionnelle")