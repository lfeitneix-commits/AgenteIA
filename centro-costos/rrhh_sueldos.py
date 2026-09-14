# -*- coding: utf-8 -*-
# ⚠️  Dato real de RRHH pero incompleto: solo Enero-Junio. Julio/Agosto usan
# el promedio de estos 6 meses como supuesto (ver rrhh_pct_for_month) hasta
# que RRHH pase esos meses -- reemplazar apenas estén.
# Totales mensuales por área interna, tal como los pasó RRHH (columna TOTAL de cada bloque).
# Mes: 1=Enero .. 6=Junio (el CSV no trae Jul/Ago todavía).
RRHH_TOTAL = {
 '1': {'Mesa':107842749.99,'Banca Privada':18825996.24,'Banca Corporativa':34477686.59,'Middle Office':18870792.25,
       'Operaciones':60656660.32,'Administración':16387909.41,'RRHH':11213181.54,'Tecnología':43781277.96,
       'General':6404897.60,'Marketing':4795333.13,'Performance':12125000.00},
 '2': {'Mesa':130229440.59,'Banca Privada':21961888.26,'Banca Corporativa':38030956.85,'Middle Office':24000913.15,
       'Operaciones':64880128.68,'Administración':23618315.97,'RRHH':11658810.94,'Tecnología':47064025.60,
       'General':6818750.10,'Marketing':5222855.66,'Performance':12488379.31},
 '3': {'Mesa':105193280.71,'Banca Privada':22115909.23,'Banca Corporativa':32789623.23,'Middle Office':21665722.50,
       'Operaciones':60277604.84,'Administración':21353526.31,'RRHH':11194011.03,'Tecnología':38314779.73,
       'General':6432583.32,'Marketing':5179271.47,'Performance':12078359.31},
 '4': {'Mesa':132525446.39,'Banca Privada':25763085.69,'Banca Corporativa':35240821.08,'Middle Office':26744525.39,
       'Operaciones':73293005.10,'Administración':25785703.63,'RRHH':13194878.55,'Tecnología':55672635.74,
       'General':5919139.86,'Marketing':6584093.66,'Performance':14254543.86},
 '5': {'Mesa':132525446.39,'Banca Privada':29479108.86,'Banca Corporativa':39985554.25,'Middle Office':39244525.40,
       'Operaciones':73293005.10,'Administración':25785703.63,'RRHH':13118179.07,'Tecnología':55672635.74,
       'General':6710966.73,'Marketing':6584093.66,'Performance':14254543.86},
 '6': {'Mesa':201011468.73,'Banca Privada':38595164.05,'Banca Corporativa':35397181.51,'Middle Office':53657975.95,
       'Operaciones':104768837.19,'Administración':38172139.91,'RRHH':16333825.20,'Tecnología':72247907.84,
       'General':9067743.06,'Marketing':9855627.17,'Performance':21402808.93},
}

def rrhh_pct_for_month(mes):
    """Devuelve {area: fraccion} para el mes dado (str '1'..'8').
    Jul/Ago (7,8) no tienen dato de RRHH todavia -> se usa el promedio de Ene-Jun (supuesto, a confirmar)."""
    if mes in RRHH_TOTAL:
        row = RRHH_TOTAL[mes]
    else:
        # promedio simple de los 6 meses conocidos
        row = {}
        for area in RRHH_TOTAL['1']:
            row[area] = sum(RRHH_TOTAL[m][area] for m in RRHH_TOTAL) / len(RRHH_TOTAL)
    tot = sum(row.values())
    return {a: v / tot for a, v in row.items()}
