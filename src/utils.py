from datetime import datetime


def calculate_age(birth_date):
    """Calcule l'age à partir de la date de naissance"""
    now = datetime.now()
    age = now.year - birth_date.year - ((now.month, now.day) < (birth_date.month, birth_date.day))
    return age
