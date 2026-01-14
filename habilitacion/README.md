# Sistema de Habilitación de Servicios de Salud

Sistema para la gestión del proceso de habilitación de prestadores de servicios de salud en Colombia, basado en la **Resolución 3100 de 2019**.

---

## Acceso Rápido

| Campo | Valor |
|-------|-------|
| **URL** | http://127.0.0.1:8020/ |
| **Usuario** | admin@habilitacion.com |
| **Contraseña** | admin123 |
| **Admin Django** | http://127.0.0.1:8020/admin/ |

---

## Iniciar el Sistema

### Opción 1: Archivo BAT
```
Ejecutar: iniciar_servidor.bat
```

### Opción 2: Línea de Comandos
```bash
cd C:\Users\HOME\PycharmProjects\habilitacion
.venv\Scripts\activate
python manage.py runserver 8020
```

---

## Entidades de Ejemplo

El sistema incluye 3 entidades de ejemplo:

| Entidad | Tipo | NIT |
|---------|------|-----|
| CLINICA EJEMPLO SALUD S.A.S. | IPS | 900123456-7 |
| CONSULTORIO MEDICO DR. GARCIA | PI | 1023456789-3 |
| LABORATORIO CLINICO ANALIZAR LTDA | PSA | 800987654-1 |

---

## Datos Cargados

- **5** Tipos de Prestador (IPS, PI, PSA, OSD, TA)
- **33** Departamentos de Colombia
- **65** Municipios
- **6** Grupos de Estándares (11.1 a 11.6)
- **7** Estándares
- **429** Criterios de Evaluación

---

## Módulos del Sistema

| Módulo | Descripción |
|--------|-------------|
| **Entidades** | Gestión de prestadores de salud |
| **Estándares** | Criterios de la Resolución 3100 |
| **Evaluación** | Autoevaluación de cumplimiento |
| **Documentos** | Gestión documental con IA |
| **Reportes** | Informes de cumplimiento |
| **PAMEC** | Mejoramiento continuo (en desarrollo) |
| **SIAU** | Atención al usuario (en desarrollo) |

---

## Documentación

Ver el archivo **MANUAL_USUARIO.md** para la guía completa de uso.

---

## Tecnologías

- Python 3.13
- Django 6.0
- Bootstrap 5
- SQLite
- OpenAI API (para generación de documentos)

---

## Resolución 3100 de 2019

Este sistema implementa los estándares de habilitación definidos en la Resolución 3100 de 2019 del Ministerio de Salud y Protección Social de Colombia.

Grupos de estándares:
- 11.1 Talento Humano
- 11.2 Infraestructura
- 11.3 Dotación
- 11.4 Medicamentos y Dispositivos
- 11.5 Procesos Prioritarios
- 11.6 Historia Clínica
