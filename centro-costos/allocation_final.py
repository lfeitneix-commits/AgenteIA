# -*- coding: utf-8 -*-
import json, unicodedata
from collections import defaultdict
from matriz import PRIMERA_MATRIZ as _PRIMERA_MATRIZ_SNAPSHOT, HEADCOUNT_DEFAULT as _HEADCOUNT_DEFAULT_SNAPSHOT, \
    CUENTA_PCT as _CUENTA_PCT_SNAPSHOT, SNAPSHOT_DATE
from roster import PERSON_INDEX
from rrhh_sueldos import rrhh_pct_for_month
import load_matriz_csv

# Preferir SIEMPRE centro-costos/matriz_gastos.csv si existe (lo sincroniza
# el Apps Script de la Matriz, o lo sube el usuario a mano) -- solo cae al
# snapshot hardcodeado de matriz.py si ese archivo todavía no existe.
_csv_primera_matriz, _csv_cuenta_pct = load_matriz_csv.load()
if _csv_primera_matriz is not None:
    PRIMERA_MATRIZ = _csv_primera_matriz
    CUENTA_PCT = _csv_cuenta_pct
    HEADCOUNT_DEFAULT = (PRIMERA_MATRIZ.get('RRHH') or PRIMERA_MATRIZ.get('IT')
                          or PRIMERA_MATRIZ.get('Administración') or _HEADCOUNT_DEFAULT_SNAPSHOT)
    print(f'[matriz] Usando {load_matriz_csv.CSV_PATH} (sincronizado desde la Matriz de gastos)')
else:
    PRIMERA_MATRIZ = _PRIMERA_MATRIZ_SNAPSHOT
    CUENTA_PCT = _CUENTA_PCT_SNAPSHOT
    HEADCOUNT_DEFAULT = _HEADCOUNT_DEFAULT_SNAPSHOT
    print(f'[matriz] matriz_gastos.csv no existe todavía -- usando el snapshot de matriz.py (SNAPSHOT_DATE={SNAPSHOT_DATE})')

d = json.load(open('quant_accounting.json'))
AREAS = ['Mesa', 'FAs', 'Banca Corporativa', 'Banca Privada']
result = defaultdict(float)          # área -> monto
flags = []                            # supuestos / cosas a confirmar
excluded = defaultdict(float)         # no erogables

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def norm(s):
    return strip_accents(s).lower().strip()

CUENTA_PCT_NORM = {norm(k): v for k, v in CUENTA_PCT.items()}
# nombres reales del export de contabilidad que no coinciden textualmente con la fila
# de la Matriz (además de acentos/mayúsculas, que ya cubre norm()) pero son la misma cuenta
ALIAS_CUENTA = {
    'merchandising': 'Página Web/Publicidad/Merchandising',
    'pagina web/publicidad': 'Página Web/Publicidad/Merchandising',
    'gtos grales tc corporativa': 'Gastos generales TC',
    'gastos mantenimiento bs. uso': 'Mantenimiento Bs Uso',
    'mantenimiento y gastos auto': 'Mantenim Auto',
    'impuestos municipales, tasas': 'Impuestos Municiaples, Tasas',  # typo tal cual está en la Matriz
    'iva no computable': 'IVA no computable',
    'alquileres y expensas neix': 'Alquileres y expensas',
    'alquileres y expensas': 'Alquileres y expensas',
    'gastos bancarios 10,5%': 'Gastos bancarios',
    'gastos bancarios exentos': 'Gastos bancarios',
    'int. desc bcario': 'Gastos bancarios',
    'impuestos a los sellos': 'Impuesto a los Sellos',
    'gastos director titular autono': 'Gastos Director Titular Autónomo',  # nombre truncado en el export
}
def cuenta_pct_lookup(n):
    if n in CUENTA_PCT:
        return CUENTA_PCT[n]
    nn = norm(n)
    if nn in CUENTA_PCT_NORM:
        return CUENTA_PCT_NORM[nn]
    if nn in ALIAS_CUENTA:
        return CUENTA_PCT[ALIAS_CUENTA[nn]]
    return None

def find_person(desc):
    dl = strip_accents(desc).lower()
    hits = []
    for variant, entries in PERSON_INDEX.items():
        if variant in dl:
            hits.extend(entries)
    return hits

# alias área interna (roster/Sueldos-CS) -> nombre de fila en 'primera matriz'
INTERNA_ALIAS = {'Operaciones': 'Back Office', 'Tecnología': 'IT', 'Back Office': 'Back Office',
                 'IT': 'IT', 'Administración': 'Administración', 'RRHH': 'RRHH',
                 'MKTG': 'MKTG', 'Marketing': 'MKTG', 'Performance': 'Performance'}
# área de negocio (roster) -> columna final
NEGOCIO_ALIAS = {'Mesa': 'Mesa', 'Banca Corporativa': 'Banca Corporativa', 'Banca Privada': 'Banca Privada',
                 'Middle Office': 'FAs'}

def total(acc):
    return sum(acc['m'].values())

