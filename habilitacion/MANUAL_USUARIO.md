# Sistema de Habilitación de Servicios de Salud
## Manual de Usuario - Resolución 3100 de 2019

---

## CREDENCIALES DE ACCESO

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin@habilitacion.com | admin123 | Super Administrador |

**URL de acceso:** http://127.0.0.1:8020/

---

## 1. ESTRUCTURA DEL SISTEMA

El sistema está diseñado según la estructura de la Resolución 3100 de 2019:

```
ENTIDAD PRESTADORA
    │
    ├── SEDE 1
    │       ├── Servicios Habilitados
    │       │       ├── Servicio A
    │       │       └── Servicio B
    │       │
    │       └── EVALUACIONES (por cada criterio)
    │               ├── Estado: C, NC, NA, PE
    │               ├── Documento de Soporte (Word editable con IA)
    │               ├── Estado Documento: NT, ED, AP
    │               ├── Responsable Desarrollo
    │               ├── Responsable Calidad
    │               ├── Responsable Aprobación
    │               ├── Fecha de Aprobación
    │               ├── Fecha de Vencimiento
    │               └── Historial de Cambios
    │
    └── SEDE 2
            └── (misma estructura)
```

---

## 2. GRUPOS DE ESTÁNDARES (Resolución 3100)

| Código | Grupo | Hojas Excel |
|--------|-------|-------------|
| 11.1 | Estándares aplicables a TODOS los servicios | |
| 11.1.1 | Talento Humano (TH) | 11.1.1TH |
| 11.1.2 | Infraestructura (INF) | 11.1.2.INF |
| 11.1.3 | Dotación (DOT) | 11.1.3.DOT |
| 11.1.4 | Medicamentos y Dispositivos (MD) | 11.1.4MD |
| 11.1.5 | Procesos Prioritarios (PP) | 11.1.5.PP |
| 11.1.6 | Historia Clínica y Registros (HCR) | 11.1.6.HCR |
| 11.1.7 | Interdependencia (INT) | 11.1.7INT |
| 11.2 - 11.6 | Estándares por Servicio Específico | Hojas específicas |

---

## 3. ESTADOS DE EVALUACIÓN

### 3.1 Estado de Cumplimiento del Criterio

| Estado | Código | Descripción | Color |
|--------|--------|-------------|-------|
| **Cumple** | C | El criterio está completamente cumplido | Verde |
| **No Cumple** | NC | El criterio NO se cumple actualmente | Rojo |
| **No Aplica** | NA | El criterio no aplica para este servicio/sede | Gris |
| **Pendiente** | PE | Aún no se ha evaluado el criterio | Amarillo |

### 3.2 Estado del Documento de Soporte

| Estado | Código | Descripción | Quién puede modificar |
|--------|--------|-------------|----------------------|
| **No Trabajado** | NT | No se ha iniciado el documento | Cualquier usuario asignado |
| **En Desarrollo** | ED | El documento está en elaboración | Responsable de Desarrollo |
| **Aprobado** | AP | Documento completo y aprobado | **SOLO el Administrador** |

> **IMPORTANTE:** Una vez un documento está en estado **APROBADO**, solo el Administrador de la Entidad puede modificar su estado.

---

