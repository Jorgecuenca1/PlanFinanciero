"""
Script para marcar los servicios del grupo 11.1 como obligatorios.
Ejecutar con: python manage.py shell < marcar_servicios_obligatorios.py
O ejecutar desde Django shell.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habilitacion_project.settings')
django.setup()

from estandares.models import Servicio, GrupoEstandar, Estandar

def marcar_obligatorios():
    """Marca los servicios y estandares del grupo 11.1 como obligatorios"""

    # Buscar el grupo 11.1
    grupo_11_1 = GrupoEstandar.objects.filter(codigo__startswith='11.1').first()

    if not grupo_11_1:
        print("No se encontro el grupo 11.1. Creando estructura basica...")

        # Crear grupo 11.1 si no existe
        grupo_11_1, created = GrupoEstandar.objects.get_or_create(
            codigo='11.1',
            defaults={
                'nombre': 'Estandares aplicables a todos los servicios',
                'descripcion': 'Estandares y criterios que aplican a todos los servicios de salud',
                'aplica_todos': True,
                'orden': 1,
                'activo': True
            }
        )
        if created:
            print(f"Creado grupo: {grupo_11_1}")

        # Crear los 7 estandares del grupo 11.1
        estandares_11_1 = [
            ('11.1.1', 'TSTH', 'Talento Humano', '59-61'),
            ('11.1.2', 'INF', 'Infraestructura', '61-68'),
            ('11.1.3', 'DOT', 'Dotacion', '68-71'),
            ('11.1.4', 'MD', 'Medicamentos, Dispositivos Medicos e Insumos', '71-73'),
            ('11.1.5', 'PP', 'Procesos Prioritarios', '73-77'),
            ('11.1.6', 'HCR', 'Historia Clinica y Registros', '77-79'),
            ('11.1.7', 'INT', 'Interdependencia', '79'),
        ]

        for i, (codigo, codigo_corto, nombre, paginas) in enumerate(estandares_11_1, 1):
            estandar, created = Estandar.objects.get_or_create(
                grupo=grupo_11_1,
                codigo=codigo,
                defaults={
                    'codigo_corto': codigo_corto,
                    'nombre': nombre,
                    'paginas_resolucion': paginas,
                    'orden': i,
                    'activo': True
                }
            )
            if created:
                print(f"Creado estandar: {estandar}")

    # Marcar el grupo como aplica_todos
    grupo_11_1.aplica_todos = True
    grupo_11_1.save()
    print(f"Grupo {grupo_11_1.codigo} marcado como aplica_todos=True")

    # Marcar todos los servicios del grupo 11.1 como obligatorios
    servicios_actualizados = Servicio.objects.filter(grupo=grupo_11_1).update(es_obligatorio=True)
    print(f"Servicios marcados como obligatorios: {servicios_actualizados}")

    # También marcar servicios que tengan código que empiece con 11.1
    servicios_por_codigo = Servicio.objects.filter(codigo__startswith='11.1').update(es_obligatorio=True)
    print(f"Servicios adicionales por codigo: {servicios_por_codigo}")

    print("\nResumen:")
    print(f"- Servicios obligatorios: {Servicio.objects.filter(es_obligatorio=True).count()}")
    print(f"- Servicios opcionales: {Servicio.objects.filter(es_obligatorio=False).count()}")
    print(f"- Grupos con aplica_todos: {GrupoEstandar.objects.filter(aplica_todos=True).count()}")

if __name__ == '__main__':
    marcar_obligatorios()
