# Intro
```
Hey,

Je viens de recevoir le rapport de QA pour la phase 1 du projet. Il y a plusieurs bogues, dont un qui fait planter l'application ! 
Malheureusement, je ne suis pas au bureau pour les prochains jours (un de mes enfants est tombé malade ce week-end). 
Je ne sais pas encore quand je pourrai être là dans la semaine. Pourriez-vous prendre en charge la mise en œuvre du projet ? 
Vous devrez régler les bogues de la phase 1 et mettre en œuvre les éléments de la phase 2 (j'ai ajouté le travail de la phase 2 et les bogues de la section “issues” du repo). 

Vous devrez cloner et forker le repo et le mettre en place sur votre machine locale (tout ce dont vous avez besoin se trouve dans le fichier README). 
Ensuite, passez en revue les bogues dans la section des problèmes, puis essayez de reproduire les problèmes sur votre machine locale pour résoudre les bogues et ajouter la gestion des erreurs. 
Pour gagner du temps de configuration, nous utilisons Flask et JSON pour éviter d'utiliser une base de données. 
La plupart des outils dont vous aurez besoin se trouvent dans le fichier requirements.txt dans le repo, 
mais vous devrez installer Flask et notre framework de test préféré, pytest, ainsi que notre outil de test de performance, Locust. 

Vous devrez également préparer un rapport de test et un rapport de performances, 
conformément au guide de développement à la fin des spécifications fonctionnelles ci-jointes. 
Veillez à suivre toutes les directives, car le QA nous reproche de ne pas respecter les normes. 
Vous devez tester de manière approfondie les résultats requis (à la fois les happy paths et les sad paths) pour toutes les fonctionnalités de l'application.  
Je vous encourage également à adopter une approche de TDD, car cela vous aidera à rationaliser votre travail. 

Une fois que vous aurez terminé, nous ferons un examen de ce que vous avez dans la branche QA du code. 
Nous examinerons les rapports et la manière dont vous avez résolu les problèmes, 
nous examinerons votre code et nous testerons la couverture de la nouvelle fonctionnalité. 

Merci !

```
1. Why


    This is a proof of concept (POC) project to show a light-weight version of our competition booking platform. The aim is the keep things as light as possible, and use feedback from the users to iterate.

