from datetime import date, datetime
from decimal import Decimal

def calcular_depreciacion_actual(valor_original, tasa_anual, fecha_ingreso):
    """
    Calcula dinámicamente la depreciación acumulada y el valor contable actual.
    Soporta fechas en formato string 'YYYY-MM-DD' o como objetos date de Python.
    """
    if not valor_original or tasa_anual is None or not fecha_ingreso:
        return {'acumulada': 0.0, 'valor_actual': 0.0, 'meses': 0}

                                                                                  
    valor = Decimal(str(valor_original))
    tasa = Decimal(str(tasa_anual))
    
                                                                                                           
    if tasa > 1:
        tasa = tasa / Decimal('100')

                                                                   
    if isinstance(fecha_ingreso, str):
        try:
            fecha_ing = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()
        except ValueError:
                                                                 
            fecha_ing = datetime.strptime(fecha_ingreso, '%Y-%m-%d %H:%M:%S').date()
    else:
        fecha_ing = fecha_ingreso

                                                         
    hoy = date.today()
    meses = (hoy.year - fecha_ing.year) * 12 + hoy.month - fecha_ing.month

                                                                                      
    if meses <= 0:
        return {
            'acumulada': 0.00,
            'valor_actual': float(valor.quantize(Decimal('0.01'))),
            'meses': 0
        }

                                                       
    depreciacion_mensual = (valor * tasa) / Decimal('12')
    acumulada = (depreciacion_mensual * Decimal(str(meses))).quantize(Decimal('0.01'))

                                                                  
    if acumulada > valor:
        acumulada = valor

    valor_actual = (valor - acumulada).quantize(Decimal('0.01'))

    return {
        'acumulada': float(acumulada),
        'valor_actual': float(valor_actual),
        'meses_uso': meses
    }