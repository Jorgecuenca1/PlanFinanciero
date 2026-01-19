# Usuarios del Sistema de Habilitacion

## Usuario Administrador (Super Admin)

| Campo | Valor |
|-------|-------|
| **Email** | admin@habilitacion.com |
| **Contrasena** | Admin123! |
| **Nombre** | Admin Sistema |
| **Rol** | SUPER (Super Administrador) |
| **Entidad** | Sin entidad asignada |
| **Permisos** | Acceso total al sistema, puede crear entidades y usuarios |

## Usuario Clinica (Admin de Entidad)

| Campo | Valor |
|-------|-------|
| **Email** | clinica@habilitacion.com |
| **Contrasena** | Clinica123! |
| **Nombre** | Usuario Clinica |
| **Rol** | ADMIN (Administrador de Entidad) |
| **Entidad** | CLINICA EJEMPLO SALUD S.A.S. |
| **Codigo REPS** | 50001234567 |
| **Permisos** | Gestion de su entidad, sedes y evaluaciones |

## Usuario Auditor (Solo Lectura)

| Campo | Valor |
|-------|-------|
| **Email** | auditor@habilitacion.com |
| **Contrasena** | Auditor123! |
| **Nombre** | Auditor Externo |
| **Rol** | AUDITOR (Solo lectura) |
| **Entidad** | CLINICA EJEMPLO SALUD S.A.S. |
| **Permisos** | Ver toda la informacion de la entidad, sin poder modificar |

---

## Acceso al Sistema

URL: http://127.0.0.1:8012/

### Funcionalidades por Rol

**SUPER (admin@habilitacion.com):**
- Crear/editar entidades
- Crear usuarios
- Ver todas las entidades
- Acceso al admin de Django

**ADMIN de Entidad (clinica@habilitacion.com):**
- Ver y editar su entidad
- Gestionar sedes
- Realizar evaluaciones de criterios
- Subir documentos
- Ver reportes de su entidad

**AUDITOR (auditor@habilitacion.com):**
- Ver toda la informacion de la entidad
- Ver evaluaciones y documentos
- NO puede modificar nada (solo lectura)
- Ideal para auditores externos o supervisores

---

## Modulos Proximos

- **SIAU** - Sistema de Informacion y Atencion al Usuario
- **RIAS** - Rutas Integrales de Atencion en Salud
- **PAMEC** - Programa de Auditoria para el Mejoramiento de la Calidad
