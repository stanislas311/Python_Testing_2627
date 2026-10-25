import json
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

MAX_PLACES_PAR_CLUB = 12
bookings = {}

MSG_CLUB_INTROUVABLE = "Club introuvable, veuillez vous reconnecter."
MSG_COMPETITION_INTROUVABLE = "Compétition introuvable, veuillez réessayer."
MSG_PLACES_INVALIDES = ("Veuillez entrer un nombre de places valide "
                        "(au moins 1).")
MSG_RESERVATION_TERMINEE = ("Cette compétition est terminée, "
                            "la réservation n'est plus possible.")
MSG_ANNULATION_TERMINEE = ("Cette compétition est terminée, "
                           "l'annulation n'est plus possible.")


def is_past(competition):
    date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
    return date < datetime.now()


app.jinja_env.globals['is_past'] = is_past


def render_welcome(club, competitionsList=None):
    if competitionsList is None:
        competitionsList = competitions
    return render_template(
        'welcome.html', club=club, competitions=competitionsList)


def refuse(club, message):
    flash(message)
    return render_welcome(club)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '')
    matching = [c for c in clubs if c['email'] == email]
    if not matching:
        flash("Désolé, cet email est inconnu.")
        return render_template('index.html')
    return render_welcome(matching[0])


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next(
        (c for c in competitions if c['name'] == competition), None)
    if not foundClub:
        flash(MSG_CLUB_INTROUVABLE)
        return render_template('index.html')
    if not foundCompetition:
        return refuse(foundClub, MSG_COMPETITION_INTROUVABLE)
    if is_past(foundCompetition):
        return refuse(foundClub, MSG_RESERVATION_TERMINEE)
    return render_template(
        'booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competitionName = request.form['competition']
    clubName = request.form['club']
    competition = [c for c in competitions if c['name'] == competitionName][0]
    club = [c for c in clubs if c['name'] == clubName][0]
    if is_past(competition):
        return refuse(club, MSG_RESERVATION_TERMINEE)
    try:
        placesRequired = int(request.form.get('places', ''))
    except ValueError:
        placesRequired = 0
    if placesRequired <= 0:
        return refuse(club, MSG_PLACES_INVALIDES)
    key = (competition['name'], club['name'])
    alreadyBooked = bookings.get(key, 0)
    if placesRequired > int(club['points']):
        return refuse(
            club, "Vous n'avez pas assez de points pour cette réservation.")
    if placesRequired > int(competition['numberOfPlaces']):
        return refuse(
            club,
            "Il n'y a pas assez de places disponibles pour cette compétition.")
    if alreadyBooked + placesRequired > MAX_PLACES_PAR_CLUB:
        return refuse(
            club,
            "Un club ne peut pas réserver plus de 12 places par compétition.")
    competition['numberOfPlaces'] = (
        int(competition['numberOfPlaces']) - placesRequired)
    club['points'] = int(club['points']) - placesRequired
    bookings[key] = alreadyBooked + placesRequired
    flash('Great-booking complete!')
    return render_welcome(club)


@app.route('/points')
def points():
    ranking = sorted(clubs, key=lambda c: int(c['points']), reverse=True)
    rows = []
    previousPoints = None
    rank = 0
    for position, c in enumerate(ranking, start=1):
        if int(c['points']) != previousPoints:
            rank = position
            previousPoints = int(c['points'])
        rows.append(
            {'rank': rank, 'name': c['name'], 'points': int(c['points'])})
    currentClub = request.args.get('club', '')
    return render_template('points.html', rows=rows, currentClub=currentClub)


@app.route('/rechercher')
def rechercher():
    clubName = request.args.get('club', '')
    terme = request.args.get('q', '').strip().lower()
    club = next((c for c in clubs if c['name'] == clubName), None)
    if not club:
        flash(MSG_CLUB_INTROUVABLE)
        return render_template('index.html')
    resultats = [c for c in competitions if terme in c['name'].lower()]
    if not resultats:
        flash("Aucune compétition ne correspond à votre recherche.")
    return render_welcome(club, resultats)


@app.route('/mesReservations')
def mesReservations():
    clubName = request.args.get('club', '')
    club = next((c for c in clubs if c['name'] == clubName), None)
    if not club:
        flash(MSG_CLUB_INTROUVABLE)
        return render_template('index.html')
    reservations = []
    for (competitionName, bookedClub), places in bookings.items():
        if bookedClub == club['name'] and places > 0:
            competition = next(
                (c for c in competitions if c['name'] == competitionName),
                None)
            if competition:
                reservations.append({
                    'competition': competitionName,
                    'date': competition['date'],
                    'places': places,
                    'past': is_past(competition),
                })
    total = sum(r['places'] for r in reservations)
    return render_template(
        'reservations.html', club=club, reservations=reservations,
        total=total)


@app.route('/annulerReservation', methods=['POST'])
def annulerReservation():
    clubName = request.form.get('club', '')
    competitionName = request.form.get('competition', '')
    club = next((c for c in clubs if c['name'] == clubName), None)
    competition = next(
        (c for c in competitions if c['name'] == competitionName), None)
    if not club:
        flash(MSG_CLUB_INTROUVABLE)
        return render_template('index.html')
    backToList = url_for('mesReservations', club=club['name'])
    if not competition:
        flash(MSG_COMPETITION_INTROUVABLE)
        return redirect(backToList)
    if is_past(competition):
        flash(MSG_ANNULATION_TERMINEE)
        return redirect(backToList)
    try:
        placesToCancel = int(request.form.get('places', ''))
    except ValueError:
        placesToCancel = 0
    if placesToCancel <= 0:
        flash(MSG_PLACES_INVALIDES)
        return redirect(backToList)
    key = (competition['name'], club['name'])
    alreadyBooked = bookings.get(key, 0)
    if placesToCancel > alreadyBooked:
        flash("Vous ne pouvez pas annuler plus de places "
              "que vous n'en avez réservé.")
        return redirect(backToList)
    competition['numberOfPlaces'] = (
        int(competition['numberOfPlaces']) + placesToCancel)
    club['points'] = int(club['points']) + placesToCancel
    bookings[key] = alreadyBooked - placesToCancel
    flash("Annulation effectuée : {} place(s) rendue(s).".format(
        placesToCancel))
    return redirect(backToList)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
