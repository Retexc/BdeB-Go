 <img width="1217" height="406" alt="Splash" src="https://github.com/user-attachments/assets/e88cf353-8a60-4702-8c12-4265d9939740" />
BdeB-Go est une application d’affichage en temps réel des horaires de transport en commun, conçue pour le Collège de Bois-de-Boulogne. Elle affiche les prochains passages, les alertes de service et le niveau d’achalandage des bus et trains, à partir des données GTFS et GTFS-RT.

# 📌 Fonctionnalités
✅ Horaires en temps réel des bus et trains (STM & Exo)

✅ Indicateurs d’achalandage (ex. : places disponibles)

✅ Alertes et interruptions de service

✅ Interface adaptée aux écrans muraux

✅ Panneau d’administration pour gérer l’affichage

## 🛠 Prérequis

**L'installateur s'occupe normalement de l'installation des prérequis**

1. **Python 3.11+**  
   - Pour exécuter le backend.  
   - Installez-le depuis : https://www.python.org/downloads/

2. **Node.js 16+ (LTS)**  
   - Pour construire et servir l’interface d’administration.  
   - Installez-le depuis : https://nodejs.org/ (version LTS recommandée)
  
3. **Clé API STM**
   - Pour pouvoir afficher les données en temps réels pour les autobus de la STM et l'état du métro
   - Créer un compte développeur sur le portail de la STM : https://portail.developpeurs.stm.info/apihub/#/
  
4. **Clé API Exo**
   - Pour pouvoir afficher les données en temps réels pour les trains de banlieue
   - Créer un compte développeur sur le portail Chrono : https://portail-developpeur.chrono-saeiv.com/

5. **Clé WeatherAPI**
   - Pour pouvoir afficher la météo et les alertes météorologiques.
   - Créer un compte sur le portail WeatherAPI : https://www.weatherapi.com/
     
## 🚀 Installation et démarrage

Ouvrez un terminal (PowerShell sous Windows et suivez ces étapes :


# 1. Cloner le répositoire
```
git clone https://github.com/Retexc/BdeB-Go
cd BdeB-Go
```
# 2. Créer un fichier d’environnement
Créer un nouveau fichier appelé . env dans le répertoire racine du projet :
Windows : Cliquez avec le bouton droit de la souris dans le dossier du projet, Nouveau document texte et renommer le fichier à .env

# 3. Ajoutez vos clés API au fichier .env
Ouvrez le fichier .env dans n’importe quel éditeur de texte et ajoutez vos clés :
```
STM_API_KEY=your_stm_api_key_here
CHRONO_TOKEN=your_exo_token_here
WEATHER_API_KEY=your_weather_api_key_here
GLOBAL_DELAY_MINUTES=0
```
# 4. Ouvrez l'installateur
```
.\install.bat
```
# 5. Lancer l’application
```
.\start.bat
```
