import html


def texte(response):
    """Retourne le contenu HTML décodé (accents et apostrophes lisibles)."""
    return html.unescape(response.data.decode('utf-8'))
