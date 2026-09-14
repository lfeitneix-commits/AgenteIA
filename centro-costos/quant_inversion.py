# -*- coding: utf-8 -*-
"""
Inversión Quant (IT) — datos del "Informe de Gastos IT — Quant" que arma el
área de IT. NO es parte del motor de asignación por área (allocation_final.py
no lo usa) -- Quant es un gasto/proyecto aparte, no se reparte entre
Mesa/FAs/BC/BP. Vive acá como referencia estructurada, mismo patrón que
matriz.py/rrhh_sueldos.py: una FOTO de un informe puntual, no un dato en vivo.

Fuente: informe en PDF que pasa IT a mano cada vez que hay gastos nuevos --
no hay URL/gid para leer esto en vivo (a diferencia de la Matriz de gastos).
Para actualizar: pedirle a IT/al usuario el informe nuevo y reemplazar este
archivo entero (las categorías y subtotales pueden cambiar de un informe a
otro, no solo agregarse filas).
"""

SNAPSHOT_DATE = '2026-09'  # cuándo se cargó este informe acá

QUANT_META = {
    'periodo': 'Enero-Agosto 2026',
    'emision_informe': '26/06/2026',  # OJO: el propio informe trae esta fecha vieja
                                       # (es anterior al fin del período que dice cubrir,
                                       # 26/06 vs Ene-Ago) -- probablemente quedó sin
                                       # actualizar del informe anterior (Ene-Jun). No es
                                       # un error de carga, así viene el PDF.
    'destinatario': 'Lucas Mieres',
    'preparado_por': 'Área de IT',
    'nota': ('Este informe solo incluye los gastos gestionados directamente por IT y no '
             'contempla herramientas de inteligencia artificial (Codex), ni otros gastos '
             'administrados por Quant. Tampoco se incluyen las horas de trabajo del equipo '
             'de IT ni los recursos en infraestructura local de Neix consumidos por Quant, '
             'los cuales resultaron considerables durante el primer semestre de 2026, dado '
             'que más del 70% del esfuerzo en infraestructura fue destinado a Quant.'),
    'nota_ojo': ('La nota de arriba dice que NO contempla Codex, pero el Resumen Ejecutivo '
                 'de este mismo informe sí trae 2 líneas de gasto de Codex/OpenAI -- '
                 'contradicción del propio informe, probablemente la nota general quedó '
                 'vieja. Reportar los montos de Codex igual, tal como vienen.'),
}

# ---- 1. Hardware -----------------------------------------------------------
# Categoría -> lista de items {desc, fecha, monto (ARS), obs}. Los subtotales
# por categoría y el total general están confirmados contra el PDF.
QUANT_HARDWARE = {
    'PCs Completas': {
        'server_llm': [
            {'desc': 'Disco rígido', 'fecha': '18/03/26', 'monto': 1032885.07, 'obs': ''},
            {'desc': 'SSD WD — BKP', 'fecha': '18/03/26', 'monto': 92140.29, 'obs': ''},
            {'desc': 'Server LLM Quant', 'fecha': '20/03/26', 'monto': 10662669.68, 'obs': ''},
            {'desc': 'Server LLM Quant', 'fecha': '20/03/26', 'monto': 391571.70, 'obs': 'Factura complementaria'},
            {'desc': 'Water Cooler', 'fecha': '16/06/26', 'monto': 265222.28, 'obs': ''},
        ],
        'subtotal_server_llm': 12444489.02,
        'otros': [
            {'desc': 'PC Trading Algorítmico', 'fecha': '08/01/26', 'monto': 967954.75, 'obs': 'Camila García'},
            {'desc': 'Mini PC Router Colocation', 'fecha': 'May/26', 'monto': 1038872.00, 'obs': '2 unidades'},
            {'desc': 'PC Armada Intel', 'fecha': '29/05/26', 'monto': 1583701.36, 'obs': 'Santiago Pivato'},
            {'desc': 'Puesto adicional', 'fecha': '14/08/26', 'monto': 1330307.69, 'obs': 'Guido'},  # nuevo vs. informe Ene-Jun
            {'desc': 'Mini PC Quant', 'fecha': '27/07/26', 'monto': 719456.11, 'obs': ''},           # nuevo vs. informe Ene-Jun
        ],
        'subtotal_categoria': 18084780.93,
    },
    'Componentes para mejoras de equipos': {
        'items': [
            {'desc': 'Microprocesador', 'fecha': '08/01/26', 'monto': 212669.68, 'obs': 'PC Pruebas Quant'},
            {'desc': 'Memoria — Trading A', 'fecha': '16/01/26', 'monto': 174395.48, 'obs': 'PC Guadalupe Sierra'},
            {'desc': 'Disco y placa — Trad.', 'fecha': '23/01/26', 'monto': 196241.63, 'obs': 'PC Guadalupe Sierra'},
            {'desc': 'Memoria DDR4', 'fecha': '30/01/26', 'monto': 95587.33, 'obs': 'Notebook Paola Herrero'},
            {'desc': 'Disco Sólido', 'fecha': '03/02/26', 'monto': 136189.13, 'obs': 'PC Uriel Paluch'},
            {'desc': 'Fuente de PC', 'fecha': '06/03/26', 'monto': 68436.20, 'obs': 'PC Mesa Quant'},
            {'desc': 'Fuente de PC', 'fecha': '15/05/26', 'monto': 69502.26, 'obs': 'PC Pruebas Quant'},
            {'desc': 'Resto Factura Varios Quant 3/9/26', 'fecha': '03/09/26', 'monto': 2822979.75,
             'obs': 'Tvs, Soportes, Placas'},  # nuevo vs. informe Ene-Jun
        ],
        'subtotal_categoria': 3776001.46,
    },
    'Notebooks': {
        'items': [
            {'desc': 'Notebook Paola Núñez Herrero', 'fecha': '27/01/26', 'monto': 1126600.07, 'obs': 'Cerramiento'},
            {'desc': '7x Notebooks Trading Algorítmico', 'fecha': '21/04/26', 'monto': 13750394.57, 'obs': 'Cerramiento'},
            {'desc': 'Notebook Santiago Pivato', 'fecha': '09/06/26', 'monto': 1583705.88, 'obs': 'Cerramiento'},
        ],
        'subtotal_categoria': 16460700.52,
    },
    'Monitores': {
        'items': [
            {'desc': 'TV 50" — Trading', 'fecha': '07/01/26', 'monto': 548123.97, 'obs': 'Agustín Latrechiana'},
            {'desc': 'TV 50" — Trading', 'fecha': '07/01/26', 'monto': 548123.97, 'obs': 'Matías Febles'},
        ],
        'subtotal_categoria': 1096247.94,
    },
    'Instalación Cámaras': {
        'items': [
            {'desc': 'Memorias Micro SD', 'fecha': '05/05/26', 'monto': 48866.97, 'obs': 'Memorias Cámaras Trading'},
            {'desc': 'Zapatillas eléctricas', 'fecha': '27/05/26', 'monto': 37884.30, 'obs': 'Zapatillas Instalación Cámaras'},
        ],
        'subtotal_categoria': 86751.27,
    },
}
QUANT_HARDWARE_TOTAL_ARS = 39504482.12  # "TOTAL HARDWARE" del PDF (Ene-Ago 2026)

