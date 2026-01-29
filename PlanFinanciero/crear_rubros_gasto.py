"""
Script para crear los rubros de gasto iniciales
Ejecutar con: python manage.py shell < crear_rubros_gasto.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from planfinanciero.models import RubroGasto

# Rubros para Centralizados (3 rubros)
rubros_centralizados = [
    ('FUNCIONAMIENTO', 'Funcionamiento', 'Gastos de funcionamiento del ente centralizado'),
    ('DEUDA', 'Deuda', 'Servicio de la deuda publica'),
    ('INVERSION', 'Inversion', 'Gastos de inversion'),
]

# Rubros para Descentralizados (4 rubros - incluye Gastos de Operacion)
rubros_descentralizados = [
    ('FUNCIONAMIENTO', 'Funcionamiento', 'Gastos de funcionamiento'),
    ('DEUDA', 'Deuda', 'Servicio de la deuda'),
    ('INVERSION', 'Inversion', 'Gastos de inversion'),
    ('GASTOS_OPERACION', 'Gastos de Operacion', 'Gastos de operacion de entidades descentralizadas'),
]

print("Creando rubros de gasto...")

# Crear rubros centralizados
for codigo, nombre, descripcion in rubros_centralizados:
    rubro, created = RubroGasto.objects.get_or_create(
        tipo_entidad='CENTRALIZADO',
        codigo=codigo,
        defaults={
            'nombre': nombre,
            'descripcion': descripcion,
        }
    )
    if created:
        print(f"  [+] Centralizado: {nombre}")
    else:
        print(f"  [=] Centralizado: {nombre} (ya existe)")

# Crear rubros descentralizados
for codigo, nombre, descripcion in rubros_descentralizados:
    rubro, created = RubroGasto.objects.get_or_create(
        tipo_entidad='DESCENTRALIZADO',
        codigo=codigo,
        defaults={
            'nombre': nombre,
            'descripcion': descripcion,
        }
    )
    if created:
        print(f"  [+] Descentralizado: {nombre}")
    else:
        print(f"  [=] Descentralizado: {nombre} (ya existe)")

print("\nRubros de gasto creados exitosamente!")
print(f"Total rubros: {RubroGasto.objects.count()}")
