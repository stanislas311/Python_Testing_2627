# Bugs trouvés et solutions apportées

Projet : Python_Testing_2627 (application Flask GUDLFT de réservation de places de compétitions)
Auteur : stanislas311 (compte GitHub)
Date : 25 octobre 2026

Ce fichier liste, en langage simple, chaque problème trouvé dans l'application et la façon dont il a été corrigé. Chaque correction a été faite sur sa propre branche Git, après avoir reproduit le bug dans le navigateur, puis vérifiée par un test automatique (dossier `tests/`).

## Résumé

| N° | Problème | Branche | Gravité |
|---|---|---|---|
| 1 | Plantage avec un email inconnu | `bug/email-inconnu-crash` | Très grave (l'appli plante) |
| 2 | Plantage si le club ou la compétition n'existe pas | `bug/club-competition-introuvable` | Grave (l'appli plante) |
| 3 | Les points du club ne diminuent pas | `bug/points-non-deduits` | Grave (règle métier) |
| 4 | Plus de places réservées que disponibles | `bug/depassement-places-disponibles` | Grave (règle métier) |
| 5 | Plus de 12 places réservées par un club | `bug/limite-12-places` | Moyenne (règle métier) |
| 6 | Saisie invalide (vide, négative) acceptée | `bug/saisie-places-invalide` | Grave (plantage et points gagnés) |
| 7 | Réservation d'une compétition déjà terminée | `bug/competitions-passees` | Moyenne (règle métier) |
| 8 | Dates du fichier JSON toutes dans le passé | `amelioration/dates-competitions-json` | Moyenne (données) |
| 9 | Code non conforme à Flake8 (53 remarques) | `amelioration/tests-et-couverture` | Faible (style) |
| 10 | Dossier `tests/` ignoré par Git | `amelioration/tests-et-couverture` | Moyenne (outils) |

## Détail de chaque bug

### Bug 1 : l'application plante avec un email inconnu

- **Comment on l'a vu :** sur la page d'accueil, taper un email qui n'existe pas (par exemple `test@test.com`) affiche « Internal Server Error ».
- **La cause :** le code cherche le club qui a cet email et prend le premier résultat. S'il n'y en a aucun, Python génère une erreur (`IndexError`).
- **La solution :** on vérifie d'abord qu'un club correspond. Sinon, on revient à l'accueil avec le message « Désolé, cet email est inconnu. ». La page d'accueil affiche maintenant les messages.
- **Test automatique :** `test_connexion_email_inconnu_affiche_un_message`, `test_connexion_sans_email_ne_plante_pas`.

### Bug 2 : plantage si le club ou la compétition n'existe pas

- **Comment on l'a vu :** ouvrir directement `/book/Inconnue/Simply Lift` ou `/book/Spring Festival/Inconnu` affiche la même erreur (`IndexError`).
- **La cause :** même défaut que le bug 1. Le code d'origine avait aussi un deuxième défaut : dans le cas d'erreur, il passait un simple texte à la page au lieu du club.
- **La solution :** on cherche le club et la compétition de façon sûre. Si l'un manque, on affiche « Club introuvable... » ou « Compétition introuvable... ».
- **Effet de bord trouvé en testant :** après une de ces erreurs, saisir un email sur la page d'accueil donnait « Method Not Allowed », car le formulaire utilisait une adresse relative qui changeait selon la page. On l'a remplacée par une adresse fixe (`url_for`).
- **Test automatique :** `test_book_competition_inconnue`, `test_book_club_inconnu`.

### Bug 3 : les points du club ne diminuent pas

- **Comment on l'a vu :** le club Simply Lift (13 points) réserve 2 places. Les places de la compétition passent de 25 à 23, mais ses points restent à 13.
- **La cause :** le code retirait les places de la compétition, mais jamais les points du club.
- **La solution :** on retire maintenant les places réservées des points du club. On refuse aussi la réservation si le club n'a pas assez de points.
- **Test automatique :** `test_reservation_valide_deduit_points_et_places`, `test_reservation_refusee_si_points_insuffisants`.

### Bug 4 : on peut réserver plus de places qu'il n'y en a

