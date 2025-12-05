#!/bin/bash

# Script pour pousser vers GitHub et GitLab

echo "🔄 Ajout des fichiers modifiés..."
git add .

echo "💬 Message du commit:"
read -p "Entrez votre message: " message

echo "📝 Création du commit..."
git commit -m "$message"

echo "📤 Push vers GitHub..."
git push origin main

echo "📤 Push vers GitLab..."
git push gitlab main

echo "✅ Terminé! Code poussé vers GitHub et GitLab"