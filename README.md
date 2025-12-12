# Challenge Triple A - Dashboard de Monitoring

## Description
Ce projet est un tableau de bord de monitoring système permettant d’afficher diverses informations concernant :
- l’état du CPU,
- la mémoire vive,
- les processus les plus gourmands,
- les informations système et réseau,
- l’analyse de fichiers dans un répertoire défini.

Le tableau de bord peut être affiché dynamiquement via Flask ou généré sous forme de fichier HTML statique (`index.html`) pour la soumission.

## Prérequis
- Python 3.8+
- pip
- Modules nécessaires :
  - psutil
  - flask

## Installation
Clonez le dépôt puis installez les dépendances :

```bash
pip install psutil flask

pip install psutil flask
```

## Fonctionnalités

###  Informations Système
- Affichage du nom de la machine (hostname)
- Système d’exploitation et version
- Heure de démarrage (boot time)
- Durée d’activité (uptime)
- Nombre d’utilisateurs connectés
- Adresse IP locale
- Charge moyenne du système (1, 5 et 15 minutes)

###  CPU
- Utilisation totale du CPU (en %)
- Fréquence actuelle du processeur
- Utilisation détaillée par cœur avec code couleur :
  - Vert : ≤ 50%
  - Orange : 51–80%
  - Rouge : > 80%
- Rendu dynamique via Jinja2

###  Mémoire RAM
- Quantité totale de RAM (GB)
- RAM utilisée (GB)
- Pourcentage d’utilisation avec code couleur (green/orange/red)

###  Processus
- Récupération des processus actifs via `psutil`
- Tri des processus en fonction de l’utilisation CPU et RAM
- Affichage du **Top 3** des processus les plus gourmands :
  - PID
  - Nom du processus
  - % CPU
  - % RAM

###  Analyse de Fichiers
- Analyse récursive d’un répertoire (par défaut : dossier utilisateur)
- Comptage du nombre de fichiers par extension
- Calcul du pourcentage par extension
- Taille totale par extension (GB)
- Catégorie “OTHER” pour les extensions non reconnues
- Classement et affichage des **5 plus gros fichiers**
### Capture d'ecran
<img width="787" height="156" alt="image" src="https://github.com/user-attachments/assets/cb201577-0294-425d-9b72-57dd0d85d799" />
<img width="1205" height="676" alt="image" src="https://github.com/user-attachments/assets/357d096c-cdaa-4f8b-8fc6-483fe0926dae" />
<img width="1193" height="650" alt="image" src="https://github.com/user-attachments/assets/b06115bd-2557-4d91-ba64-475d0d78e88f" />

###  Interface HTML
- Dashboard généré via un template `template.html`
- Mise en forme simple et claire (tableaux + couleurs dynamiques)
- Code 100% statique ou affichage dynamique via Flask

###  Mode Statique (Soumission)
- Génération automatique d’un fichier `index.html`
- Aucun serveur nécessaire pour l’affichage
- Ouvrir simplement `index.html` dans un navigateur

###  Mode Dynamique (Flask)
- Interface actualisée à chaque requête
- Hébergement local via `flask run`


## Difficultés rencontrées

### Gestion des fichiers et permissions
- Certains fichiers ou répertoires nécessitent des autorisations spéciales.
- Génère des erreurs lors du scan récursif (résolues via try/except).

###  Parcours récursif du système de fichiers
- Analyse potentiellement longue sur des dossiers volumineux.
- Risque de ralentissement dû au nombre de fichiers scannés.

###  Précision et timing des métriques CPU
- Les valeurs CPU peuvent fluctuer rapidement.
- La synchronisation entre `psutil.cpu_percent()` et `percpu=True` nécessite un réglage du temps d’échantillonnage.

###  Intégration du template HTML
- Adaptation du template Jinja2 aux différentes sections du monitoring.
- Gestion du rendu dynamique et de l'injection des blocs HTML (listes, tableaux).

###  Double mode (statique & dynamique)
- Nécessité de maintenir deux accès au dashboard :
  - génération du fichier statique,
  - affichage en live avec Flask.
- Gestion des erreurs si le template est manquant ou mal placé.


### 👤 Équipe du projet
- **Rodriguez Ugo**
- **Cylia Ould Amara**
- **Placinta Emanuel**