## 4. FLUJO DE TRABAJO POR CRITERIO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE EVALUACIÓN POR CRITERIO                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PASO 1: ASIGNAR RESPONSABLES                                               │
│  ─────────────────────────────                                              │
│  • Responsable de Desarrollo: Quien elabora el documento                   │
│  • Responsable de Calidad: Quien revisa el contenido                       │
│  • Responsable de Aprobación: Quien da el visto bueno final               │
│                                                                             │
│  PASO 2: CREAR/EDITAR DOCUMENTO                                             │
│  ─────────────────────────────                                              │
│  • Estado inicial: NO TRABAJADO (NT)                                       │
│  • El responsable crea el documento (puede usar IA)                        │
│  • Cambiar estado a: EN DESARROLLO (ED)                                    │
│                                                                             │
│  PASO 3: DESARROLLO CON IA                                                  │
│  ─────────────────────────                                                  │
│  • Generar borrador con ChatGPT                                            │
│  • Editar y ajustar el contenido                                           │
│  • Adjuntar archivos de soporte                                            │
│  • El documento puede tener múltiples versiones                            │
│                                                                             │
│  PASO 4: REVISIÓN DE CALIDAD                                                │
│  ─────────────────────────                                                  │
│  • El responsable de calidad revisa                                        │
│  • Puede devolver a desarrollo si hay correcciones                         │
│  • Si está correcto, solicita aprobación                                   │
│                                                                             │
│  PASO 5: APROBACIÓN                                                         │
│  ─────────────────                                                          │
│  • El responsable de aprobación revisa                                     │
│  • Cambia estado a: APROBADO (AP)                                          │
│  • Se registra fecha de aprobación                                         │
│  • El documento queda BLOQUEADO para edición                               │
│                                                                             │
│  PASO 6: EVALUACIÓN DEL CRITERIO                                            │
│  ───────────────────────────────                                            │
│  • Con el documento aprobado, se evalúa:                                   │
│    - CUMPLE (C): Todo correcto                                             │
│    - NO CUMPLE (NC): Hay deficiencias                                      │
│    - NO APLICA (NA): No corresponde a este servicio                        │
│                                                                             │
│  PASO 7: SEGUIMIENTO                                                        │
│  ────────────────────                                                       │
│  • Si tiene fecha de vencimiento, monitorear                               │
│  • El sistema alerta 30, 60, 90 días antes                                 │
│  • Todo queda registrado en el historial                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. ROLES Y PERMISOS

| Rol | Código | Permisos |
|-----|--------|----------|
| Super Administrador | SUPER | Acceso total, gestión de usuarios, todas las entidades |
| Administrador | ADMIN | Gestión de su entidad, puede aprobar documentos, cambiar estados aprobados |
| Gestión de Calidad | CALIDAD | Revisar documentos, gestionar evaluaciones, no puede aprobar |
| Evaluador | EVALUADOR | Crear/editar documentos, evaluar criterios |
| Aprobador | APROBADOR | Aprobar documentos y evaluaciones |
| Consultor | CONSULTOR | Solo lectura, ver reportes |

---

## 6. PROCESO DETALLADO DE EVALUACIÓN

### 6.1 Acceder a la Evaluación

1. Menú → **Evaluaciones**
2. Seleccionar la **Sede** a evaluar
3. Ver el resumen de cumplimiento por estándar

### 6.2 Evaluar un Estándar (Ejemplo: Talento Humano)

1. Hacer clic en **"Evaluar"** en el estándar 11.1.1 Talento Humano
2. Aparece la lista de todos los criterios:

```
┌──────────┬────────────────────────────────────────────────────────┬────────┬──────────────┬─────────────┐
│ Código   │ Criterio                                               │ Estado │ Estado Doc   │ Responsable │
├──────────┼────────────────────────────────────────────────────────┼────────┼──────────────┼─────────────┤
│ TSTH.1   │ El talento humano cuenta con títulos de educación...  │   PE   │     NT       │   Sin asignar │
│ TSTH.2   │ El talento humano cuenta con resolución de ejercicio..│   PE   │     NT       │   Sin asignar │
│ TSTH.3   │ El prestador determina la cantidad de talento humano..│   PE   │     NT       │   Sin asignar │
│ TSTH.4.1 │ Convenio vigente con institución educativa...         │   PE   │     NT       │   Sin asignar │
│ TSTH.4.2 │ Mecanismos de supervisión del personal en entrenamiento│   PE   │     NT       │   Sin asignar │
└──────────┴────────────────────────────────────────────────────────┴────────┴──────────────┴─────────────┘
```

### 6.3 Trabajar un Criterio Específico

