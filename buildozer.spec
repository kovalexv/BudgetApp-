[app]

# Nom de l'application
title = Gestion de Budget
package.name = budgetapp
package.domain = org.kov

# Fichiers à inclure
source.dir = .
source.include_exts = py,png,jpg,kv,json

# Dépendances Python
requirements = python3,kivy==2.3.1,matplotlib

# Orientation de l'application
orientation = portrait

# Version Android et architecture
android.api = 33
android.arch = arm64-v8a

# Version de l'application
version = 1.0

# Icône de l'application (optionnel)
# icon.filename = icon.png

# Permissions Android (optionnel)
# android.permissions = INTERNET

[buildozer]

# Dossier pour la compilation
build_dir = .buildozer

# Nettoyage après compilation pour gagner de l'espace
clean_build = True

# Nombre de processus pour accélérer la compilation (optionnel)
# jobs = 4
