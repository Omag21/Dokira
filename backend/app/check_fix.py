#!/usr/bin/env python3
"""
Script de vérification et correction automatique pour Dokira
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Exécute une commande et affiche le résultat"""
    print(f"> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(f"STDERR: {result.stderr.strip()}")
    return result.returncode == 0

def main():
    print("=" * 60)
    print("VÉRIFICATION ET CORRECTION DOKIRA - Python 3.14")
    print("=" * 60)
    
    # 1. Vérifier la version Python
    print("\n1. VÉRIFICATION PYTHON")
    print("-" * 30)
    run_command("python --version")
    
    # 2. Vérifier l'environnement virtuel
    print("\n2. VÉRIFICATION ENVIRONNEMENT VIRTUEL")
    print("-" * 30)
    if os.path.exists("venv"):
        print("✓ venv existe")
        # Activer venv
        if sys.platform == "win32":
            activate_script = "venv\\Scripts\\activate"
        else:
            activate_script = "source venv/bin/activate"
        print(f"Script d'activation: {activate_script}")
    else:
        print("✗ venv n'existe pas")
        create = input("Créer venv? (o/n): ")
        if create.lower() == 'o':
            run_command("python -m venv venv")
    
    # 3. Vérifier les dépendances CRITIQUES
    print("\n3. VÉRIFICATION DÉPENDANCES CRITIQUES")
    print("-" * 30)
    
    # Liste des dépendances critiques
    critical_deps = [
        ("psycopg", "psycopg (version 3) pour PostgreSQL"),
        ("sqlalchemy", "SQLAlchemy pour ORM"),
        ("fastapi", "FastAPI pour l'API"),
        ("uvicorn", "Uvicorn pour le serveur"),
    ]
    
    all_ok = True
    for dep, desc in critical_deps:
        print(f"\n{desc}...")
        if dep == "psycopg":
            # Test spécial pour psycopg (version 3)
            test_code = '''
try:
    import psycopg
    print(f"  ✓ psycopg version: {psycopg.__version__}")
    print("  ℹ Utilisez 'postgresql+psycopg://' dans DATABASE_URL")
except ImportError:
    print("  ✗ psycopg non installé")
    print("  ℹ psycopg2-binary ne fonctionne pas avec Python 3.14")
    print("  ℹ Installez avec: pip install psycopg")
'''
        else:
            test_code = f'''
try:
    import {dep}
    version = getattr({dep}, '__version__', 'unknown')
    print(f"  ✓ {dep} version: {{version}}")
except ImportError:
    print(f"  ✗ {dep} non installé")
    all_ok = False
'''
        
        # Créer un fichier temporaire pour le test
        with open("_temp_check.py", "w", encoding="utf-8") as f:
            f.write(test_code)
        
        run_command("python _temp_check.py")
        
        # Nettoyer
        if os.path.exists("_temp_check.py"):
            os.remove("_temp_check.py")
    
    # 4. Installation automatique si nécessaire
    print("\n4. INSTALLATION AUTOMATIQUE")
    print("-" * 30)
    
    install_now = input("\nVoulez-vous installer les dépendances manquantes? (o/n): ")
    if install_now.lower() == 'o':
        print("\nInstallation en cours...")
        
        # Désinstaller psycopg2 s'il existe
        run_command("pip uninstall psycopg2 psycopg2-binary -y")
        
        # Installer les dépendances
        packages = [
            "psycopg>=3.1.0",
            "sqlalchemy>=2.0.0",
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "python-dotenv>=1.0.0",
            "passlib[bcrypt]>=1.7.4",
            "bcrypt>=4.1.2",
            "pydantic>=2.5.0",
            "jinja2>=3.1.2",
        ]
        
        for pkg in packages:
            print(f"\nInstallation de {pkg}...")
            run_command(f"pip install {pkg}")
        
        print("\n✓ Installation terminée")
    
    # 5. Vérifier database.py
    print("\n5. VÉRIFICATION DATABASE.PY")
    print("-" * 30)
    
    db_file = "app/database.py"
    if os.path.exists(db_file):
        print(f"✓ {db_file} existe")
        
        # Lire le fichier pour vérifier l'URL
        with open(db_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        if "postgresql+psycopg://" in content:
            print("  ✓ Utilise postgresql+psycopg:// (correct pour Python 3.14)")
        elif "postgresql://" in content:
            print("  ⚠ Utilise postgresql:// (problème avec Python 3.14)")
            print("  ℹ Changez en: postgresql+psycopg://")
            
            fix = input("  Corriger automatiquement? (o/n): ")
            if fix.lower() == 'o':
                # Corriger l'URL
                new_content = content.replace("postgresql://", "postgresql+psycopg://")
                with open(db_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print("  ✓ Fichier corrigé")
        else:
            print("  ? URL de base de données non identifiée")
    else:
        print(f"✗ {db_file} n'existe pas")
    
    # 6. Test final
    print("\n6. TEST FINAL")
    print("-" * 30)
    
    test_final = '''
print("Test d'importation des modules...")
try:
    # Test psycopg
    import psycopg
    print("✓ psycopg importé")
    
    # Test SQLAlchemy
    import sqlalchemy
    print(f"✓ SQLAlchemy {sqlalchemy.__version__} importé")
    
    # Test database.py
    import sys
    sys.path.append('.')
    try:
        from app.database import engine
        print("✓ app.database importé")
        
        # Tester l'URL
        if hasattr(engine, 'url'):
            url = str(engine.url)
            if 'psycopg' in url:
                print(f"✓ URL correcte: {url}")
            else:
                print(f"⚠ URL: {url}")
                print("  ℹ L'URL devrait contenir 'psycopg'")
        else:
            print("ℹ Engine sans URL (peut être un mock)")
            
    except ImportError as e:
        print(f"✗ Erreur import database: {e}")
        
except Exception as e:
    print(f"✗ Erreur générale: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open("_final_test.py", "w", encoding="utf-8") as f:
        f.write(test_final)
    
    run_command("python _final_test.py")
    
    # Nettoyer
    for temp_file in ["_temp_check.py", "_final_test.py"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    # 7. Instructions finales
    print("\n" + "=" * 60)
    print("INSTRUCTIONS FINALES")
    print("=" * 60)
    
    print("\nSI TOUT EST OK:")
    print("  uvicorn app.main:app --reload --port 8000")
    
    print("\nSI VOUS AVEZ DES ERREURS:")
    print("  1. Vérifiez que PostgreSQL est installé et fonctionne")
    print("  2. Créez la base: psql -U postgres -c 'CREATE DATABASE dokira;'")
    print("  3. Vérifiez .env: DB_HOST=localhost, DB_USER=postgres, etc.")
    
    print("\nPOUR CORRIGER DATABASE.PY MANUELLEMENT:")
    print('  Changez: f"postgresql://{user}:{pass}@{host}:{port}/{db}"')
    print('  En:      f"postgresql+psycopg://{user}:{pass}@{host}:{port}/{db}"')
    
    print("\nPOUR UTILISER SQLITE TEMPORAIREMENT:")
    print('  Dans database.py, remplacez DATABASE_URL par:')
    print('  DATABASE_URL = "sqlite:///./dokira.db"')
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()