- **Comment on l'a vu :** réserver 11 places pour une compétition qui en a 10 était accepté, et la compétition affichait -1 place.
- **La cause :** aucune vérification du nombre de places disponibles.
- **La solution :** on compare avec les places disponibles avant d'accepter. Sinon : « Il n'y a pas assez de places disponibles pour cette compétition. », et rien ne change.
- **Test automatique :** `test_reservation_refusee_si_pas_assez_de_places`.

### Bug 5 : on peut réserver plus de 12 places

- **Comment on l'a vu :** les spécifications interdisent plus de 12 places par club et par compétition, mais 13 places étaient acceptées.
- **La cause :** aucune limite dans le code.
- **La solution :** l'application retient combien de places chaque club a déjà réservées pour chaque compétition. Elle refuse si le total dépasse 12, même si la réservation est faite en plusieurs fois (par exemple 12 puis 1).
- **Test automatique :** `test_reservation_refusee_au_dela_de_12_places`, `test_limite_de_12_places_cumulee`.

### Bug 6 : les saisies invalides sont acceptées ou font planter

- **Comment on l'a vu :** un champ vide faisait planter l'appli (`ValueError`). Un nombre négatif comme `-5` donnait 5 points de plus au club.
- **La cause :** la saisie était convertie en nombre sans aucune vérification.
- **La solution :** on convertit de façon sûre et on refuse tout ce qui n'est pas un nombre d'au moins 1 (« Veuillez entrer un nombre de places valide »). Le champ de la page de réservation bloque aussi ces valeurs dans le navigateur.
- **Test automatique :** `test_reservation_refusee_si_saisie_invalide` (4 cas : vide, 0, -5, texte).

### Bug 7 : on peut réserver une compétition déjà terminée

- **Comment on l'a vu :** la compétition « Winter Cup » date de janvier 2026, mais le bouton « Book Places » restait disponible et la réservation était acceptée.
- **La cause :** l'application ne comparait jamais la date de la compétition avec la date du jour.
- **La solution :** une fonction `is_past` fait cette comparaison. Le blocage est fait à trois endroits : la page du club n'affiche plus le bouton (elle montre « Compétition terminée »), la page de réservation refuse l'accès, et l'achat est refusé même si la demande est envoyée directement.
- **Test automatique :** `test_book_competition_passee`, `test_reservation_refusee_pour_une_competition_passee`.

### Problème 8 : les dates du fichier JSON étaient toutes dans le passé

- **Comment on l'a vu :** les deux compétitions de `competitions.json` étaient datées de 2020, donc déjà terminées.
- **La solution :** les dates ont été remplacées par des dates futures (15 décembre 2026 et 20 février 2027). La compétition « Winter Cup » a été ajoutée volontairement dans le passé, pour pouvoir tester le bug 7.

### Problème 9 : le code ne respectait pas le style Flake8

- **Comment on l'a vu :** `python -m flake8 server.py tests` signalait 53 remarques (espaces manquants après les virgules, indentation, lignes vides, lignes trop longues, retour à la ligne manquant en fin de fichier).
- **La solution :** `server.py` a été remis en forme et les lignes trop longues des tests ont été coupées. Résultat final : 0 remarque. Le rapport est dans `rapports/flake8_report.txt`.

### Problème 10 : le dossier `tests/` était ignoré par Git

- **Comment on l'a vu :** `git add tests/...` répondait que les fichiers étaient ignorés, et le premier commit des tests ne contenait que `pytest.ini`.
- **La cause :** le fichier `.gitignore` d'origine contenait la ligne `tests/`.
- **La solution :** on a retiré cette ligne et refait les commits dans l'ordre. Au passage, `venv/`, les fichiers temporaires Python et le fichier inutile `.DS_Store` sont maintenant ignorés.

## Résultat final

- 51 tests automatiques réussis (cas normaux et cas d'erreur)
- Couverture de `server.py` : 100 % (le minimum demandé était 60 %)
- Flake8 : 0 remarque
- Tests de performance Locust : 0 échec sur 340 requêtes, temps maximum de 185 ms (seuils demandés : 5 s et 2 s)