# ---- 2. Servicios de infraestructura (costo mensual recurrente, USD) ------
# Sin cambios respecto al informe anterior (Ene-Jun) -- misma lista, mismos montos.
QUANT_SERVICIOS = {
    'nota': ('Los siguientes servicios se encuentran activos con facturación mensual '
             'recurrente, con excepción de Cirion que está en etapa de contratación.'),
    'rows': [
        {'servicio': 'Ancho de banda adicional (15 Mbps)', 'costo_usd': 375.00, 'desde': 'Mayo 2026',
         'obs': '15 Mbps × USD 25/Mbps — Colocation'},
        {'servicio': 'AWS', 'costo_usd': 170.00, 'desde': 'Ene 2026', 'obs': 'VPS'},
        {'servicio': 'Fibertel Colocation', 'costo_usd': 100.00, 'desde': 'Marzo 2026', 'obs': 'Enlace secundario'},
        {'servicio': 'Metrotel Colocation', 'costo_usd': 500.00, 'desde': 'Junio 2026',
         'obs': 'Enlace SLA (sube a USD 700/mes a partir de 2027)'},
        {'servicio': 'Beeks', 'costo_usd': 360.00, 'desde': 'Ene 2026', 'obs': 'VPS'},
        {'servicio': 'Colocation BYMA', 'costo_usd': 2048.00, 'desde': 'Ene 2026', 'obs': '½ rack en BYMA'},
        {'servicio': 'Cirion Enlace', 'costo_usd': 700.00, 'desde': 'Proyectado',
         'obs': 'Enlace dedicado COLOCATION ↔ BEEKS (en proceso de instalación)'},
    ],
    'total_mensual_usd': 4253.00,
}

# ---- 3. Resumen ejecutivo (tal cual la tabla del PDF, mezcla ARS/USD) -----
QUANT_RESUMEN_EJECUTIVO = [
    {'concepto': 'Total Hardware adquirido en Pesos', 'importe': 39504482.12, 'moneda': 'ARS',
     'periodo': 'Ene-Ago 2026'},
    {'concepto': 'Obra - Oficina Quant', 'importe': 65877000.00, 'moneda': 'ARS', 'periodo': 'Por única vez'},
    {'concepto': 'Obra - Oficina Quant (Cámaras y controles de acceso)', 'importe': 2400.00, 'moneda': 'USD',
     'periodo': ''},  # nuevo vs. informe Ene-Jun
    {'concepto': 'Servicios de infraestructura', 'importe': 4253.00, 'moneda': 'USD',
     'periodo': 'Recurrente mensual (incluido Cirion)'},
    {'concepto': 'OpenAI – Codex (AMEX Administración)', 'importe': 36426.54, 'moneda': 'USD',
     'periodo': 'Acumulado (Marzo-Julio 2026)'},  # nuevo
    {'concepto': 'OpenAI – Codex (Suscripciones x 6)', 'importe': 1200.00, 'moneda': 'USD',
     'periodo': 'Recurrente mensual a partir de Agosto'},  # nuevo
    {'concepto': 'Placa FPGA', 'importe': 3464.00, 'moneda': 'USD', 'periodo': 'En Aduana'},  # nuevo
    {'concepto': 'Placa FPGA', 'importe': 2345.00, 'moneda': 'USD', 'periodo': 'En Camino'},  # nuevo
]

if __name__ == '__main__':
    hw_check = sum(cat['subtotal_categoria'] for cat in QUANT_HARDWARE.values())
    print(f'Suma de subtotales de categoría: {hw_check:,.2f} (PDF dice {QUANT_HARDWARE_TOTAL_ARS:,.2f})')
    assert abs(hw_check - QUANT_HARDWARE_TOTAL_ARS) < 1, 'No cierra contra el TOTAL HARDWARE del PDF'
    print('OK -- cierra.')
