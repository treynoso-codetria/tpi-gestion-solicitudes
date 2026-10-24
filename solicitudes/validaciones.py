"""Reglas de formato de los datos que ingresa el usuario."""

LARGO_MINIMO_LEGAJO = 5
LARGO_MINIMO_DESCRIPCION = 10


def es_legajo_valido(legajo: str) -> bool:
    return legajo.isdigit() and len(legajo) >= LARGO_MINIMO_LEGAJO


def es_email_valido(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1]


def es_descripcion_valida(descripcion: str) -> bool:
    return len(descripcion.strip()) >= LARGO_MINIMO_DESCRIPCION
