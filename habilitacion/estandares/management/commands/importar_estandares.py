"""
Comando para importar estándares y criterios desde el archivo Excel de autoevaluación.
Resolución 3100 de 2019 - MinSalud Colombia
"""

import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from estandares.models import GrupoEstandar, Estandar, Servicio, EstandarServicio, Criterio


class Command(BaseCommand):
    help = 'Importa estándares y criterios desde el archivo Excel de autoevaluación'

    # Mapeo de hojas del Excel a grupos de estándares
    GRUPOS_ESTANDARES = {
        '11.1': {
            'nombre': 'Estándares aplicables a todos los servicios',
            'aplica_todos': True,
            'estandares': [
                ('11.1.1', 'TH', 'Talento Humano'),
                ('11.1.2', 'INF', 'Infraestructura'),
                ('11.1.3', 'DOT', 'Dotación'),
                ('11.1.4', 'MD', 'Medicamentos, Dispositivos Médicos e Insumos'),
                ('11.1.5', 'PP', 'Procesos Prioritarios'),
                ('11.1.6', 'HCR', 'Historia Clínica y Registros'),
                ('11.1.7', 'INT', 'Interdependencia'),
            ]
        },
        '11.2': {
            'nombre': 'Grupo Consulta Externa',
            'aplica_todos': False,
        },
        '11.3': {
            'nombre': 'Grupo Apoyo Diagnóstico y Complementación Terapéutica',
            'aplica_todos': False,
        },
        '11.4': {
            'nombre': 'Grupo Internación',
            'aplica_todos': False,
        },
        '11.5': {
            'nombre': 'Grupo Quirúrgico',
            'aplica_todos': False,
        },
        '11.6': {
            'nombre': 'Grupo Atención Inmediata',
            'aplica_todos': False,
        },
    }

    # Mapeo de hojas del Excel a servicios
    HOJAS_SERVICIOS = {
        # Grupo 11.1 - Todos los servicios
        'TSTH': ('11.1', '11.1.1', 'Talento Humano'),
        'INF': ('11.1', '11.1.2', 'Infraestructura'),
        'DOT': ('11.1', '11.1.3', 'Dotación'),
        'MDI': ('11.1', '11.1.4', 'Medicamentos, Dispositivos Médicos e Insumos'),
        'PP': ('11.1', '11.1.5', 'Procesos Prioritarios'),
        'HC': ('11.1', '11.1.6', 'Historia Clínica y Registros'),
        'IND': ('11.1', '11.1.7', 'Interdependencia'),

        # Grupo 11.2 - Consulta Externa
        'CEGM': ('11.2', '11.2.1', 'Consulta Externa General de Medicina'),
        'CEGE': ('11.2', '11.2.2', 'Consulta Externa General de Enfermería'),
        'CEOD': ('11.2', '11.2.3', 'Consulta Externa General de Odontología'),

        # Grupo 11.3 - Apoyo Diagnóstico
        'SFARMA': ('11.3', '11.3.1', 'Servicio Farmacéutico'),
        'LABCLINI': ('11.3', '11.3.2', 'Laboratorio Clínico'),
        'IMGDX': ('11.3', '11.3.3', 'Diagnóstico por Imagen'),
        'ECOC': ('11.3', '11.3.4', 'Ecocardiografía'),

        # Grupo 11.4 - Internación
        'HOSPGRAL': ('11.4', '11.4.1', 'Hospitalización General'),
        'HOSPOBS': ('11.4', '11.4.2', 'Hospitalización Obstétrica'),
        'HOSPPED': ('11.4', '11.4.3', 'Hospitalización Pediátrica'),

        # Grupo 11.5 - Quirúrgico
        'SALAS CIR': ('11.5', '11.5.1', 'Salas de Cirugía'),
        'PARTOS': ('11.5', '11.5.2', 'Sala de Partos'),

        # Grupo 11.6 - Atención Inmediata
        'URGENCIAS': ('11.6', '11.6.1', 'Servicio de Urgencias'),
        'AMBULANCIA': ('11.6', '11.6.2', 'Transporte Asistencial'),
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            type=str,
            default='autoevaluacion-_resolucion-3100-2019-anexo-estandar.xlsx',
            help='Ruta al archivo Excel de autoevaluación'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Eliminar datos existentes antes de importar'
        )

    def handle(self, *args, **options):
        archivo = options['archivo']

        # Buscar el archivo en la carpeta del proyecto
        if not os.path.isabs(archivo):
            archivo = os.path.join(settings.BASE_DIR, archivo)

        if not os.path.exists(archivo):
            self.stderr.write(self.style.ERROR(f'No se encontró el archivo: {archivo}'))
            return

        self.stdout.write(f'Leyendo archivo: {archivo}')

        if options['limpiar']:
            self.stdout.write('Limpiando datos existentes...')
            Criterio.objects.all().delete()
            EstandarServicio.objects.all().delete()
            Servicio.objects.all().delete()
            Estandar.objects.all().delete()
            GrupoEstandar.objects.all().delete()

        try:
            # Leer todas las hojas del Excel
            excel_file = pd.ExcelFile(archivo)
            self.stdout.write(f'Hojas encontradas: {len(excel_file.sheet_names)}')

            # Crear grupos de estándares
            self.crear_grupos_estandares()

            # Importar criterios de cada hoja
            for hoja in excel_file.sheet_names:
                self.importar_hoja(excel_file, hoja)

            self.stdout.write(self.style.SUCCESS('Importación completada exitosamente'))

            # Mostrar resumen
            self.stdout.write(f'\nResumen:')
            self.stdout.write(f'  Grupos de estándares: {GrupoEstandar.objects.count()}')
            self.stdout.write(f'  Estándares: {Estandar.objects.count()}')
            self.stdout.write(f'  Servicios: {Servicio.objects.count()}')
            self.stdout.write(f'  Criterios: {Criterio.objects.count()}')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error durante la importación: {str(e)}'))
            raise

    def crear_grupos_estandares(self):
        """Crea los grupos principales de estándares"""
        self.stdout.write('Creando grupos de estándares...')

        for orden, (codigo, datos) in enumerate(self.GRUPOS_ESTANDARES.items(), 1):
            grupo, created = GrupoEstandar.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': datos['nombre'],
                    'aplica_todos': datos.get('aplica_todos', False),
                    'orden': orden
                }
            )

            if created:
                self.stdout.write(f'  Creado grupo: {codigo} - {datos["nombre"]}')

            # Crear estándares del grupo 11.1
            if 'estandares' in datos:
                for est_orden, (est_codigo, est_corto, est_nombre) in enumerate(datos['estandares'], 1):
                    estandar, _ = Estandar.objects.update_or_create(
                        grupo=grupo,
                        codigo=est_codigo,
                        defaults={
                            'codigo_corto': est_corto,
                            'nombre': est_nombre,
                            'orden': est_orden
                        }
                    )

    def importar_hoja(self, excel_file, hoja):
        """Importa criterios de una hoja del Excel"""
        try:
            df = pd.read_excel(excel_file, sheet_name=hoja)

            if df.empty:
                return

            # Buscar la columna que contiene los criterios
            col_criterio = None
            for col in df.columns:
                col_str = str(col).lower()
                if 'estándar' in col_str or 'criterio' in col_str or 'requisito' in col_str:
                    col_criterio = col
                    break

            if col_criterio is None and len(df.columns) > 0:
                # Usar la primera columna que tenga texto
                for col in df.columns:
                    if df[col].dtype == 'object' and df[col].notna().any():
                        col_criterio = col
                        break

            if col_criterio is None:
                return

            # Determinar a qué estándar pertenece
            grupo_codigo, estandar_codigo, servicio_nombre = self.HOJAS_SERVICIOS.get(
                hoja, (None, None, None)
            )

            if grupo_codigo is None:
                # Intentar determinar por el nombre de la hoja
                for key, value in self.HOJAS_SERVICIOS.items():
                    if key.lower() in hoja.lower():
                        grupo_codigo, estandar_codigo, servicio_nombre = value
                        break

            if grupo_codigo is None:
                self.stdout.write(f'  Hoja "{hoja}" no mapeada, omitiendo...')
                return

            grupo = GrupoEstandar.objects.filter(codigo=grupo_codigo).first()
            if not grupo:
                return

            # Para el grupo 11.1, agregar criterios al estándar
            if grupo_codigo == '11.1':
                estandar = Estandar.objects.filter(codigo=estandar_codigo).first()
                if estandar:
                    self.importar_criterios_estandar(df, col_criterio, estandar, hoja)
            else:
                # Para otros grupos, crear servicio y estándares de servicio
                servicio, _ = Servicio.objects.update_or_create(
                    codigo=estandar_codigo,
                    defaults={
                        'grupo': grupo,
                        'nombre': servicio_nombre or hoja,
                        'codigo_hoja_excel': hoja
                    }
                )
                self.importar_criterios_servicio(df, col_criterio, servicio, hoja)

            self.stdout.write(f'  Importada hoja: {hoja}')

        except Exception as e:
            self.stderr.write(f'  Error en hoja "{hoja}": {str(e)}')

    def importar_criterios_estandar(self, df, col_criterio, estandar, hoja):
        """Importa criterios para un estándar general (11.1.x)"""
        orden = 0
        for idx, row in df.iterrows():
            texto = row.get(col_criterio)
            if pd.isna(texto) or not str(texto).strip():
                continue

            texto = str(texto).strip()
            orden += 1

            # Detectar si es un título
            es_titulo = len(texto) < 100 and texto.isupper()

            # Extraer número si existe
            numero = str(orden)
            if texto[0].isdigit():
                partes = texto.split(' ', 1)
                if partes[0].replace('.', '').isdigit():
                    numero = partes[0]

            Criterio.objects.update_or_create(
                estandar=estandar,
                numero=numero,
                defaults={
                    'texto': texto,
                    'es_titulo': es_titulo,
                    'orden': orden
                }
            )

    def importar_criterios_servicio(self, df, col_criterio, servicio, hoja):
        """Importa criterios para un servicio específico"""
        # Crear estándar de servicio genérico
        estandar_servicio, _ = EstandarServicio.objects.update_or_create(
            servicio=servicio,
            tipo='TH',  # Por defecto Talento Humano
            defaults={
                'codigo': f'{servicio.codigo}_TH',
                'orden': 1
            }
        )

        orden = 0
        for idx, row in df.iterrows():
            texto = row.get(col_criterio)
            if pd.isna(texto) or not str(texto).strip():
                continue

            texto = str(texto).strip()
            orden += 1

            es_titulo = len(texto) < 100 and texto.isupper()
            numero = str(orden)

            Criterio.objects.update_or_create(
                estandar_servicio=estandar_servicio,
                numero=numero,
                defaults={
                    'texto': texto,
                    'es_titulo': es_titulo,
                    'orden': orden
                }
            )
