"""
Script para cargar datos del Plan Financiero desde Excel
Ejecutar con: python cargar_excel.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pandas as pd
from decimal import Decimal
from datetime import date
from django.contrib.auth.models import User
from planfinanciero.models import (
    OrganoEjecutor, IngresoAgregado, TipoIngreso, Rubro, Movimiento, Vigencia
)

# Archivo Excel
EXCEL_FILE = 'PLAN FINANCIERO 2026.xlsx'


def limpiar_texto(texto):
    """Limpia y normaliza texto"""
    if pd.isna(texto):
        return None
    texto = str(texto).strip()
    # Corregir caracteres mal codificados
    texto = texto.replace('�', 'í').replace('á', 'á').replace('é', 'é')
    texto = texto.replace('ó', 'ó').replace('ú', 'ú').replace('ñ', 'ñ')
    return texto if texto else None


def crear_catalogos():
    """Crear catálogos base"""
    print("=== Creando catálogos ===")

    # Órganos Ejecutores
    organos = [
        'DESPACHO Y SECRETARIAS', 'FONDO EDUCACION', 'FONDO SALUD',
        'FONDO SEGURIDAD', 'FONDO EDUCACION SUPERIOR', 'FONDO PENSIONES',
        'IDERMETA', 'INSTITUTO CULTURA', 'INST ITUTO TURISMO',
        'INSTITUTO TRANSITO', 'UNIDAD LICORES', 'CASA CULTURA', 'AIM'
    ]
    for nombre in organos:
        obj, created = OrganoEjecutor.objects.get_or_create(
            codigo=nombre.replace(' ', '_')[:50],
            defaults={'nombre': nombre}
        )
        if created:
            print(f"  Órgano creado: {nombre}")

    # Ingresos Agregados (Fuentes)
    ingresos = [
        ('ICDE', 'Ingresos Corrientes de Destinación Específica'),
        ('ICLD 1', 'Ingresos Corrientes de Libre Destinación 1'),
        ('ICLD 2', 'Ingresos Corrientes de Libre Destinación 2'),
        ('ESTAMPILLAS', 'Estampillas'),
        ('SGP', 'Sistema General de Participaciones'),
        ('COFINANCIACION', 'Cofinanciación'),
        ('CREDITO', 'Crédito'),
        ('REGALIAS', 'Regalías'),
        ('ICDE SALUD', 'ICDE Salud'),
    ]
    for codigo, nombre in ingresos:
        obj, created = IngresoAgregado.objects.get_or_create(
            codigo=codigo,
            defaults={'nombre': nombre}
        )
        if created:
            print(f"  Ingreso Agregado creado: {codigo}")

    # Tipos de Ingreso
    tipos = [
        'TRIBUTARIO', 'NO TRIBUTARIO', 'EXCEDENTES', 'DIVIDENDOS',
        'RENDIMIENTOS', 'CREDITO', 'CANC RESERVAS', 'SUPERAVIT',
        'REINTEGROS', 'OTROS RK', 'TRANSF K', 'REC CARTERA',
        'RET FONPET', 'SUPERAVIT FISCAL'
    ]
    for nombre in tipos:
        obj, created = TipoIngreso.objects.get_or_create(
            codigo=nombre,
            defaults={'nombre': nombre}
        )
        if created:
            print(f"  Tipo Ingreso creado: {nombre}")

    # Vigencia 2026
    vigencia, created = Vigencia.objects.get_or_create(
        ano=2026,
        defaults={'activa': True, 'fecha_apertura': date(2026, 1, 1)}
    )
    if created:
        print("  Vigencia 2026 creada")


def cargar_rubros_y_presupuesto(df, admin_user):
    """Carga rubros y presupuesto inicial desde el DataFrame"""
    print("\n=== Cargando rubros y presupuesto inicial ===")

    rubros_creados = 0
    movimientos_creados = 0
    rubros_dict = {}  # Para guardar referencias

    for idx, row in df.iterrows():
        # Saltar filas de encabezado
        if idx < 4:
            continue

        codigo_pptal = limpiar_texto(row[7])  # Columna H - CODIGO PPTAL
        nombre = limpiar_texto(row[9])  # Columna J - CONCEPTO DEL INGRESO
        valor = row[10]  # Columna K - Valor 2026

        if not codigo_pptal or not nombre:
            continue

        # Limpiar código
        codigo_pptal = codigo_pptal.strip()

        # Determinar si es totalizador o detalle
        nivel = limpiar_texto(row[1])  # Columna B - NIVEL
        organo = limpiar_texto(row[2])  # Columna C - ORGANO EJECUTOR
        ingreso_agr = limpiar_texto(row[4])  # Columna E - INGRESO AGREGADO
        clase = limpiar_texto(row[5])  # Columna F - CLASE INGRESO
        tipo_ing = limpiar_texto(row[6])  # Columna G - TIPO INGRESO
        fuente = limpiar_texto(row[8])  # Columna I - FUENTE

        es_detalle = nivel in ['AC', 'EP'] and organo is not None

        # Buscar o crear rubro
        try:
            rubro = Rubro.objects.get(codigo=codigo_pptal)
        except Rubro.DoesNotExist:
            rubro = Rubro(
                codigo=codigo_pptal,
                nombre=nombre,
                es_totalizador=not es_detalle,
                activo=True,
                creado_por=admin_user
            )

            if es_detalle:
                rubro.nivel = nivel
                if organo:
                    rubro.organo_ejecutor = OrganoEjecutor.objects.filter(nombre=organo).first()
                if ingreso_agr:
                    rubro.ingreso_agregado = IngresoAgregado.objects.filter(codigo=ingreso_agr).first()
                if clase:
                    rubro.clase_ingreso = clase.upper()
                if tipo_ing:
                    rubro.tipo_ingreso = TipoIngreso.objects.filter(codigo=tipo_ing).first()
                if fuente:
                    rubro.codigo_fuente = fuente

            rubro.save()
            rubros_creados += 1
            rubros_dict[codigo_pptal] = rubro

            if rubros_creados % 50 == 0:
                print(f"  Rubros creados: {rubros_creados}")

        # Crear movimiento de presupuesto inicial si es rubro de detalle y tiene valor
        try:
            valor_float = float(valor) if pd.notna(valor) and str(valor).strip() else 0
        except (ValueError, TypeError):
            valor_float = 0

        if es_detalle and valor_float > 0:
            mov, created = Movimiento.objects.get_or_create(
                rubro=rubro,
                tipo='INICIAL',
                numero_ajuste=0,
                defaults={
                    'fecha': date(2026, 1, 1),
                    'documento_soporte': 'Ordenanza PF 2026',
                    'valor': Decimal(str(valor_float)),
                    'observaciones': 'Presupuesto inicial cargado desde Excel',
                    'registrado_por': admin_user
                }
            )
            if created:
                movimientos_creados += 1

    print(f"\n  Total rubros creados: {rubros_creados}")
    print(f"  Total movimientos iniciales: {movimientos_creados}")

    return rubros_dict


def establecer_jerarquia():
    """Establece la jerarquía de rubros basada en los códigos"""
    print("\n=== Estableciendo jerarquía de rubros ===")

    rubros = Rubro.objects.all().order_by('codigo')
    actualizados = 0

    for rubro in rubros:
        # Buscar padre basado en el código
        # El código tiene formato: 0301 - 1.1.01.02.100.01 - 14
        codigo = rubro.codigo

        # Extraer la parte jerárquica (entre los guiones)
        partes = codigo.split(' - ')
        if len(partes) >= 2:
            prefijo = partes[0]  # 0301
            jerarquia = partes[1] if len(partes) >= 2 else ''

            # Buscar padre quitando el último nivel
            if '.' in jerarquia:
                padre_jerarquia = '.'.join(jerarquia.split('.')[:-1])
                codigo_padre = f"{prefijo} - {padre_jerarquia}"

                padre = Rubro.objects.filter(codigo=codigo_padre).first()
                if padre and padre != rubro and rubro.padre != padre:
                    rubro.padre = padre
                    rubro.save(update_fields=['padre'])
                    actualizados += 1

    print(f"  Rubros con padre establecido: {actualizados}")


def main():
    print("=" * 60)
    print("CARGA DE DATOS DEL PLAN FINANCIERO 2026")
    print("=" * 60)

    # Verificar archivo
    if not os.path.exists(EXCEL_FILE):
        print(f"ERROR: No se encontró el archivo {EXCEL_FILE}")
        sys.exit(1)

    # Obtener o crear usuario admin
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', 'admin@planfinanciero.com', 'admin123')
        print("Usuario admin creado")

    # Limpiar datos anteriores
    print("\nLimpiando datos anteriores...")
    Movimiento.objects.all().delete()
    Rubro.objects.all().delete()
    print("  Datos limpiados")

    # Crear catálogos
    crear_catalogos()

    # Leer Excel
    print("\n=== Leyendo archivo Excel ===")
    xlsx = pd.ExcelFile(EXCEL_FILE)

    # Cargar PF INICIAL
    print("\nProcesando hoja: PF INICIAL")
    df_inicial = pd.read_excel(xlsx, sheet_name='PF INICIAL', header=None)
    rubros_dict = cargar_rubros_y_presupuesto(df_inicial, admin_user)

    # Establecer jerarquía
    establecer_jerarquia()

    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN DE CARGA")
    print("=" * 60)
    print(f"Órganos Ejecutores: {OrganoEjecutor.objects.count()}")
    print(f"Ingresos Agregados: {IngresoAgregado.objects.count()}")
    print(f"Tipos de Ingreso: {TipoIngreso.objects.count()}")
    print(f"Rubros totales: {Rubro.objects.count()}")
    print(f"  - Totalizadores: {Rubro.objects.filter(es_totalizador=True).count()}")
    print(f"  - Detalle: {Rubro.objects.filter(es_totalizador=False).count()}")
    print(f"Movimientos: {Movimiento.objects.count()}")

    # Calcular totales
    from django.db.models import Sum
    total = Movimiento.objects.filter(tipo='INICIAL').aggregate(Sum('valor'))['valor__sum']
    print(f"\nPresupuesto Total Cargado: ${total:,.0f}" if total else "Sin movimientos")

    print("\n¡Carga completada exitosamente!")


if __name__ == '__main__':
    main()
