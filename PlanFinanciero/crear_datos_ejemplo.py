"""
Script para crear datos de ejemplo en el sistema Plan Financiero
Ejecutar con: python manage.py shell < crear_datos_ejemplo.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from planfinanciero.models import FuenteFinanciacion, Rubro, Movimiento
from datetime import date
from decimal import Decimal

# Obtener o crear usuario admin
admin_user = User.objects.filter(username='admin').first()
if not admin_user:
    admin_user = User.objects.create_superuser('admin', 'admin@planfinanciero.com', 'admin123')
    print("Usuario admin creado")

# Crear Fuentes de Financiacion
fuentes_data = [
    {'codigo': 'ICLD', 'nombre': 'Ingresos Corrientes de Libre Destinacion', 'descripcion': 'Recursos propios del departamento de libre destinacion'},
    {'codigo': 'SGP', 'nombre': 'Sistema General de Participaciones', 'descripcion': 'Transferencias de la Nacion'},
    {'codigo': 'REG', 'nombre': 'Regalias', 'descripcion': 'Recursos del Sistema General de Regalias'},
    {'codigo': 'CRED', 'nombre': 'Recursos de Credito', 'descripcion': 'Recursos provenientes de operaciones de credito publico'},
    {'codigo': 'COOP', 'nombre': 'Cooperacion Internacional', 'descripcion': 'Recursos de cooperacion y donaciones internacionales'},
]

for f_data in fuentes_data:
    fuente, created = FuenteFinanciacion.objects.get_or_create(
        codigo=f_data['codigo'],
        defaults={'nombre': f_data['nombre'], 'descripcion': f_data['descripcion']}
    )
    if created:
        print(f"Fuente creada: {fuente.codigo}")

# Obtener fuentes
icld = FuenteFinanciacion.objects.get(codigo='ICLD')
sgp = FuenteFinanciacion.objects.get(codigo='SGP')
reg = FuenteFinanciacion.objects.get(codigo='REG')

# Crear Rubros de ejemplo
rubros_data = [
    {'codigo': '1.1.01.01', 'nombre': 'Impuesto Predial Unificado', 'fuente': icld, 'nivel': 'CENTRAL', 'tipo_recurso': 'CORRIENTE'},
    {'codigo': '1.1.01.02', 'nombre': 'Impuesto de Industria y Comercio', 'fuente': icld, 'nivel': 'CENTRAL', 'tipo_recurso': 'CORRIENTE'},
    {'codigo': '1.1.02.01', 'nombre': 'Sobretasa a la Gasolina', 'fuente': icld, 'nivel': 'CENTRAL', 'tipo_recurso': 'CORRIENTE'},
    {'codigo': '1.2.01.01', 'nombre': 'SGP Educacion', 'fuente': sgp, 'nivel': 'CENTRAL', 'tipo_recurso': 'CORRIENTE'},
    {'codigo': '1.2.01.02', 'nombre': 'SGP Salud', 'fuente': sgp, 'nivel': 'CENTRAL', 'tipo_recurso': 'CORRIENTE'},
    {'codigo': '1.2.01.03', 'nombre': 'SGP Proposito General', 'fuente': sgp, 'nivel': 'CENTRAL', 'tipo_recurso': 'CORRIENTE'},
    {'codigo': '1.3.01.01', 'nombre': 'Regalias Directas', 'fuente': reg, 'nivel': 'CENTRAL', 'tipo_recurso': 'CAPITAL'},
    {'codigo': '1.3.01.02', 'nombre': 'Asignaciones Directas FCR', 'fuente': reg, 'nivel': 'CENTRAL', 'tipo_recurso': 'CAPITAL'},
    {'codigo': '2.1.01.01', 'nombre': 'Recursos Propios EP Salud', 'fuente': icld, 'nivel': 'EP', 'tipo_recurso': 'CORRIENTE'},
    {'codigo': '2.1.01.02', 'nombre': 'Recursos Propios EP Educacion', 'fuente': icld, 'nivel': 'EP', 'tipo_recurso': 'CORRIENTE'},
]

for r_data in rubros_data:
    rubro, created = Rubro.objects.get_or_create(
        codigo=r_data['codigo'],
        defaults={
            'nombre': r_data['nombre'],
            'fuente': r_data['fuente'],
            'nivel': r_data['nivel'],
            'tipo_recurso': r_data['tipo_recurso'],
            'creado_por': admin_user
        }
    )
    if created:
        print(f"Rubro creado: {rubro.codigo}")

# Crear algunos movimientos de ejemplo
rubros = Rubro.objects.all()

for rubro in rubros[:5]:  # Solo los primeros 5 rubros
    # Presupuesto inicial
    mov, created = Movimiento.objects.get_or_create(
        rubro=rubro,
        tipo='INICIAL',
        documento_soporte='Ordenanza 001 de 2025',
        defaults={
            'fecha': date(2025, 1, 1),
            'valor': Decimal('150000000'),
            'observaciones': 'Presupuesto inicial aprobado',
            'registrado_por': admin_user
        }
    )
    if created:
        print(f"Movimiento inicial creado para {rubro.codigo}")

    # Una adicion
    mov2, created2 = Movimiento.objects.get_or_create(
        rubro=rubro,
        tipo='ADICION',
        documento_soporte='Decreto 015 de 2025',
        defaults={
            'fecha': date(2025, 3, 15),
            'valor': Decimal('25000000'),
            'observaciones': 'Adicion por mayor recaudo',
            'registrado_por': admin_user
        }
    )
    if created2:
        print(f"Adicion creada para {rubro.codigo}")

print("\n=== Datos de ejemplo creados exitosamente ===")
print(f"Fuentes: {FuenteFinanciacion.objects.count()}")
print(f"Rubros: {Rubro.objects.count()}")
print(f"Movimientos: {Movimiento.objects.count()}")
