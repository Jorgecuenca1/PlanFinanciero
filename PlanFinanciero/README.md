# Sistema de Gestion del Plan Financiero de Ingresos

Sistema web desarrollado en Django para la administracion, control y trazabilidad de las modificaciones al Plan Financiero de Ingresos del Departamento.

## Caracteristicas

- **Catalogo de Rubros Presupuestales**: Gestion de la estructura presupuestal base
- **Registro de Movimientos**: Presupuesto inicial, adiciones, reducciones y traslados
- **Control de Saldos**: Validacion automatica para evitar saldos negativos
- **Kardex por Rubro**: Historia cronologica de todos los movimientos
- **Reportes**: Vista de ejecucion presupuestal y exportacion a Excel
- **Autenticacion**: Sistema de usuarios con registro e inicio de sesion

## Requisitos

- Python 3.10+
- Django 5.0+

## Instalacion

1. Clonar o descargar el proyecto

2. Crear entorno virtual:
```bash
python -m venv .venv
```

3. Activar entorno virtual:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

5. Ejecutar migraciones:
```bash
python manage.py migrate
```

6. Crear superusuario (opcional si no se ejecuto el script de datos):
```bash
python manage.py createsuperuser
```

7. Cargar datos de ejemplo (opcional):
```bash
python crear_datos_ejemplo.py
```

8. Ejecutar servidor de desarrollo:
```bash
python manage.py runserver
```

9. Acceder al sistema:
- URL: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin

## Credenciales por Defecto

Si ejecutaste el script de datos de ejemplo:
- **Usuario**: admin
- **Contrasena**: admin123

## Estructura del Proyecto

```
PlanFinanciero/
├── accounts/          # App de autenticacion (login, registro, perfil)
├── core/              # App principal (landing page)
├── planfinanciero/    # App de gestion financiera
│   ├── models.py      # Modelos: Rubro, Movimiento, FuenteFinanciacion
│   ├── views.py       # Vistas del dashboard y CRUD
│   ├── forms.py       # Formularios
│   └── admin.py       # Configuracion del admin
├── templates/         # Templates HTML
├── static/            # Archivos estaticos (CSS, JS)
├── config/            # Configuracion Django
└── manage.py
```

## Modulos Principales

### 1. Parametrizacion
- Gestion de Fuentes de Financiacion (ICLD, SGP, Regalias, etc.)
- Catalogo de Rubros Presupuestales

### 2. Operaciones
- Registro de Presupuesto Inicial
- Registro de Adiciones
- Registro de Reducciones
- Traslados entre rubros

### 3. Reportes
- Vista de Ejecucion Presupuestal
- Kardex por Rubro
- Exportacion a Excel (CSV)

## Reglas de Negocio Implementadas

1. **Calculo de Saldo**: Saldo = P.Inicial + Adiciones - Reducciones
2. **Control de Solvencia**: No se permiten reducciones mayores al saldo disponible
3. **Integridad**: Los movimientos no se eliminan, solo se anulan para mantener trazabilidad
4. **Proteccion de Datos**: No se permite modificar el codigo de un rubro con movimientos

## Tecnologias Utilizadas

- Django 5.x
- Bootstrap 5.3
- Bootstrap Icons
- SQLite (desarrollo)

## Licencia

Proyecto desarrollado para gestion financiera publica.
