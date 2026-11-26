# GUDLFT — Portail de réservation de compétitions

Application web Flask légère permettant aux secrétaires de clubs sportifs de consulter leurs points, réserver ou annuler des places pour des compétitions régionales et suivre le classement public des clubs.

## Fonctionnalités

- **Connexion des secrétaires** via l'email du club ([clubs.json](clubs.json)), sans crash sur email inconnu.
- **Réservation de places** avec vérification des règles métier :
  - blocage des compétitions déjà terminées (`is_past`) ;
  - validation des saisies (`parse_places`, minimum 1 place) ;
  - vérification du solde de points du club et des places disponibles ;
  - plafond cumulé de **12 places maximum** par club et par compétition (`MAX_PLACES_PAR_CLUB`).
- **Tableau public des points** (`/points`), accessible sans connexion, trié par points décroissants avec gestion des ex aequo.
- **Recherche de compétitions** (`/rechercher`) par nom, insensible à la casse.
- **Historique et annulation** (`/mesReservations`, `/annulerReservation`) pour les compétitions à venir, avec restitution des points et des places.

## Prérequis et installation

- Python 3.11+
- Environnement virtuel recommandé (`venv`)

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Lancer l'application

```bash
flask --app server run
```

L'application est ensuite accessible sur `http://127.0.0.1:5000`.

Comptes de démonstration disponibles dans [clubs.json](clubs.json) :
- `john@simplylift.co` (*Simply Lift*, 13 points)
- `admin@irontemple.com` (*Iron Temple*, 4 points)
- `kate@shelifts.co.uk` (*She Lifts*, 12 points)

## Architecture du projet

```text
.
├── clubs.json                      # Données des clubs (secrétaires et points)
├── competitions.json               # Données des compétitions
├── server.py                       # Application Flask et logique métier
├── static/
│   └── style.css                   # Feuille de style
├── templates/                      # Vues Jinja2 (accueil, réservation, points, historique)
├── tests/
│   └── unit/                       # Tests unitaires (fonctions pures et logique métier)
├── rapports/
│   ├── flake8_report.txt           # Rapport de conformité PEP 8
│   ├── rapport_bugs_et_solutions.md
│   ├── rapport_performance.html    # Rapport Locust HTML
│   └── rapport_performance_stats.csv
├── pytest.ini
├── .coveragerc
└── requirements.txt
```

## Tests et couverture

Le projet est actuellement à l'étape des **tests unitaires** (`tests/unit`) :

```bash
# Tests unitaires
python -m pytest tests/unit

# Suite complète et couverture
python -m pytest
python -m coverage run -m pytest
python -m coverage report
python -m coverage html
```

Résultats actuels :
- **102 tests unitaires réussis** (`tests/unit`)
- **Couverture de `server.py`** : **66 %** (135 instructions sur 205 — la logique métier est couverte ; les routes Flask restantes seront couvertes lors de l'ajout des tests d'intégration).

## Qualité de code (Flake8)

```bash
python -m flake8 server.py tests --count --statistics
```

Résultat : **0 erreur, 0 avertissement** (Flake8 7.4.1, Python 3.11.9). Voir [rapports/flake8_report.txt](rapports/flake8_report.txt).

## Tests de performance (Locust)

Seuils définis par les spécifications :
- chargement de la liste des compétitions : moins de 5 secondes ;
- mise à jour des points (réservation / annulation) : moins de 2 secondes.

Commande (serveur Flask lancé dans un premier terminal) :

```bash
locust -f tests/performance/locustfile.py --headless -u 6 -r 2 -t 20s --host http://127.0.0.1:5000 --html rapports/rapport_performance.html --csv rapports/rapport_performance
```

Résultats enregistrés dans [rapports/rapport_performance_stats.csv](rapports/rapport_performance_stats.csv) (6 utilisateurs simultanés, 20 secondes) :

| Requête | Nombre | Moyenne (ms) | 95 % (ms) | Maximum (ms) | Échecs |
|---|---|---|---|---|---|
| Liste des compétitions | 45 | 6 | 11 | 17 | 0 |
| Page de réservation | 24 | 6 | 10 | 23 | 0 |
| Tableau des points | 24 | 5 | 9 | 10 | 0 |
| Mise à jour des points (réservation) | 15 | 6 | 10 | 10 | 0 |
| Mise à jour des points (annulation) | 15 | 13 | 20 | 20 | 0 |
| **Total** | **123** | **7** | **15** | **23** | **0** |

## Conventions Git

- Branche principale : `main` (code stable et testé).
- Branches par tâche : `bug/<nom>`, `feature/<nom>`, `amelioration/<nom>`.
- Branche de révision : `QA` (non fusionnée dans `main`).