def add(area, monto):
    result[area] += monto

def apply_pct(monto, pcts):
    for area, frac in pcts.items():
        add(area, monto * frac)

def txns_of(code):
    acc = d[code]
    out = []
    for mes, lst in acc.get('d', {}).items():
        for t in lst:
            out.append((mes, *t))
    return out

NO_EROGABLE = {'Amortizaciones', 'Diferencia de Redondeo', 'Diferencia cambio u$s (Pesos)', 'RECPAM',
               'D/C por Cambio', 'Impuesto a las ganancias'}   # esta última: confirmado como provisión, se excluye

MESA_NETO = {'Gastos Caja de Valores', 'Gastos A3 Mercados', 'Gastos Byma', 'Gastos Mae',
             'Gastos Caja de Valores Exento', 'Gastos Byma Op. fuera Horario',
             'Gtos Alq Comitentes', 'Intereses Pagados'}

DIRECT_SECTOR = {'Mesa': 'Mesa', 'Banca Corporativa': 'Banca Corporativa', 'Banca Privada': 'Banca Privada',
                  'Productores': 'FAs', 'Oficina Mendoza': 'FAs'}

# cuentas con sufijo de área interna que se reparten por 'primera matriz' (según el área que indica el sufijo)
SUFIJO_INTERNO = {'Adm': 'Administración', 'RRHH': 'RRHH', 'MKTG': 'MKTG', 'IT': 'IT', 'Back': 'Back Office',
                  'General': None, 'Performance': 'Performance'}

def dept_from_name(n):
    for suf, dept in SUFIJO_INTERNO.items():
        if n.endswith(' ' + suf) or n.endswith(suf):
            return dept, suf
    return None, None

TECH_KWS = ['adobe','nss s.a','microsoft','github','gibhub','slack','digital ocean','lanbot','mailchimp','z gastos']
MEMB_KWS = ['byma','camara de agent','bolsa de comercio','cfa institute','encode s.a','certi firma digit']
OFICINA_KWS = ['limpieza','alarma','seguridad','isikawa','star servicios']
ADMIN_KWS = ['interbanking','consultora','contable','auditoria','estudio','gimenez ezequie']
NUBI_KWS = ['nubi', 'nuby']

