# -*- coding: utf-8 -*-
# ⚠️  FOTO DE UN MOMENTO DADO (snapshot 2026-09), no el roster "en vivo" de
# RRHH. La gente entra, sale y cambia de área -> antes de un cálculo que
# importe de verdad, confirmar con el usuario si esto sigue vigente.
SNAPSHOT_DATE = '2026-09'
# Nota: Pedro Perez Marexiano figura acá en Middle Office porque esa fue su
# área durante Ene-Ago 2026 (el período ya calculado); en la realidad actual
# pasó a Mesa. Si se recalcula un período posterior a su cambio de área, hay
# que moverlo a Mesa en este diccionario.
ROSTER = {
'Operaciones': ['Silvia Olid','Yessica Ramos','Nadia Bernal','Sebastián Fernandez Molas','Cecilia Berardi',
    'Roberto Guerrierri','Maximo Casero','Tomas Troncar','Lucas Aristi','Lucas de Abelleyra',
    'Millie Urrere Pon','Lucila Lazcano','Valentina Cheloni','Oliver Hassel','Valentin Flores Pueyo','Vanesa Aquino'],
'Mesa': ['Nicolas Olivares','Pablo Sanches','Ignacio Mendiberri','Luca Furlong','Pedro Romagnano',
    'Germán Nerenberg','Mora Benedit','Arturo Liva Besil','Juan Nagore','Agustín Latrechiana','Uriel Paluch',
    'Hernan Naccarato','Matias Febles','Germán Jurado','Camila Gallo García','Santiago Pivato',
    'Paola Nuñez Herrero','Guido Schifani','Juan Cruz Miranda'],
'Administración': ['Sebastián Funes','Elsimar Ramirez','Sebastian Garone','Diego Cleriere','Agustina Marchese'],
'RRHH': ['Martina Perez Monti','Sofia Santangelo'],
'Banca Privada': ['Tomas Vodanovich','Lucas Malaccorto','Martina Degrossi','Nicanor Furlani'],
'Banca Corporativa': ['Brenda Merino','Marcelo Lipovetzky','Lucila Battaglia','Julían Gonzalez','Alvanny Viloria','Facundo Linares'],
'Middle Office': ['Franco Migliano','Manuela Conti','Soledad Sicouly','Manuela Depino','Jaime Santamarina','Pedro Perez Marexiano'],
'Tecnología': ['Emiliano Ghezzi','Martin Concettoni','Leonardo García','Iara Guglielmetti','Franco Catania',
    'Facundo Bustelo','Fabián Centurión','Juan Patricio Dugo','Esteban Sonaglioni'],
'General': ['Luna Feit','Catalina Cirio'],
'Marketing': ['Pilar Garat','Felicitas Gilges'],
'Performance': ['Santiago De Mario','Pilar Bottazzi'],
}

# área interna -> etiqueta usada en las cuentas contables (accounting sector / suffix)
AREA_ALIAS = {'Operaciones':'Back Office','Tecnología':'IT / Sistemas','Middle Office':'FAs/Prods'}

def name_variants(full_name):
    import unicodedata
    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    parts = full_name.split()
    variants = {strip_accents(full_name).lower()}
    if len(parts) >= 2:
        variants.add(strip_accents(parts[-1]).lower())          # apellido solo (último token)
        variants.add(strip_accents(' '.join(parts[:2])).lower())  # primeros 2 tokens
    return variants

PERSON_INDEX = {}  # variante de nombre (sin acentos, lower) -> (nombre completo, area)
for area, people in ROSTER.items():
    for p in people:
        for v in name_variants(p):
            if len(v) < 5:
                continue  # evita falsos positivos con apellidos muy cortos
            PERSON_INDEX.setdefault(v, []).append((p, area))