2. Getting Started

    This project uses the following technologies:

    * Python v3.x+

    * [Flask](https://flask.palletsprojects.com/en/1.1.x/)

        Whereas Django does a lot of things for us out of the box, Flask allows us to add only what we need. 
     

    * [Virtual environment](https://virtualenv.pypa.io/en/stable/installation.html)

        This ensures you'll be able to install the correct packages without interfering with Python on your machine.

        Before you begin, please ensure you have this installed globally. 


3. Installation

    - After cloning, change into the directory and type <code>virtualenv .</code>. This will then set up a a virtual python environment within that directory.

    - Next, type <code>source bin/activate</code>. You should see that your command prompt has changed to the name of the folder. This means that you can install packages in here without affecting affecting files outside. To deactivate, type <code>deactivate</code>

    - Rather than hunting around for the packages you need, you can install in one step. Type <code>pip install -r requirements.txt</code>. This will install all the packages listed in the respective file. If you install a package, make sure others know by updating the requirements.txt file. An easy way to do this is <code>pip freeze > requirements.txt</code>

    - Flask requires that you set an environmental variable to the python file. However you do that, you'll want to set the file to be <code>server.py</code>. Check [here](https://flask.palletsprojects.com/en/1.1.x/quickstart/#a-minimal-application) for more details

    - You should now be ready to test the application. In the directory, type either <code>flask run</code> or <code>python -m flask run</code>. The app should respond with an address you should be able to go to using your browser.

4. Current Setup

    The app is powered by [JSON files](https://www.tutorialspoint.com/json/json_quick_guide.htm). This is to get around having a DB until we actually need one. The main ones are:
     
    * competitions.json - list of competitions
    * clubs.json - list of clubs with relevant information. You can look here to see what email addresses the app will accept for login.

5. Testing

    You are free to use whatever testing framework you like-the main thing is that you can show what tests you are using.

    We also like to show how well we're testing, so there's a module called 
    [coverage](https://coverage.readthedocs.io/en/coverage-5.1/) you should add to your project.
   
## 6. Flake8 Report

Commande lancée à la racine du projet, environnement virtuel activé :

```
python -m flake8 server.py tests --count --statistics
```

Résultat final : **0 erreur, 0 avertissement**.

Avant correction, Flake8 signalait 53 remarques sur `server.py` et sur le fichier de tests :

| Code | Signification | Correction |
|---|---|---|
| E231 | espace manquant après une virgule | espaces ajoutés |
| E111 / E117 | indentation incorrecte | indentation de 4 espaces |
| E302 / E305 | lignes vides manquantes autour des fonctions | 2 lignes vides |
| E501 | ligne de plus de 79 caractères | lignes découpées, messages regroupés dans des constantes |
| W292 | pas de retour à la ligne en fin de fichier | ajouté |

Version utilisée : Flake8 7.4.1 (Python 3.11.9).

## 7. Rapport de tests et de couverture

Les tests sont rangés dans le dossier `tests/` :

* `tests/unit` : helpers purs, chargement des données et fonction `is_past` (15 tests)
* `tests/integration` : connexion, réservation, règles métier, classement, recherche, historique et annulation, avec les cas normaux (happy paths) et les cas d'erreur (sad paths) (47 tests)
* `tests/functional` : parcours complet de réservation et parcours d'erreur (2 tests)
* `tests/conftest.py` : remet les données à zéro avant chaque test

Commandes :

```
python -m pytest
python -m coverage run -m pytest
python -m coverage report
python -m coverage html
```

Résultats : **64 tests réussis** (15 unitaires, 47 d'intégration et 2 fonctionnels), couverture de `server.py` : **100 %** (162 instructions sur 162). Le rapport détaillé se génère dans `htmlcov/index.html`.

Branches de sujet fusionnées dans `main` :

* `amelioration/dates-competitions-json`
* `amelioration/gitignore-venv`
* `amelioration/interface-css`
* `amelioration/performance-locust`
* `amelioration/refonte-design`
* `amelioration/tests-et-couverture`
* `amelioration/tests-fonctionnels`
* `amelioration/tests-unitaires`
* `bug/club-competition-introuvable`
* `bug/competitions-passees`
* `bug/depassement-places-disponibles`
* `bug/email-inconnu-crash`
* `bug/limite-12-places`
* `bug/points-non-deduits`
* `bug/saisie-places-invalide`
* `feature/annulation-reservation`
* `feature/historique-reservations`
* `feature/recherche-competitions`
* `feature/tableau-points-public`

## 8. Rapport de performance

Outil : Locust 2.47.0. Le scénario est dans `tests/performance/locustfile.py` : chaque utilisateur simulé charge la liste des compétitions, ouvre le tableau des points et la page de réservation, puis réserve une place et l'annule.

Seuils demandés par les spécifications :

* chargement de la liste des compétitions : moins de 5 secondes ;
* mise à jour des points (réservation) : moins de 2 secondes.

Commande (le serveur Flask tourne dans un premier terminal) :

```
locust -f tests/performance/locustfile.py --headless -u 6 -r 2 -t 20s --host http://127.0.0.1:5000 --html rapports/rapport_performance.html --csv rapports/rapport_performance
```

Conditions : 6 utilisateurs simultanés, 2 nouveaux utilisateurs par seconde,
20 secondes, serveur de développement Flask sous Windows (Python 3.11.9).

Résultats (temps en millisecondes) :

| Requête | Nombre | Moyenne (ms) | 95 % (ms) | Maximum (ms) | Échecs |
|---|---|---|---|---|---|
| Liste des compétitions | 45 | 6 | 11 | 17 | 0 |
| Page de réservation | 24 | 6 | 10 | 23 | 0 |
| Tableau des points | 24 | 5 | 9 | 10 | 0 |
| Mise à jour des points (réservation) | 15 | 6 | 10 | 10 | 0 |
| Mise à jour des points (annulation) | 15 | 13 | 20 | 20 | 0 |
| **Total** | **123** | **7** | **15** | **23** | **0** |

Conclusion : les seuils sont respectés (17 ms au maximum pour la liste et
20 ms pour une mise à jour). Ces mesures portent sur un serveur de
développement avec des données en mémoire et ne remplacent pas un test en
production. Les rapports HTML et CSV existants dans `rapports/` sont
conservés sans modification.
