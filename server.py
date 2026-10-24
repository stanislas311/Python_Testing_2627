import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


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

def is_past(competition):
    date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
    return date < datetime.now()

app.jinja_env.globals['is_past'] = is_past

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form.get('email', '')
    matching = [c for c in clubs if c['email'] == email]
    if not matching:
        flash("Désolé, cet email est inconnu.")
        return render_template('index.html')
    club = matching[0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if not foundClub:
        flash("Club introuvable, veuillez vous reconnecter.")
        return render_template('index.html')
    if not foundCompetition:
        flash("Compétition introuvable, veuillez réessayer.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)
    if is_past(foundCompetition):
        flash("Cette compétition est terminée, la réservation n'est plus possible.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)
    return render_template('booking.html',club=foundClub,competition=foundCompetition)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    if is_past(competition):
        flash("Cette compétition est terminée, la réservation n'est plus possible.")
        return render_template('welcome.html', club=club, competitions=competitions)
    try:
        placesRequired = int(request.form.get('places', ''))
    except ValueError:
        placesRequired = 0
    if placesRequired <= 0:
        flash("Veuillez entrer un nombre de places valide (au moins 1).")
        return render_template('welcome.html', club=club, competitions=competitions)
    key = (competition['name'], club['name'])
    alreadyBooked = bookings.get(key, 0)
    if placesRequired > int(club['points']):
        flash("Vous n'avez pas assez de points pour cette réservation.")
        return render_template('welcome.html', club=club, competitions=competitions)
    if placesRequired > int(competition['numberOfPlaces']):
        flash("Il n'y a pas assez de places disponibles pour cette compétition.")
        return render_template('welcome.html', club=club, competitions=competitions)
    if alreadyBooked + placesRequired > MAX_PLACES_PAR_CLUB:
        flash("Un club ne peut pas réserver plus de 12 places par compétition.")
        return render_template('welcome.html', club=club, competitions=competitions)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points'])-placesRequired
    bookings[key] = alreadyBooked + placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


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
        rows.append({'rank': rank, 'name': c['name'], 'points': int(c['points'])})
    currentClub = request.args.get('club', '')
    return render_template('points.html', rows=rows, currentClub=currentClub)


@app.route('/rechercher')
def rechercher():
    clubName = request.args.get('club', '')
    terme = request.args.get('q', '').strip().lower()
    club = next((c for c in clubs if c['name'] == clubName), None)
    if not club:
        flash("Club introuvable, veuillez vous reconnecter.")
        return render_template('index.html')
    resultats = [c for c in competitions if terme in c['name'].lower()]
    if not resultats:
        flash("Aucune compétition ne correspond à votre recherche.")
    return render_template('welcome.html', club=club, competitions=resultats)


@app.route('/mesReservations')
def mesReservations():
    clubName = request.args.get('club', '')
    club = next((c for c in clubs if c['name'] == clubName), None)
    if not club:
        flash("Club introuvable, veuillez vous reconnecter.")
        return render_template('index.html')
    reservations = []
    for (competitionName, bookedClub), places in bookings.items():
        if bookedClub == club['name'] and places > 0:
            competition = next((c for c in competitions if c['name'] == competitionName), None)
            if competition:
                reservations.append({
                    'competition': competitionName,
                    'date': competition['date'],
                    'places': places,
                    'past': is_past(competition),
                })
    total = sum(r['places'] for r in reservations)
    return render_template('reservations.html', club=club, reservations=reservations, total=total)


@app.route('/annulerReservation', methods=['POST'])
def annulerReservation():
    club = next((c for c in clubs if c['name'] == request.form.get('club', '')), None)
    competition = next((c for c in competitions if c['name'] == request.form.get('competition', '')), None)
    if not club:
        flash("Club introuvable, veuillez vous reconnecter.")
        return render_template('index.html')
    if not competition:
        flash("Compétition introuvable, veuillez réessayer.")
        return redirect(url_for('mesReservations', club=club['name']))
    if is_past(competition):
        flash("Cette compétition est terminée, l'annulation n'est plus possible.")
        return redirect(url_for('mesReservations', club=club['name']))
    try:
        placesToCancel = int(request.form.get('places', ''))
    except ValueError:
        placesToCancel = 0
    if placesToCancel <= 0:
        flash("Veuillez entrer un nombre de places valide (au moins 1).")
        return redirect(url_for('mesReservations', club=club['name']))
    key = (competition['name'], club['name'])
    alreadyBooked = bookings.get(key, 0)
    if placesToCancel > alreadyBooked:
        flash("Vous ne pouvez pas annuler plus de places que vous n'en avez réservé.")
        return redirect(url_for('mesReservations', club=club['name']))
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) + placesToCancel
    club['points'] = int(club['points']) + placesToCancel
    bookings[key] = alreadyBooked - placesToCancel
    flash("Annulation effectuée : {} place(s) rendue(s).".format(placesToCancel))
    return redirect(url_for('mesReservations', club=club['name']))


@app.route('/logout')
def logout():
    return redirect(url_for('index'))