# CotizAPI 🤖💸🐂

CotizAPI es un bot de Telegram diseñado para ofrecer información actualizada sobre precios de activos financieros clave, como oro, plata, bitcoin, trigo y petróleo. Este sistema combina tecnologías modernas para proporcionar una API eficiente, fácil de usar y completamente automatizada para consultar precios, generar alertas y manejar datos históricos.

## **✨ Características del proyecto**

- **📊 Consulta de precios actuales**: Permite obtener los precios en tiempo real de activos financieros.
- **🔔 Alertas automáticas**: Genera notificaciones basadas en cambios significativos en los precios.
- **📈 Historial de precios**: Almacena y permite consultar precios históricos para análisis comparativos.
- **📅 Variación diaria y semanal**: Calcula automáticamente la variación en los precios respecto a días o semanas anteriores.
- **⏰ Programación automática**: Actualiza los precios de los activos de manera periódica mediante un programador de tareas.
- **🌍 Soporte a múltiples activos**: Actualmente soporta oro, plata, bitcoin, trigo y petróleo, pero es fácilmente escalable para incluir más activos.
- **🚀 API REST rápida**: Diseñada con FastAPI para ofrecer una interfaz eficiente y fácil de integrar.

## **🛠️ Tecnologías utilizadas**

El proyecto se construyó utilizando un conjunto de herramientas modernas que aseguran su eficiencia y facilidad de despliegue:

1. **🌐 Vercel**: Para el despliegue y hosting de la API, asegurando alta disponibilidad y rendimiento.
2. **🐙 GitHub**: Para el control de versiones y la colaboración en el desarrollo del código.
3. **📬 Postman**: Para realizar pruebas exhaustivas de las rutas y funcionalidades de la API.
4. **⚡ FastAPI**: Framework ligero y rápido para el desarrollo de la API REST.
5. **💾 SQLite (DB Browser for SQLite)**: Base de datos ligera y embebida, utilizada para almacenar precios históricos y alertas generadas.
6. **🖥️ DBeaver**: Herramienta gráfica para gestionar y consultar la base de datos SQLite.
7. **⏲️ Programador de tareas**: Utilizado para automatizar la actualización de precios y la generación de alertas.

## **📋 Arquitectura del sistema**

CotizAPI utiliza dos tablas principales en su base de datos:
1. **📁 Tabla de precios**: Registra los precios de los activos con su fecha correspondiente.
2. **🔔 Tabla de alertas**: Almacena las alertas generadas basadas en cambios significativos en los precios.

## **🤝 Cómo funciona CotizAPI**

1. **🚀 Actualización de precios**:
   - Un programador de tareas automatiza la actualización diaria de precios en la base de datos.
   - Los precios de los activos se obtienen de fuentes externas y se almacenan en la tabla de precios.
2. **🔔 Generación de alertas**:
   - Cuando se detecta un cambio significativo en los precios, se genera una alerta en la tabla correspondiente.
3. **📲 Interacción con Telegram**:
   - Los usuarios pueden interactuar con el bot para consultar precios actuales, históricos y alertas recientes.
4. **📉 Análisis de variaciones**:
   - La API calcula las variaciones porcentuales diarias y semanales basándose en los datos almacenados.

## **🚀 Cómo desplegar el proyecto**

### **Requisitos previos**
- Python 3.10+
- SQLite
- Vercel CLI
- Git

### **Instalación**
1. Clona el repositorio:
   ```bash
   git clone https://github.com/RafaelRemoteDev/cotizAPI.git
   cd cotizAPI

## **📬 Contacto**
- **Correo:  _rmartinezomenaca@gmail.com_**

- **GitHub: _RafaelRemoteDev_**