1. Hacer clic en el criterio **TSTH.1**
2. Aparece la pantalla de detalle:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CRITERIO: TSTH.1                                                            │
│ Estándar: 11.1.1 Talento Humano                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ DESCRIPCIÓN:                                                                │
│ El talento humano en salud y otros profesionales que se relacionan con     │
│ la atención o resultados en salud de los usuarios, cuentan con los         │
│ títulos, según aplique, de educación superior o certificados de aptitud    │
│ ocupacional, expedidos por la entidad educativa competente.                │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ RESPONSABLES:                                                               │
│ ┌─────────────────────┬──────────────────────────────────────┐             │
│ │ Desarrollo:         │ [Seleccionar usuario ▼]              │             │
│ │ Calidad:            │ [Seleccionar usuario ▼]              │             │
│ │ Aprobación:         │ [Seleccionar usuario ▼]              │             │
│ └─────────────────────┴──────────────────────────────────────┘             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ ESTADO DEL DOCUMENTO:                                                       │
│ ○ No Trabajado (NT)   ● En Desarrollo (ED)   ○ Aprobado (AP)               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ DOCUMENTO DE SOPORTE:                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐│
│ │ [Editor de texto enriquecido]                                           ││
│ │                                                                         ││
│ │ PROTOCOLO DE GESTIÓN DE HOJAS DE VIDA DEL TALENTO HUMANO               ││
│ │                                                                         ││
│ │ 1. OBJETIVO                                                             ││
│ │ Establecer los lineamientos para la verificación y custodia de...      ││
│ │                                                                         ││
│ │ 2. ALCANCE                                                              ││
│ │ Aplica a todo el personal asistencial y administrativo...              ││
│ │                                                                         ││
│ └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│ [🤖 Generar con IA]  [📎 Adjuntar archivo]  [💾 Guardar borrador]          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ EVALUACIÓN:                                                                 │
│ Estado de cumplimiento: ○ Cumple (C)  ○ No Cumple (NC)  ○ No Aplica (NA)   │
│                                                                             │
│ Comentarios: [__________________________________________________]          │
│                                                                             │
│ Fecha de vencimiento: [__/__/____] (si aplica)                             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ HISTORIAL:                                                                  │
│ • 10/01/2026 09:15 - Juan Pérez: Creación del registro                     │
│ • 10/01/2026 10:30 - María López: Documento generado con IA                │
│ • 10/01/2026 14:00 - María López: Documento editado                        │
│ • 10/01/2026 16:00 - Carlos Ruiz: Revisión de calidad                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. GENERACIÓN DE DOCUMENTOS CON IA

### 7.1 Usar el Asistente de IA

1. En el criterio, hacer clic en **"🤖 Generar con IA"**
2. El sistema genera un borrador basado en:
   - El criterio específico
   - La normativa aplicable (Resolución 3100)
   - Mejores prácticas del sector
3. Revisar y editar el contenido generado
4. Guardar como borrador

### 7.2 Tipos de Documentos que Genera

| Tipo | Descripción |
|------|-------------|
| Protocolo | Procedimiento detallado paso a paso |
| Guía | Orientaciones generales |
| Manual | Documento extenso con múltiples secciones |
| Formato | Plantilla para registro de información |
| Lista de chequeo | Verificación de cumplimiento |

---

## 8. CONTROL DE VENCIMIENTOS

### 8.1 Documentos con Fecha de Vencimiento

Algunos criterios requieren documentos que deben renovarse periódicamente:

| Documento | Vencimiento típico |
|-----------|-------------------|
| Pólizas de responsabilidad civil | Anual |
| Certificados de calibración de equipos | Anual |
| Licencias de software médico | Variable |
| Permisos sanitarios | 5 años |
| Contratos de mantenimiento | Anual |

### 8.2 Alertas de Vencimiento

El sistema alerta automáticamente:
- **90 días antes**: Alerta informativa (azul)
- **60 días antes**: Alerta de precaución (amarilla)
- **30 días antes**: Alerta urgente (naranja)
- **Vencido**: Alerta crítica (roja)

---

## 9. PORCENTAJES DE CUMPLIMIENTO

### 9.1 Cálculo del Porcentaje

```
                    Criterios que CUMPLEN (C)
Porcentaje = ────────────────────────────────────── × 100
              Total Criterios - No Aplica (NA)
```

### 9.2 Niveles de Cumplimiento

| Nivel | Porcentaje | Significado |
|-------|------------|-------------|
| Excelente | 90% - 100% | Listo para habilitación |
| Bueno | 70% - 89% | Requiere ajustes menores |
| Regular | 50% - 69% | Requiere trabajo significativo |
| Deficiente | < 50% | Requiere plan de mejora urgente |

### 9.3 Porcentajes que Muestra el Sistema

