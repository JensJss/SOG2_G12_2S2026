# Plan de Distribución de Actividades y Responsabilidades - Proyecto QuetzalMart
**Curso:** Sistemas Organizacionales y Gerenciales 2  
**Universidad de San Carlos de Guatemala - Facultad de Ingeniería**  

---

## Integrante 1: Responsable del Sistema de Gestión Documental y Apoyo de Datos
*Enfoque: Repositorio centralizado, control normativo y etiquetado de archivos.*

### Responsabilidades y Actividades:
1. **Implementación del Gestor Documental:** Configurar e integrar el módulo de gestión documental con el ERP (Odoo).
2. **Carga de Documentos Esenciales:** Subir y clasificar correctamente los archivos requeridos:
   - Al menos 5 facturas de proveedores.
   - Al menos 5 contratos de outsourcing.
   - Al menos 5 contratos de empleados.
3. **Etiquetado y Categorización:** Establecer la estructura de etiquetas y categorías para asegurar un filtrado eficiente de la documentación.
4. **Apoyo en Carga Masiva ERP:** Colaborar con el Integrante 3 en la recolección, ordenamiento y estructuración de los datos maestros para las importaciones masivas.
5. **Redacción de Secciones de Documentación:** Apoyar en la redacción de los apartados del **Manual 1** y **Manual 2** referentes al uso del gestor documental y control de archivos.

---

## Integrante 2: Responsable de Analítica Web e Inteligencia de Negocio (Google Analytics)
*Enfoque: Métricas, comercio electrónico mejorado y visualización de datos.*

### Responsabilidades y Actividades:
1. **Configuración de Google Analytics (GA4):** Configurar GA4 bajo el modelo de comercio electrónico mejorado vinculado al portal web.
2. **Registro de Eventos Clave:** Asegurar y verificar el correcto disparo y registro de los eventos solicitados:
   - `view_item` (ver producto)
   - `add_to_cart` (agregar al carrito)
   - `begin_checkout` (finalizar compra y pago)
   - `purchase` (compra completada)
3. **Generación de Segmentos y Audiencias:**
   - Crear 3 segmentos de usuarios y 5 segmentos de eventos.
   - Configurar 3 audiencias, asegurando que al menos 1 sea personalizada.
4. **Informes de Exploración y Métricas:** Extraer métricas de tasa de conversión, adquisición de usuarios, ingresos totales, productos más vendidos y embudos de abandono de carrito.
5. **Elaboración del Manual 3:** Diseñar y redactar el **Manual 3** completo, integrando los gráficos de inteligencia de negocio derivados de Google Analytics.

---

## Integrante 3: Responsable del ERP (Módulos Administrativos: Empleados, Compras y Facturas)
*Enfoque: Gestión de recursos internos, inventarios de suministros y control fiscal.*

### Responsabilidades y Actividades:
1. **Configuración de la Base de Datos y ERP:** Asegurar la correcta implementación de Odoo y la base de datos relacional (MySQL/PostgreSQL/SQL Server) en la nube.
2. **Módulo de Empleados:** Ingresar al menos 35 empleados, distribuidos formalmente en 6 cargos y 5 departamentos de trabajo.
3. **Módulo de Compras y Suministros:**
   - Registrar al menos 100 compras realizadas junto con sus facturas correspondientes.
   - Ingresar al menos 60 materiales necesarios para el funcionamiento de las sucursales.
4. **Control de Facturas:** Gestionar y asegurar la generación de al menos 50 facturas (compras y ventas), organizándolas en una carpeta con sus respectivos archivos PDF comprobables.
5. **Preparación de Consultas SQL:** Estructurar y tener listas las consultas SQL necesarias para comprobar la existencia y veracidad de los datos en la base de datos durante la calificación.

---

## Integrante 4: Responsable del Portal Web, Módulo de Ventas y Marketing CRM
*Enfoque: Experiencia de usuario, comercio electrónico y automatización de campañas.*

### Responsabilidades y Actividades:
1. **Desarrollo del Portal Web (Tienda en Línea):** Implementar la plataforma de e-commerce con catálogo de productos detallado (imágenes, descripciones, precios), carrito de compras (cálculo de impuestos y envíos) y pasarela de pago segura.
2. **Integración Web-ERP-CRM:** Conectar el portal web con el ERP y el CRM para sincronizar pedidos, inventarios y relaciones con clientes.
3. **Módulo de Ventas en el ERP:** 
   - Ingresar al menos 150 ventas con distintos productos y clientes.
   - Ingresar al menos 20 cotizaciones a clientes y proveedores.
4. **Automatización de Marketing (CRM):** Configurar el envío automatizado de correos electrónicos desde el ERP. Garantizar que tras realizar una compra y enviar el recibo, el CRM envíe un segundo correo con la campaña de marketing con asunto diferenciado (sin usar correos personales).
5. **Simulación de Compra:** Apoyar al auxiliar durante la calificación ejecutando el registro y la compra en línea para validar la pasarela, el ERP y la recepción de correos.

---

## Integrante 5: Responsable de Automatización RPA (UiPath) y Documentación Técnica General
*Enfoque: Procesos automatizados, estructuración de datos externos y coordinación de manuales.*

### Responsabilidades y Actividades:
1. **Desarrollo del Flujo RPA en UiPath:** Diseñar el flujo automatizado para procesar la carpeta de archivos Excel con jerarquías y nombres específicos.
2. **Filtrado y Carga de Datos:** Programar el robot para extraer únicamente los datos de las hojas llamadas `"clientes"` (con campos específicos: Name, Company Type, Email, Phone, etc.) y `"productos"` (ID Externo, Name, Sales Price, Cost, etc.), cargándolos de forma centralizada a la base de datos.
3. **Ejecución en Calificación:** Demostrar en vivo el funcionamiento del robot UiPath, mostrando la carga de datos visualizable tanto en el sitio web como en consultas SQL.
4. **Coordinación y Redacción del Manual 1:** Redactar los pasos detallados de instalación del sistema, funcionamiento de módulos, capturas de carga masiva y la sección explicativa del RPA y sus ventajas.
5. **Coordinación y Redacción del Manual 2:** Crear todos los diagramas de flujo requeridos: visualización de UiPath, compras a proveedores, ventas, el flujo operativo completo de la empresa (recepción, almacenamiento, control de calidad, empaque, inventario) y el flujo del cliente web.

---