# ------------------------------------------------------------------
for code, acc in d.items():
    n, s, tot = acc['n'], acc['s'], total(acc)
    if tot == 0:
        continue

    if n in NO_EROGABLE:
        excluded[n] += tot
        continue

    if n in MESA_NETO:
        add('Mesa', tot)
        continue

    if n in ('Sueldos', 'Cargas Sociales', 'Vacaciones'):
        # Viene 100% sin discriminar en contabilidad -> se reparte con el % real
        # que pasó RRHH por área y mes (Sueldos y CS). Jul/Ago (sin dato de RRHH
        # todavía) usan el promedio Ene-Jun -- supuesto, a confirmar.
        for mes, monto in acc['m'].items():
            rrhh_pct = rrhh_pct_for_month(mes)
            if mes not in ('1','2','3','4','5','6'):
                flags.append((code, n, f'mes {mes}: sin dato RRHH -> promedio Ene-Jun', monto))
            for area_interna, frac in rrhh_pct.items():
                sub_monto = monto * frac
                if area_interna in NEGOCIO_ALIAS:
                    add(NEGOCIO_ALIAS[area_interna], sub_monto)
                else:
                    apply_pct(sub_monto, PRIMERA_MATRIZ.get(INTERNA_ALIAS.get(area_interna), HEADCOUNT_DEFAULT))
        continue

    if n == 'Eventos Empresariales':
        for mes, fecha, cpte, desc, monto in txns_of(code):
            hits = find_person(desc)
            areas = set(h[1] for h in hits)
            if len(areas) == 1:
                a = areas.pop()
                add(NEGOCIO_ALIAS.get(a) or 'Mesa', monto) if a in NEGOCIO_ALIAS else apply_pct(monto, CUENTA_PCT['Representación'])
            else:
                apply_pct(monto, CUENTA_PCT['Representación'])  # eventos genéricos, sin persona identificable
        continue

    if n in ('Gastos de Viajes Neix', 'Viaticos y Mov. Neix'):
        for mes, fecha, cpte, desc, monto in txns_of(code):
            dl = strip_accents(desc).lower()
            hits = find_person(desc)
            areas = set(h[1] for h in hits)
            if 'mdz' in dl or 'mendoza' in dl:
                add('FAs', monto)
            elif len(areas) == 1 and list(areas)[0] in NEGOCIO_ALIAS:
                add(NEGOCIO_ALIAS[list(areas)[0]], monto)
            else:
                apply_pct(monto, CUENTA_PCT['Movilidad y viajes'])  # default: headcount
        continue

    if n == 'Gastos Representacion Neix':
        for mes, fecha, cpte, desc, monto in txns_of(code):
            hits = find_person(desc)
            areas = set(h[1] for h in hits)
            if len(areas) == 1 and list(areas)[0] in NEGOCIO_ALIAS:
                add(NEGOCIO_ALIAS[list(areas)[0]], monto)
            else:
                apply_pct(monto, CUENTA_PCT['Representación'])  # eventos genéricos -> Marketing/Representación
        continue

    if n == 'Capacit. y Cursos Neix':
        for mes, fecha, cpte, desc, monto in txns_of(code):
            hits = find_person(desc)
            areas = set(h[1] for h in hits)
            if len(areas) == 1:
                a = list(areas)[0]
                if a in NEGOCIO_ALIAS:
                    add(NEGOCIO_ALIAS[a], monto)
                elif a in INTERNA_ALIAS:
                    apply_pct(monto, PRIMERA_MATRIZ.get(INTERNA_ALIAS[a], HEADCOUNT_DEFAULT))
            else:
                apply_pct(monto, HEADCOUNT_DEFAULT)
                flags.append((code, n, 'sin persona identificada -> default headcount', monto))
        continue

    if n == 'Suscripciones Neix':
        for mes, fecha, cpte, desc, monto in txns_of(code):
            dl = desc.lower()
            if any(k in dl for k in TECH_KWS):
                apply_pct(monto, CUENTA_PCT['Tecnología y Software'])
            elif any(k in dl for k in MEMB_KWS):
                apply_pct(monto, CUENTA_PCT['Membresías/Regulatorio'])
            else:
                apply_pct(monto, HEADCOUNT_DEFAULT)
                flags.append((code, n, 'sin proveedor legible -> default headcount', monto))
        continue

    if n == 'Serv. Contratados Neix':
        for mes, fecha, cpte, desc, monto in txns_of(code):
            dl = desc.lower()
            if any(k in dl for k in NUBI_KWS):
                continue  # ya está en Sueldos, no sumar de nuevo
            if 'petracchi' in dl:
                add('FAs', monto)
            elif any(k in dl for k in OFICINA_KWS):
                apply_pct(monto, CUENTA_PCT['Gtos Mant de Oficina'])
            elif any(k in dl for k in ADMIN_KWS):
                apply_pct(monto, CUENTA_PCT['Administración/Consultoría'])
            else:
                apply_pct(monto, HEADCOUNT_DEFAULT)
                flags.append((code, n, 'proveedor no identificado -> default headcount', monto))
        continue

    if n == 'Gtos Hardw y Comp Neix':
        apply_pct(tot, HEADCOUNT_DEFAULT)
        flags.append((code, n, 'catch-all sin depto propio -> default headcount', tot))
        continue

    if n == 'Hon. Profesionales Neix':
        apply_pct(tot, CUENTA_PCT['Honorarios Profesionales'])
        continue

    if s in DIRECT_SECTOR:
        add(DIRECT_SECTOR[s], tot)
        continue

    dept, suf = dept_from_name(n)
    # familias que se reparten por área interna vía primera matriz
    if dept is not None and any(n.startswith(fam) for fam in
                     ['Suscripciones', 'Sueldos y CS', 'Gtos Hardw y Comp', 'Viaticos y Mov.',
                      'Serv. Contratados', 'Gastos Representacion', 'Hon. Profesionales',
                      'Capacit. y Cursos', 'Capacitacion y Cursos']):
        apply_pct(tot, PRIMERA_MATRIZ.get(dept, HEADCOUNT_DEFAULT))
        continue
    if suf == 'General' and any(n.startswith(fam) for fam in
                     ['Suscripciones', 'Sueldos y CS', 'Gtos Hardw y Comp', 'Viaticos y Mov.',
                      'Serv. Contratados', 'Gastos Representacion', 'Hon. Profesionales',
                      'Capacit. y Cursos', 'Capacitacion y Cursos']):
        apply_pct(tot, HEADCOUNT_DEFAULT)
        flags.append((code, n, '"General" sin fila propia en Matriz -> default headcount', tot))
        continue

    found_pct = cuenta_pct_lookup(n)
    if found_pct:
        apply_pct(tot, found_pct)
        continue

    flags.append((code, n, 'SIN REGLA -> no incluido', tot))

# ------------------------------------------------------------------
print('='*60)
print('RESULTADO FINAL POR ÁREA (Ene-Ago 2026)')
print('='*60)
grand = sum(result.values())
for a in AREAS:
    print(f'  {a:20s} {result[a]:>18,.2f}   ({result[a]/grand*100:5.1f}%)')
print(f'  {"TOTAL":20s} {grand:>18,.2f}')

print()
print('EXCLUIDO (no erogable):')
for k, v in excluded.items():
    print(f'  {k:35s} {v:>18,.2f}')

print()
print(f'FLAGS / SUPUESTOS APLICADOS ({len(flags)}):')
by_reason = defaultdict(float)
for code, n, reason, monto in flags:
    by_reason[(n, reason)] += monto
for (n, reason), v in sorted(by_reason.items(), key=lambda x: -x[1]):
    print(f'  {n:30s} | {reason:55s} {v:>14,.2f}')
