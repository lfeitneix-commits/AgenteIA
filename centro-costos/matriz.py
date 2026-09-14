# -*- coding: utf-8 -*-
# ============================================================================
# ⚠️  FOTO DE UN MOMENTO DADO, NO LA MATRIZ "EN VIVO".
#
# Estos % son los que traía el CSV de la Matriz de gastos que el usuario pasó
# por chat. Este entorno NO tiene salida de red a Google Sheets (confirmado
# con curl y con la tool de fetch web: EGRESS_BLOCKED a docs.google.com), así
# que no hay forma de refrescarlos solo. La Matriz de gastos es una hoja que
# el usuario edita directamente -> estos números pueden estar desactualizados
# en cualquier momento futuro.
#
# SNAPSHOT_DATE = última vez que se confirmaron estos valores.
#
# Regla obligatoria antes de usar esto para un cálculo que importe de verdad
# (no solo una prueba): NO asumir que siguen vigentes. Preguntarle al usuario
# "¿la Matriz sigue igual a la del {SNAPSHOT_DATE}, o cambió algo?" y, si
# cambió, pedirle el CSV actualizado y volver a generar este archivo antes de
# calcular nada.
#
# FUENTE (pestaña "Matriz de gastos" del Sheet "Resultados por área 2026",
# mismo gid que MATRIZ_GID en el index.html de dashboard-rentabilidad):
# https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4gdsYZTOZlI1jllNuQ2mBWBjabHVL5vJ9dPGVso5lnUVOOuRsQ_xhKVfa0XYDlKpPGr61FUnO3kvy/pub?output=csv&gid=44234235
# ============================================================================
SNAPSHOT_DATE = '2026-09'  # mes en que el usuario pasó este CSV por última vez

# Claves = nombre exacto de cuenta. Valores = (Mesa, FAs+Mza, Banca
# Corporativa, Banca Privada) en fracción (no %).

def pct(m, f, bc, bp):
    return {'Mesa': m/100, 'FAs': f/100, 'Banca Corporativa': bc/100, 'Banca Privada': bp/100}

PRIMERA_MATRIZ = {  # por área INTERNA (staff) -> reparto a las 4 áreas de negocio
    'Back Office': pct(60, 30, 5, 5),
    'RRHH': pct(58, 14, 17, 11),
    'IT': pct(58, 14, 17, 11),
    'Administración': pct(58, 14, 17, 11),
    'MKTG': pct(16, 59, 12, 14),
    'Performance': pct(8, 57, 16, 19),
    # 'General' no tiene fila propia en la Matriz -> se usa el default de headcount (con flag)
}
HEADCOUNT_DEFAULT = pct(58, 14, 17, 11)

CUENTA_PCT = {
    'Gastos generales': pct(58,14,17,11), 'Librería y papelería': pct(58,14,17,11),
    'Refrigerios y cafetería': pct(58,14,17,11),
    'Certificaciones y legalización': pct(20,20,20,42),
    'Gtos Mant de Oficina': pct(58,14,17,11), 'Correspondencia y Mensajería': pct(58,14,17,11),
    'Gastos generales TC': pct(58,14,17,11), 'Mantenimiento Bs Uso': pct(58,14,17,11),
    'Mantenim Auto': pct(58,14,17,11), 'Útiles y Elementos de Oficina': pct(58,14,17,11),
    'Alquileres y expensas': pct(58,14,17,11), 'Adicional Obra Social': pct(58,14,17,11),
    'Electricidad': pct(58,14,17,11), 'Telefonía e Internet': pct(58,14,17,11),
    'Tasa CNV': pct(1,74,10,14), 'Tecnología y Software': pct(58,14,17,11),
    'Movilidad y viajes': pct(58,14,17,11), 'Membresías/Regulatorio': pct(1,74,10,14),
    'Administración/Consultoría': pct(58,14,17,11),
    'Intereses y multas impositivos': pct(1,74,10,14), 'Gastos bancarios': pct(1,74,10,14),
    'Gastos financieros': pct(1,74,10,14), 'Seguros': pct(58,14,17,11),
    'Representación': pct(1,74,10,14), 'Afters y eventos': pct(58,14,17,11),
    'Donaciones': pct(25,25,25,25), 'Honorarios Profesionales': pct(58,14,17,11),
    'Honorarios por Servicios': pct(58,14,17,11), 'Gastos Director Titular Autónomo': pct(58,14,17,11),
    'Gastos Corresp. Ext. u$s': pct(60,30,5,5),
    'Ingresos Brutos': pct(60,34,4,2), 'Impuesto Ley 25413': pct(60,34,4,2),
    'IVA no computable': pct(60,34,4,2), 'Imp. Bs. Part. Accionaria': pct(60,34,4,2),
    'Impuesto a los Sellos': pct(60,34,4,2), 'Impuestos Municiaples, Tasas': pct(60,34,4,2),
    'Otros Impuestos': pct(60,34,4,2),
    'Página Web/Publicidad/Merchandising': pct(16,59,12,14),
    'Serv Contratados BC (Marina Muller)': pct(0,20,10,70),
    'Gtos trad': pct(0,80,20,0),
    'Ingresos/egresos varios': pct(58,14,17,11),
}
