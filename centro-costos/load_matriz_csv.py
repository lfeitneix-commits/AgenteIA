# -*- coding: utf-8 -*-
"""
Si existe centro-costos/matriz_gastos.csv (sincronizado por el Apps Script
de la Matriz de gastos, o subido a mano), lo parsea y devuelve los mismos
PRIMERA_MATRIZ / CUENTA_PCT que matriz.py -- para que allocation_final.py
use SIEMPRE el archivo del repo si está, en vez del snapshot hardcodeado.

Formato esperado (el mismo que exporta Google Sheets como CSV, con la
sección de "primera matriz" arriba, la sección "Cuentas" en el medio, y
"CÁLCULOS AUX" al final -- esta última no se usa acá, es solo referencia
para quien arme la hoja).
"""
import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), 'matriz_gastos.csv')

PRIMERA_MATRIZ_NAMES = {'Back Office', 'RRHH', 'IT', 'Administración', 'MKTG', 'Performance'}


def _pct_row(row):
    def f(v):
        v = (v or '').strip().replace('%', '')
        return float(v) / 100 if v else 0.0
    return {'Mesa': f(row[1]), 'FAs': f(row[2]), 'Banca Corporativa': f(row[3]), 'Banca Privada': f(row[4])}


def load():
    """Devuelve (primera_matriz, cuenta_pct) o (None, None) si no hay CSV."""
    if not os.path.exists(CSV_PATH):
        return None, None

    with open(CSV_PATH, encoding='utf-8') as f:
        rows = list(csv.reader(f))

    primera_matriz = {}
    cuenta_pct = {}
    in_cuentas_section = False

    for row in rows:
        if not row or not any(c.strip() for c in row):
            continue
        name = row[0].strip()
        if name.lower().startswith('cuentas'):
            in_cuentas_section = True
            continue
        if name.upper().startswith('CÁLCULOS AUX') or name.upper().startswith('CALCULOS AUX'):
            break  # el resto es la sección de referencia (headcount/comitentes/facturación), no reparto
        if name in ('Mesa', 'Concepto') or row[1].strip() == 'Mesa':
            continue  # fila de encabezado repetida
        if len(row) < 5:
            continue
        if not in_cuentas_section and name in PRIMERA_MATRIZ_NAMES:
            primera_matriz[name] = _pct_row(row)
        elif in_cuentas_section:
            cuenta_pct[name] = _pct_row(row)

    return primera_matriz, cuenta_pct


if __name__ == '__main__':
    pm, cp = load()
    if pm is None:
        print(f'No existe {CSV_PATH} todavía -- se sigue usando el snapshot de matriz.py.')
    else:
        print(f'Leído {CSV_PATH}: {len(pm)} filas de "primera matriz", {len(cp)} cuentas.')