| Reporte | Descripción |
|---------|-------------|
| **Por Grupo** | % de cumplimiento de cada grupo (11.1.1, 11.1.2, etc.) |
| **Por Estándar** | % de cada estándar dentro del grupo |
| **Por Servicio** | % para servicios específicos (cuando aplica) |
| **General de Vigencia** | % total para el período de habilitación |
| **Por Sede** | % de cada sede de la entidad |

---

## 10. REPORTES DISPONIBLES

### 10.1 Reporte de Cumplimiento General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REPORTE DE CUMPLIMIENTO - VIGENCIA 2026                  │
│                    CLINICA EJEMPLO SALUD S.A.S.                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CUMPLIMIENTO GENERAL: 78.5%  ████████████████████░░░░░                     │
│                                                                             │
│  Por Grupo de Estándares:                                                   │
│  ┌─────────────────────────────────────┬───────────┬──────────────────────┐ │
│  │ Grupo                               │ Criterios │ Cumplimiento         │ │
│  ├─────────────────────────────────────┼───────────┼──────────────────────┤ │
│  │ 11.1.1 Talento Humano               │    21     │ 95% ████████████████ │ │
│  │ 11.1.2 Infraestructura              │   167     │ 72% ██████████████░░ │ │
│  │ 11.1.3 Dotación                     │    52     │ 85% ████████████████ │ │
│  │ 11.1.4 Medicamentos                 │    51     │ 80% ████████████████ │ │
│  │ 11.1.5 Procesos Prioritarios        │    91     │ 68% █████████████░░░ │ │
│  │ 11.1.6 Historia Clínica             │    50     │ 75% ███████████████░ │ │
│  └─────────────────────────────────────┴───────────┴──────────────────────┘ │
│                                                                             │
│  Documentos por Estado:                                                     │
│  • Aprobados (AP):     245  ████████████████████                           │
│  • En Desarrollo (ED):  87  ███████░░░░░░░░░░░░░                           │
│  • No Trabajados (NT):  97  ████████░░░░░░░░░░░░                           │
│                                                                             │
│  Próximos Vencimientos:                                                     │
│  • 5 documentos vencen en los próximos 30 días                             │
│  • 12 documentos vencen en los próximos 60 días                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. ENTIDADES DE EJEMPLO EN EL SISTEMA

| Entidad | Tipo | NIT | Estado |
|---------|------|-----|--------|
| CLINICA EJEMPLO SALUD S.A.S. | IPS | 900123456-7 | Activo |
| CONSULTORIO MEDICO DR. GARCIA | PI | 1023456789-3 | En Proceso |
| LABORATORIO CLINICO ANALIZAR LTDA | PSA | 800987654-1 | Activo |

---

## 12. DATOS CARGADOS EN EL SISTEMA

| Concepto | Cantidad |
|----------|----------|
| Tipos de Prestador | 5 (IPS, PI, PSA, OSD, TA) |
| Departamentos | 33 |
| Municipios | 65 |
| Grupos de Estándares | 6 (11.1.1 a 11.1.6) |
| Estándares | 7 |
| Criterios de Evaluación | 429 |

---

## 13. INICIAR EL SISTEMA

### Opción 1: Ejecutar el archivo BAT
```
Doble clic en: iniciar_servidor.bat
```

### Opción 2: Línea de comandos
```bash
cd C:\Users\HOME\PycharmProjects\habilitacion
.venv\Scripts\activate
python manage.py runserver 8020
```

### Acceder al Sistema
1. Abrir navegador: **http://127.0.0.1:8020/**
2. Usuario: **admin@habilitacion.com**
3. Contraseña: **admin123**

---

## 14. PANEL DE ADMINISTRACIÓN DJANGO

Para gestión avanzada de datos:

- **URL:** http://127.0.0.1:8020/admin/
- Mismas credenciales de acceso

Permite gestionar:
- Usuarios y roles
- Entidades y sedes
- Criterios y estándares
- Evaluaciones
- Documentos
- Historial de cambios

---

## 15. RESUMEN DE LA ESTRUCTURA DE DATOS

