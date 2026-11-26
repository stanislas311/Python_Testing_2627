import json
import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for


def _load_json_list(filepath, key):
    """Charge une liste d'éléments depuis un fichier JSON."""
    with open(filepath, encoding='utf-8') as file_handle:
        return json.load(file_handle)[key]


def loadClubs(filepath='clubs.json'):
    """Charge la liste des clubs depuis le fichier JSON."""
    return _load_json_list(filepath, 'clubs')


def loadCompetitions(filepath='competitions.json'):
    """Charge la liste des compétitions depuis le fichier JSON."""
    return _load_json_list(filepath, 'competitions')


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

competitions = loadCompetitions()
clubs = loadClubs()

MAX_PLACES_PAR_CLUB = 12
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
bookings = {}

MSG_EMAIL_INCONNU = "Désolé, cet email est inconnu."
MSG_CLUB_INTROUVABLE = "Club introuvable, veuillez vous reconnecter."
MSG_COMPETITION_INTROUVABLE = "Compétition introuvable, veuillez réessayer."
MSG_PLACES_INVALIDES = (
    "Veuillez entrer un nombre de places valide (au moins 1)."
)
MSG_POINTS_INSUFFISANTS = (
    "Vous n'avez pas assez de points pour cette réservation."
)
MSG_PLACES_INSUFFISANTES = (
    "Il n'y a pas assez de places disponibles pour cette compétition."
)
MSG_LIMITE_PLACES = (
    "Un club ne peut pas réserver plus de 12 places par compétition."
)
MSG_RESERVATION_REUSSIE = "Great-booking complete!"
MSG_RESERVATION_TERMINEE = (
    "Cette compétition est terminée, la réservation n'est plus possible."
)
MSG_ANNULATION_TERMINEE = (
    "Cette compétition est terminée, l'annulation n'est plus possible."
)
MSG_ANNULATION_TROP_DE_PLACES = (
    "Vous ne pouvez pas annuler plus de places que vous n'en avez réservé."
)
MSG_AUCUNE_COMPETITION = "Aucune compétition ne correspond à votre recherche."


def find_club(name, clubs_list=None):
    """Retourne le club correspondant au nom, ou None."""
    source = clubs if clubs_list is None else clubs_list
    return next((c for c in source if c['name'] == name), None)


def find_club_by_email(email, clubs_list=None):
    """Retourne le club correspondant à l'email, ou None."""
    source = clubs if clubs_list is None else clubs_list
    return next((c for c in source if c['email'] == email), None)


def find_competition(name, competitions_list=None):
    """Retourne la compétition correspondant au nom, ou None."""
    source = competitions if competitions_list is None else competitions_list
    return next((c for c in source if c['name'] == name), None)


def is_past(competition, now=None):
    """Indique si la date d'une compétition est antérieure à maintenant."""
    date = datetime.strptime(competition['date'], DATE_FORMAT)
    reference = datetime.now() if now is None else now
    return date < reference


def parse_places(value):
    """Convertit une saisie de nombre de places en entier (0 si invalide)."""
    if isinstance(value, bool):
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def compute_ranking(clubs_list):
    """Calcule le classement par points décroissants (avec ex aequo)."""
    ranking = sorted(
        clubs_list, key=lambda c: int(c['points']), reverse=True
    )
    rows = []
    previous_points = None
    rank = 0
    for position, club in enumerate(ranking, start=1):
        points = int(club['points'])
        if points != previous_points:
            rank = position
            previous_points = points
        rows.append({
            'rank': rank,
            'name': club['name'],
            'points': points,
        })
    return rows


def filter_competitions(term, competitions_list=None):
    """Filtre les compétitions dont le nom contient le terme recherché."""
    source = competitions if competitions_list is None else competitions_list
    query = (term or '').strip().lower()
    if not query:
        return list(source)
    return [c for c in source if query in c['name'].lower()]


def book_places(
    club,
    competition,
    places_required,
    bookings_store=None,
    max_places=MAX_PLACES_PAR_CLUB,
    now=None,
):
    """Valide et enregistre une réservation de places pour un club."""
    store = bookings if bookings_store is None else bookings_store
    if is_past(competition, now=now):
        return False, MSG_RESERVATION_TERMINEE
    if places_required <= 0:
        return False, MSG_PLACES_INVALIDES
    key = (competition['name'], club['name'])
    already_booked = store.get(key, 0)
    if places_required > int(club['points']):
        return False, MSG_POINTS_INSUFFISANTS
    if places_required > int(competition['numberOfPlaces']):
        return False, MSG_PLACES_INSUFFISANTES
    if already_booked + places_required > max_places:
        return False, MSG_LIMITE_PLACES

    competition['numberOfPlaces'] = (
        int(competition['numberOfPlaces']) - places_required
    )
    club['points'] = int(club['points']) - places_required
    store[key] = already_booked + places_required
    return True, MSG_RESERVATION_REUSSIE


