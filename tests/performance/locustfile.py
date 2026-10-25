"""Tests de performance (Locust) de l'application GUDLFT.

Seuils demandes par les specifications :
* chargement de la liste des competitions : moins de 5 secondes ;
* mise a jour des points (reservation) : moins de 2 secondes.
"""
from locust import HttpUser, between, events, task

EMAIL = "john@simplylift.co"
CLUB = "Simply Lift"
COMPETITION = "Spring Festival"

SEUIL_LISTE = 5.0
SEUIL_MISE_A_JOUR = 2.0


def verifier_temps(reponse, seuil):
    """Marque la requete en echec si elle est en erreur ou trop lente."""
    duree = reponse.elapsed.total_seconds()
    if reponse.status_code != 200:
        reponse.failure("code HTTP {}".format(reponse.status_code))
    elif duree > seuil:
        reponse.failure(
            "trop lent : {:.2f} s (seuil {} s)".format(duree, seuil))
    else:
        reponse.success()


class SecretaireDeClub(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(4)
    def charger_la_liste_des_competitions(self):
        with self.client.post(
                "/showSummary",
                data={"email": EMAIL},
                name="Liste des competitions",
                catch_response=True) as reponse:
            verifier_temps(reponse, SEUIL_LISTE)

    @task(2)
    def afficher_le_tableau_des_points(self):
        with self.client.get(
                "/points",
                params={"club": CLUB},
                name="Tableau des points",
                catch_response=True) as reponse:
            verifier_temps(reponse, SEUIL_LISTE)

    @task(2)
    def ouvrir_la_page_de_reservation(self):
        with self.client.get(
                "/book/{}/{}".format(COMPETITION, CLUB),
                name="Page de reservation",
                catch_response=True) as reponse:
            verifier_temps(reponse, SEUIL_LISTE)

    @task(1)
    def reserver_puis_annuler(self):
        donnees = {"competition": COMPETITION, "club": CLUB, "places": 1}
        with self.client.post(
                "/purchasePlaces",
                data=donnees,
                name="Mise a jour des points (reservation)",
                catch_response=True) as reponse:
            verifier_temps(reponse, SEUIL_MISE_A_JOUR)
        with self.client.post(
                "/annulerReservation",
                data=donnees,
                name="Mise a jour des points (annulation)",
                catch_response=True) as reponse:
            verifier_temps(reponse, SEUIL_MISE_A_JOUR)


@events.quitting.add_listener
def definir_le_code_de_sortie(environment, **kwargs):
    """Code de sortie 1 si au moins une requete a depasse un seuil."""
    echecs = environment.stats.total.num_failures
    environment.process_exit_code = 1 if echecs else 0