```
EVALUACIÓN (por cada criterio en cada sede)
├── Estado de Cumplimiento: C / NC / NA / PE
├── Estado del Documento: NT / ED / AP
├── Responsables:
│   ├── Desarrollo (quien crea)
│   ├── Calidad (quien revisa)
│   └── Aprobación (quien autoriza)
├── Fechas:
│   ├── Fecha de Evaluación
│   ├── Fecha de Aprobación
│   └── Fecha de Vencimiento (si aplica)
├── Documento de Soporte:
│   ├── Contenido editable (HTML)
│   ├── Archivos adjuntos
│   ├── Versiones del documento
│   └── Generado con IA (sí/no)
├── Comentarios y Justificaciones
└── Historial completo de cambios
```

---

## 16. VIGENCIAS DE EVALUACIÓN

Las **Vigencias** permiten organizar las evaluaciones por periodos de tiempo. Cada vigencia representa un ciclo de habilitación (normalmente de 4 años según la Resolución 3100).

### 16.1 Crear una Nueva Vigencia

1. Ir a **Evaluación > Vigencias** en el menú lateral
2. Clic en **Nueva Vigencia**
3. Completar:
   - **Entidad:** Seleccionar la entidad a evaluar
   - **Nombre del Periodo:** Ej: "Vigencia 2026", "Habilitación Inicial"
   - **Fecha Inicio y Fin:** Periodo de evaluación
   - **Observaciones:** Notas adicionales
4. Guardar

### 16.2 Dashboard de Vigencia

Al ver el detalle de una vigencia, se muestra:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VIGENCIA 2026                                        │
│                         CLINICA EJEMPLO S.A.S.                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CUMPLIMIENTO GENERAL: 78%                                                  │
│  ████████████████████░░░░░                                                 │
│                                                                             │
│  CUMPLIMIENTO POR GRUPOS:                                                   │
│  ┌───────────────────────────┬────────┬────────┬────────┬────────┬────────┐│
│  │ Grupo                     │ Cumple │ No Cum │ N/A    │ Pend.  │ %      ││
│  ├───────────────────────────┼────────┼────────┼────────┼────────┼────────┤│
│  │ 11.1.1 Talento Humano     │   18   │   2    │   1    │   0    │  90%   ││
│  │ 11.1.2 Infraestructura    │  120   │   35   │   12   │   0    │  77%   ││
│  │ 11.1.3 Dotación           │   45   │   5    │   2    │   0    │  90%   ││
│  │ 11.1.4 Medicamentos       │   40   │   8    │   3    │   0    │  83%   ││
│  │ 11.1.5 Procesos Prioritar │   65   │   22   │   4    │   0    │  75%   ││
│  │ 11.1.6 Historia Clínica   │   38   │   10   │   2    │   0    │  79%   ││
│  └───────────────────────────┴────────┴────────┴────────┴────────┴────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 16.3 Evaluar Criterios Individuales

Para cada criterio puede:

1. **Seleccionar Estado:** C (Cumple), NC (No Cumple), NA (No Aplica)
2. **Editar Documento:** Editor visual con opciones de formato
3. **Generar con IA:** Botón para crear documento usando ChatGPT
4. **Asignar Responsables:** Desarrollo, Calidad, Aprobación
5. **Establecer Fecha de Vencimiento:** Para documentos con vigencia limitada
6. **Aprobar:** Cuando está listo, se bloquea para edición

### 16.4 Flujo de Aprobación

```
NO TRABAJADO (NT)  -->  EN DESARROLLO (ED)  -->  APROBADO (AP)
     │                       │                        │
     │                       │                        │
  Editable              Editable                Solo Admin
  por todos            por asignados            puede editar
```

---

## 17. GENERACIÓN DE DOCUMENTOS CON IA

El sistema permite generar documentos de soporte usando ChatGPT:

1. Ir al criterio que desea documentar
2. Clic en **"Generar con IA"**
3. Escribir instrucciones, por ejemplo:
   - "Genera un procedimiento para verificación de títulos de personal de salud"
   - "Crea un formato de seguimiento de limpieza y desinfección"
   - "Elabora un protocolo de manejo de historias clínicas"
4. El sistema generará el documento en formato HTML editable
5. Revisar y modificar según necesidades específicas

**Nota:** Requiere configurar la API Key de OpenAI en el archivo `.env`:
```
OPENAI_API_KEY=sk-tu-api-key-aqui
```

---

**Versión del Sistema:** 1.0
**Fecha:** Enero 2026
**Basado en:** Resolución 3100 de 2019 - MinSalud Colombia
