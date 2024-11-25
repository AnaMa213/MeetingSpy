    
    
def convert_seconds(secondes):
    """
    Convertit un nombre de secondes en une chaîne formatée en minutes et secondes.

    Paramètres
    ----------
    secondes : float
        Le nombre de secondes à convertir.

    Retourne
    -------
    str
        Une chaîne formatée représentant la durée en minutes et secondes.
    """
    if secondes < 60:
        return f"{secondes:.2f} s"
    else:
        minutes = secondes // 60
        secondes_restantes = secondes % 60
        return f"{minutes:.0f}min{secondes_restantes:.2f}s"