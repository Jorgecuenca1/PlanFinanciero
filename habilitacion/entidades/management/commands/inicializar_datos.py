"""
Comando para inicializar datos básicos del sistema.
Departamentos, municipios y tipos de prestador.
"""

from django.core.management.base import BaseCommand
from entidades.models import TipoPrestador, Departamento, Municipio


class Command(BaseCommand):
    help = 'Inicializa datos básicos: tipos de prestador, departamentos y municipios'

    # Tipos de prestador según Resolución 3100 de 2019
    TIPOS_PRESTADOR = [
        ('IPS', 'Institución Prestadora de Servicios de Salud',
         'Entidades públicas, privadas o mixtas, cuyo objeto social es la prestación de servicios de salud.'),
        ('PI', 'Profesional Independiente',
         'Persona natural con título de formación en el área de la salud que presta servicios de salud de forma independiente.'),
        ('PSA', 'Prestación de Servicios Asistenciales',
         'Entidades con objeto social diferente a la prestación de servicios de salud, que cuentan con una infraestructura para prestar servicios de salud.'),
        ('OSD', 'Objeto Social Diferente',
         'Entidades cuyo objeto social es diferente a la prestación de servicios de salud.'),
        ('TA', 'Transporte Asistencial',
         'Entidades que prestan servicios de transporte de pacientes en ambulancias.'),
    ]

    # Departamentos de Colombia con sus códigos DANE
    DEPARTAMENTOS = [
        ('05', 'Antioquia'),
        ('08', 'Atlántico'),
        ('11', 'Bogotá D.C.'),
        ('13', 'Bolívar'),
        ('15', 'Boyacá'),
        ('17', 'Caldas'),
        ('18', 'Caquetá'),
        ('19', 'Cauca'),
        ('20', 'Cesar'),
        ('23', 'Córdoba'),
        ('25', 'Cundinamarca'),
        ('27', 'Chocó'),
        ('41', 'Huila'),
        ('44', 'La Guajira'),
        ('47', 'Magdalena'),
        ('50', 'Meta'),
        ('52', 'Nariño'),
        ('54', 'Norte de Santander'),
        ('63', 'Quindío'),
        ('66', 'Risaralda'),
        ('68', 'Santander'),
        ('70', 'Sucre'),
        ('73', 'Tolima'),
        ('76', 'Valle del Cauca'),
        ('81', 'Arauca'),
        ('85', 'Casanare'),
        ('86', 'Putumayo'),
        ('88', 'San Andrés y Providencia'),
        ('91', 'Amazonas'),
        ('94', 'Guainía'),
        ('95', 'Guaviare'),
        ('97', 'Vaupés'),
        ('99', 'Vichada'),
    ]

    # Municipios principales (capitales y ciudades importantes)
    MUNICIPIOS = {
        '05': [
            ('05001', 'Medellín'),
            ('05088', 'Bello'),
            ('05360', 'Itagüí'),
            ('05266', 'Envigado'),
        ],
        '08': [
            ('08001', 'Barranquilla'),
            ('08758', 'Soledad'),
            ('08433', 'Malambo'),
        ],
        '11': [
            ('11001', 'Bogotá D.C.'),
        ],
        '13': [
            ('13001', 'Cartagena'),
            ('13430', 'Magangué'),
        ],
        '15': [
            ('15001', 'Tunja'),
            ('15759', 'Sogamoso'),
            ('15238', 'Duitama'),
        ],
        '17': [
            ('17001', 'Manizales'),
        ],
        '18': [
            ('18001', 'Florencia'),
        ],
        '19': [
            ('19001', 'Popayán'),
        ],
        '20': [
            ('20001', 'Valledupar'),
            ('20013', 'Aguachica'),
        ],
        '23': [
            ('23001', 'Montería'),
        ],
        '25': [
            ('25754', 'Soacha'),
            ('25473', 'Mosquera'),
            ('25214', 'Facatativá'),
            ('25269', 'Fusagasugá'),
            ('25286', 'Funza'),
            ('25175', 'Chía'),
            ('25899', 'Zipaquirá'),
        ],
        '27': [
            ('27001', 'Quibdó'),
        ],
        '41': [
            ('41001', 'Neiva'),
            ('41551', 'Pitalito'),
        ],
        '44': [
            ('44001', 'Riohacha'),
            ('44430', 'Maicao'),
        ],
        '47': [
            ('47001', 'Santa Marta'),
            ('47189', 'Ciénaga'),
        ],
        '50': [
            ('50001', 'Villavicencio'),
            ('50006', 'Acacías'),
            ('50313', 'Granada'),
        ],
        '52': [
            ('52001', 'Pasto'),
            ('52356', 'Ipiales'),
            ('52835', 'Tumaco'),
        ],
        '54': [
            ('54001', 'Cúcuta'),
            ('54498', 'Ocaña'),
        ],
        '63': [
            ('63001', 'Armenia'),
        ],
        '66': [
            ('66001', 'Pereira'),
            ('66170', 'Dosquebradas'),
        ],
        '68': [
            ('68001', 'Bucaramanga'),
            ('68276', 'Floridablanca'),
            ('68307', 'Girón'),
            ('68547', 'Piedecuesta'),
            ('68081', 'Barrancabermeja'),
        ],
        '70': [
            ('70001', 'Sincelejo'),
        ],
        '73': [
            ('73001', 'Ibagué'),
        ],
        '76': [
            ('76001', 'Cali'),
            ('76109', 'Buenaventura'),
            ('76520', 'Palmira'),
            ('76834', 'Tuluá'),
            ('76147', 'Cartago'),
        ],
        '81': [
            ('81001', 'Arauca'),
        ],
        '85': [
            ('85001', 'Yopal'),
        ],
        '86': [
            ('86001', 'Mocoa'),
        ],
        '88': [
            ('88001', 'San Andrés'),
        ],
        '91': [
            ('91001', 'Leticia'),
        ],
        '94': [
            ('94001', 'Inírida'),
        ],
        '95': [
            ('95001', 'San José del Guaviare'),
        ],
        '97': [
            ('97001', 'Mitú'),
        ],
        '99': [
            ('99001', 'Puerto Carreño'),
        ],
    }

    def handle(self, *args, **options):
        self.stdout.write('Inicializando datos básicos...\n')

        # Crear tipos de prestador
        self.stdout.write('Creando tipos de prestador...')
        for codigo, nombre, descripcion in self.TIPOS_PRESTADOR:
            tipo, created = TipoPrestador.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'activo': True
                }
            )
            if created:
                self.stdout.write(f'  Creado: {nombre}')

        # Crear departamentos
        self.stdout.write('\nCreando departamentos...')
        for codigo, nombre in self.DEPARTAMENTOS:
            depto, created = Departamento.objects.update_or_create(
                codigo=codigo,
                defaults={'nombre': nombre}
            )
            if created:
                self.stdout.write(f'  Creado: {nombre}')

        # Crear municipios
        self.stdout.write('\nCreando municipios...')
        municipios_creados = 0
        for depto_codigo, municipios in self.MUNICIPIOS.items():
            try:
                departamento = Departamento.objects.get(codigo=depto_codigo)
                for mun_codigo, mun_nombre in municipios:
                    mun, created = Municipio.objects.update_or_create(
                        codigo=mun_codigo,
                        defaults={
                            'nombre': mun_nombre,
                            'departamento': departamento
                        }
                    )
                    if created:
                        municipios_creados += 1
            except Departamento.DoesNotExist:
                continue

        self.stdout.write(f'  Municipios creados: {municipios_creados}')

        # Resumen final
        self.stdout.write(self.style.SUCCESS('\n¡Inicialización completada!'))
        self.stdout.write(f'\nResumen:')
        self.stdout.write(f'  Tipos de prestador: {TipoPrestador.objects.count()}')
        self.stdout.write(f'  Departamentos: {Departamento.objects.count()}')
        self.stdout.write(f'  Municipios: {Municipio.objects.count()}')