def get_club_reservations(
    club_name,
    bookings_store=None,
    competitions_list=None,
    now=None,
):
    """Retourne les réservations actives d'un club et le total de places."""
    store = bookings if bookings_store is None else bookings_store
    source = competitions if competitions_list is None else competitions_list
    reservations = []
    for (competition_name, booked_club), places in store.items():
        if booked_club == club_name and places > 0:
            competition = find_competition(competition_name, source)
            if competition:
                reservations.append({
                    'competition': competition_name,
                    'date': competition['date'],
                    'places': places,
                    'past': is_past(competition, now=now),
                })
    total = sum(r['places'] for r in reservations)
    return reservations, total


def cancel_places(
    club,
    competition,
    places_to_cancel,
    bookings_store=None,
    now=None,
):
    """Valide et exécute l'annulation de places réservées."""
    store = bookings if bookings_store is None else bookings_store
    if is_past(competition, now=now):
        return False, MSG_ANNULATION_TERMINEE
    if places_to_cancel <= 0:
        return False, MSG_PLACES_INVALIDES
    key = (competition['name'], club['name'])
    already_booked = store.get(key, 0)
    if places_to_cancel > already_booked:
        return False, MSG_ANNULATION_TROP_DE_PLACES

    competition['numberOfPlaces'] = (
        int(competition['numberOfPlaces']) + places_to_cancel
    )
    club['points'] = int(club['points']) + places_to_cancel
    remaining = already_booked - places_to_cancel
    if remaining > 0:
        store[key] = remaining
    else:
        store.pop(key, None)
    return True, "Annulation effectuée : {} place(s) rendue(s).".format(
        places_to_cancel
    )


app.jinja_env.globals['is_past'] = is_past


def render_welcome(club, competitions_list=None):
    """Affiche la page d'accueil du club avec la liste des compétitions."""
    items = competitions if competitions_list is None else competitions_list
    return render_template('welcome.html', club=club, competitions=items)


def refuse(club, message):
    """Affiche un message d'erreur sur la page du club."""
    flash(message)
    return render_welcome(club)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '')
    club = find_club_by_email(email)
    if not club:
        flash(MSG_EMAIL_INCONNU)
        return render_template('index.html')
    return render_welcome(club)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = find_club(club)
    found_competition = find_competition(competition)
    if not found_club:
        flash(MSG_CLUB_INTROUVABLE)
        return render_template('index.html')
    if not found_competition:
        return refuse(found_club, MSG_COMPETITION_INTROUVABLE)
    if is_past(found_competition):
        return refuse(found_club, MSG_RESERVATION_TERMINEE)
    return render_template(
        'booking.html', club=found_club, competition=found_competition
    )


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get('competition', '')
    club_name = request.form.get('club', '')
    club = find_club(club_name)
    if not club:
        flash(MSG_CLUB_INTROUVABLE)
        return render_template('index.html')
    competition = find_competition(competition_name)
    if not competition:
        return refuse(club, MSG_COMPETITION_INTROUVABLE)
    places_required = parse_places(request.form.get('places', ''))
    _, message = book_places(club, competition, places_required)
    flash(message)
    return render_welcome(club)


@app.route('/points')
def points():
    rows = compute_ranking(clubs)
    current_club = request.args.get('club', '')
    return render_template(
        'points.html', rows=rows, currentClub=current_club
    )


@app.route('/rechercher')
def rechercher():
    club_name = request.args.get('club', '')
    terme = request.args.get('q', '')
    club = find_club(club_name)
    if not club:
        flash(MSG_CLUB_INTROUVABLE)
        return render_template('index.html')
    resultats = filter_competitions(terme)
    if not resultats:
        flash(MSG_AUCUNE_COMPETITION)
    return render_welcome(club, resultats)


@app.route('/mesReservations')
def mesReservations():
    club_name = request.args.get('club', '')
    club = find_club(club_name)
    if not club:
        flash(MSG_CLUB_INTROUVABLE)
        return render_template('index.html')
    reservations, total = get_club_reservations(club['name'])
    return render_template(
        'reservations.html',
        club=club,
        reservations=reservations,
        total=total,
    )


@app.route('/annulerReservation', methods=['POST'])
def annulerReservation():
    club_name = request.form.get('club', '')
    competition_name = request.form.get('competition', '')
    club = find_club(club_name)
    if not club:
        flash(MSG_CLUB_INTROUVABLE)
        return render_template('index.html')
    back_to_list = url_for('mesReservations', club=club['name'])
    competition = find_competition(competition_name)
    if not competition:
        flash(MSG_COMPETITION_INTROUVABLE)
        return redirect(back_to_list)
    places_to_cancel = parse_places(request.form.get('places', ''))
    _, message = cancel_places(club, competition, places_to_cancel)
    flash(message)
    return redirect(back_to_list)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
