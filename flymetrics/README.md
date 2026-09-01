# Flymetrics Command Center OS — API REST & Web Platform

Esta es la plataforma web y API REST oficial de **Flymetrics S.A.S.**, diseñada bajo **Clean Architecture** e implementada con **FastAPI**, **SQLAlchemy 2.0**, **Pydantic v2**, **MySQL**, y **Vanilla Javascript / CSS Premium**.

El sistema gestiona la agenda de vuelos de drones agrícolas, bitácoras RAC-100 de pilotos, entregables en Google Drive (SLA 24-48h), generación de informes técnicos en PDF con recomendaciones agronómicas, atención oficial por WhatsApp y la **Torre de Control Admin-Técnico**.

---

## 🛠️ Requisitos e Instalación Local

### 1. Clonación e Instalación de Dependencias
Asegúrese de estar en el directorio raíz del proyecto y tener Python 3.10+ instalado:

```bash
pip install -r requirements.txt
```

### 2. Configuración del Archivo `.env`
El proyecto ya cuenta con el archivo `.env` configurado para conectarse a su base de datos local `flymetrics_db` en el puerto 3306 usando el usuario `root` y la contraseña `miguepro`.

Variables de entorno principales:
* `DB_HOST`: Host de la base de datos (por defecto `localhost`)
* `DB_PORT`: Puerto (por defecto `3306`)
* `DB_NAME`: `flymetrics_db`
* `DB_USER`: `root`
* `DB_PASSWORD`: `miguepro`
* `JWT_SECRET`: Clave secreta para firmar tokens JWT

---

## 👑 Creación de Usuarios Administradores por CLI

Para crear un nuevo usuario con rol de **administrador** directamente en la base de datos desde la línea de comandos, ejecute cualquiera de los dos scripts CLI habilitados:

```bash
# Método 1: Comando CLI directo con argumentos
python create_admin_cli.py nuevo_admin@flymetrics.co MiContraseña123!

# Método 2: Menú interactivo seguro
python create_admin.py
```

---

## 🚀 Cómo Iniciar el Servidor Local

Ejecute el servidor web backend en segundo plano o consola:

```bash
python main.py
# o también:
python run_server.py
```

El servidor iniciará en `http://localhost:3000`.

### 🌐 Accesos a Paneles e Interfaces:
* **Panel Administrador (Torre Control)**: [http://localhost:3000/admin.html](http://localhost:3000/admin.html)
* **Panel del Cliente**: [http://localhost:3000/cliente.html](http://localhost:3000/cliente.html)
* **Portal del Técnico**: [http://localhost:3000/tecnico.html](http://localhost:3000/tecnico.html)
* **Documentación Swagger UI**: [http://localhost:3000/docs](http://localhost:3000/docs)

---

## 📋 Módulos y Flujo Operativo de la Plataforma

```
[1. Cliente: Agenda Servicio] ➔ [2. Admin-Técnico: Asigna Piloto + Dron] ➔ [3. Técnico: Check-in y Operación]
                                                                                     │
[6. Soporte WA & Auditoría] ◄── [5. Cliente: Abre Link Drive & PDF] ◄── [4. Técnico: Checkout + Link Drive]
```

### 1️⃣ Agendamiento y Cotización Directa (`/agenda`)
- El cliente registra su predio/finca y solicita el servicio deseado.
- El turno se crea en estado `Pendiente`.

### 2️⃣ Torre de Control & Monitoreo Admin-Técnico (`/admin.html`)
- Monitoreo individual de pilotos en tiempo real.
- Matriz de Ocupación Dron + Piloto anti-choque de horarios.
- Edición total de bitácoras, datos RAC-100, justificaciones y enlaces de Google Drive.
- Recálculo de rutas y reagendamiento en 1 clic.

### 3️⃣ Checkout Técnico & Bitácora RAC-100 (`/tecnico.html`)
- Registro de llegada ("Check-in") y cierre ("Checkout").
- Formulario con hectáreas, litros de insumo, agua, baterías, observaciones, **Recomendaciones Agronómicas** y el **Enlace de Google Drive / Nube**.

### 4️⃣ Entregables en Google Drive & Recomendaciones en PDF (`/entregables`)
- **Google Drive**: Evita la saturación del servidor alojando los mapas pesados en la nube.
- **Informe PDF Oficial**: Descarga directa del reporte técnico certificado que incluye la telemetría del vuelo, insumos y recomendaciones agronómicas firmadas.
- **Insignia SLA**: Indicador de tiempo estimado de entrega (24h - 48h).

### 5️⃣ Atención Oficial WhatsApp (`/cliente.html`)
- Canal de soporte directo a WhatsApp (`https://wa.me/573001234567`) para atención inmediata sin bucles de tickets lerdos.
