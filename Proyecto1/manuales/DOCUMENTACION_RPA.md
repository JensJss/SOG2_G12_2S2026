# Documentación del proyecto RPA: RPAGeren2

**Autor:** Integrante 1
**Herramienta:** UiPath Studio (proyecto `RPAGeren2`, flujo principal `Main.xaml`)
**Sistema destino:** Odoo (`http://3.231.215.139/odoo`)

---

## Índice

1. [Enunciado del problema](#1-enunciado-del-problema)
2. [Objetivo de la automatización](#2-objetivo-de-la-automatización)
3. [Requisitos y entorno](#3-requisitos-y-entorno)
4. [Estructura del proyecto y de los datos](#4-estructura-del-proyecto-y-de-los-datos)
5. [Visión general del flujo](#5-visión-general-del-flujo)
6. [Paso a paso del flujo `Main.xaml`](#6-paso-a-paso-del-flujo-mainxaml)
   - [6.1 Variables](#61-variables)
   - [6.2 Inicialización (Asignación múltiple)](#62-inicialización-asignación-múltiple)
   - [6.3 Preparar carpeta de salida](#63-preparar-carpeta-de-salida)
   - [6.4 Recorrido de carpetas, archivos y hojas](#64-recorrido-de-carpetas-archivos-y-hojas)
   - [6.5 Tratamiento de la hoja "clientes"](#65-tratamiento-de-la-hoja-clientes)
   - [6.6 Tratamiento de la hoja "productos"](#66-tratamiento-de-la-hoja-productos)
   - [6.7 Validación y limpieza de clientes](#67-validación-y-limpieza-de-clientes)
   - [6.8 Validación y limpieza de productos](#68-validación-y-limpieza-de-productos)
   - [6.9 Archivo de errores](#69-archivo-de-errores)
   - [6.10 Generación de los consolidados](#610-generación-de-los-consolidados)
   - [6.11 Carga automática a Odoo](#611-carga-automática-a-odoo)
7. [Archivos de salida](#7-archivos-de-salida)
8. [Problemas encontrados y cómo se resolvieron](#8-problemas-encontrados-y-cómo-se-resolvieron)
9. [Cómo ejecutar el robot](#9-cómo-ejecutar-el-robot)
10. [Limitaciones y riesgos conocidos](#10-limitaciones-y-riesgos-conocidos)
11. [Anexo: código de las actividades "Invocar código"](#11-anexo-código-de-las-actividades-invocar-código)

---

## 1. Enunciado del problema

> El departamento de ventas creó una jerarquía inicialmente poco práctica de carpetas (clientes, proveedores, reclamos, registro, productos) seguido de un guion y descripción adicional; de igual manera fueron nombrados los archivos Excel. Dentro de estos archivos se encuentran varias hojas con información adicional, pero tuvieron el cuidado de nombrar correctamente qué hojas tienen los (clientes, proveedor, reclamos, registros, productos). La empresa está interesada únicamente en todos los archivos que contengan una hoja llamada **"clientes"** y **"productos"**.

En resumen:

- Hay carpetas con nombres del tipo `clientes - prueba`, `productos - lo que sea`, etc.
- Dentro hay archivos Excel (`.xlsx` o `.xls`) con nombres del mismo estilo.
- Cada archivo puede tener varias hojas; solo interesan las hojas llamadas `clientes` y `productos`.
- La información de esas hojas debe consolidarse, limpiarse y cargarse en Odoo.

## 2. Objetivo de la automatización

El robot hace, sin intervención humana:

1. **Busca** todas las carpetas y archivos que siguen el patrón `<tipo> - <descripción>`.
2. **Lee** únicamente las hojas `clientes` y `productos` de cada archivo.
3. **Normaliza** los datos: limpia encabezados, quita filas vacías, ajusta formatos y valores.
4. **Valida** los campos obligatorios y separa las filas con errores.
5. **Elimina duplicados** usando un identificador externo (External ID).
6. **Genera** tres archivos de salida:
   - `clientes_consolidado.xlsx`
   - `productos_consolidado.xlsx` (compatible con la plantilla oficial de Odoo)
   - `errores.xlsx` (solo si hubo errores)
7. **Carga** los dos consolidados en Odoo usando la pantalla de "Importar registros", controlando Chrome.

## 3. Requisitos y entorno

| Elemento | Valor |
|---|---|
| UiPath Studio | 2026 (`studioVersion` 26.0.203.0) |
| Lenguaje de expresiones | Visual Basic |
| Framework | Windows |
| Paquete `UiPath.Excel.Activities` | 3.5.1 |
| Paquete `UiPath.System.Activities` | 26.8.2 |
| Paquete `UiPath.UIAutomation.Activities` | 26.10.5 |
| Microsoft Excel | Instalado (lo usan las actividades modernas de Excel) |
| Navegador | Google Chrome con la extensión de UiPath |
| Odoo | Servidor `http://3.231.215.139`, con sesión iniciada en Chrome |

> **Importante:** antes de ejecutar, Chrome debe tener una sesión iniciada en Odoo. El robot no hace login.

## 4. Estructura del proyecto y de los datos

```
RPAGeren2/
├── Main.xaml                  ← flujo principal (todo el robot)
├── project.json               ← dependencias y configuración
├── DOCUMENTACION_RPA.md       ← este documento
├── .objects/                  ← Repositorio de objetos (elementos de UI de Odoo)
└── data/
    ├── clientes - prueba/
    │   └── clientes-archivo de ejemplo.xlsx      (hoja "clientes")
    ├── productos - prueba/
    │   └── productos - archivo de ejemplo.xls    (hoja "productos")
    ├── otros/
    │   └── prueba.xlsx                           (se ignora: no cumple el patrón)
    ├── salida - esperada/
    │   └── plantilla_productos.xls               (plantilla oficial de Odoo, referencia)
    └── salida/                                   ← lo genera el robot
        ├── clientes_consolidado.xlsx
        ├── productos_consolidado.xlsx
        └── errores.xlsx
```

**Regla del patrón.** Una carpeta o archivo se procesa solo si su nombre cumple esta expresión regular (sin distinguir mayúsculas):

```
^(clientes|proveedores|reclamos|registros?|productos)\s*-\s*.+$
```

- `clientes - prueba` ✅
- `productos - archivo de ejemplo` ✅
- `clientes-archivo de ejemplo` ✅ (los espacios alrededor del guion son opcionales)
- `otros` ❌
- `salida - esperada` ❌ (no empieza con un tipo válido)

<!-- IMAGEN 1: Captura del explorador de archivos mostrando la carpeta data/ con sus subcarpetas -->
> 📷 **[Imagen 1 – Estructura de carpetas en `data/`]**

## 5. Visión general del flujo

```
Main Sequence
│
├─ 1. Asignación múltiple ............ inicializa tablas y busca carpetas válidas
├─ 2. Preparar carpeta salida ........ crea data\salida y borra salidas anteriores
│
├─ 3. Alcance del proceso de Excel
│   ├─ For Each carpeta
│   │   └─ For Each archivo
│   │       └─ Utilice el archivo de Excel
│   │           └─ Para cada hoja de Excel
│   │               ├─ Si la hoja es "clientes"  → leer, normalizar, fusionar
│   │               └─ Si la hoja es "productos" → leer, normalizar, fusionar
│   │
│   ├─ Validar campos requeridos (clientes)
│   ├─ Generar ID externo y quitar duplicados (clientes)
│   ├─ Validar campos requeridos productos
│   ├─ Normalizar tipo y quitar duplicados productos
│   ├─ Si hay errores → escribir errores.xlsx
│   ├─ Quitar columna Origen (clientes) → escribir clientes_consolidado.xlsx
│   ├─ Ajustar columnas a plantilla productos → escribir productos_consolidado.xlsx
│   └─ Registrar mensaje (resumen)
│
└─ 4. Para cada carga a Odoo (clientes, productos)
    └─ Si hay datos para cargar
        └─ Chrome Odoo
            ├─ Ir a importar (URL directa)
            ├─ Clic "Subir archivo de datos"
            ├─ Escribir ruta completa en el diálogo "Abrir"
            ├─ Clic "Abrir"
            └─ Clic "Importar" (con pausas)
```

<!-- IMAGEN 2: Captura de Main.xaml en UiPath Studio con las actividades principales colapsadas -->
> 📷 **[Imagen 2 – Vista general de `Main.xaml` en UiPath Studio]**

## 6. Paso a paso del flujo `Main.xaml`

### 6.1 Variables

Todas están declaradas en `Main Sequence`:

| Variable | Tipo | Uso |
|---|---|---|
| `rutaData` | `String` | Carpeta de datos. Valor por defecto: `If(Directory.Exists("data"), "data", "..\data")`, así funciona tanto desde la raíz del proyecto como desde una subcarpeta. |
| `patron` | `String` | Expresión regular para reconocer carpetas y archivos válidos (ver sección 4). |
| `carpetas` | `String[]` | Carpetas de `data` que cumplen el patrón. |
| `archivos` | `String[]` | Archivos Excel válidos dentro de la carpeta actual. |
| `dt_ClientesHoja` | `DataTable` | Datos de una hoja `clientes` (temporal). |
| `dt_ClientesTotal` | `DataTable` | Todos los clientes consolidados. |
| `dt_ProductosHoja` | `DataTable` | Datos de una hoja `productos` (temporal). |
| `dt_ProductosTotal` | `DataTable` | Todos los productos consolidados. |
| `dt_Errores` | `DataTable` | Filas rechazadas, con columnas `Tipo`, `Origen` y `Detalle`. |

### 6.2 Inicialización (Asignación múltiple)

Actividad **Asignación múltiple**:

| Destino | Valor |
|---|---|
| `dt_ClientesTotal` | `New DataTable` |
| `dt_Errores` | `New DataTable` |
| `dt_ProductosTotal` | `New DataTable` |
| `carpetas` | `Directory.GetDirectories(rutaData).Where(Function(d) Regex.IsMatch(Path.GetFileName(d), patron, RegexOptions.IgnoreCase)).ToArray()` |

Las tablas se crean vacías para que **Fusionar tabla de datos** pueda agregarles columnas y filas después.

### 6.3 Preparar carpeta de salida

Actividad **Invocar código** "Preparar carpeta salida", con el argumento `rutaSalida = Path.Combine(rutaData, "salida")`:

- Crea `data\salida` si no existe.
- Borra `errores.xlsx`, `clientes_consolidado.xlsx` y `productos_consolidado.xlsx` si existen.

**¿Por qué?** Si una ejecución anterior escribió más filas que la actual, *Escribir rango* no borra las filas viejas que sobran. Empezar con archivos nuevos evita mezclar datos de ejecuciones distintas.

> ⚠️ Si alguno de esos archivos está abierto en Excel, no se puede borrar y el robot se detiene. Hay que cerrarlos antes de ejecutar.

### 6.4 Recorrido de carpetas, archivos y hojas

Todo ocurre dentro de **Alcance del proceso de Excel**, que mantiene una sola instancia de Excel durante todo el procesamiento (más rápido y estable).

1. **For Each carpeta** en `carpetas`.
2. **Asignar** `archivos` con los archivos de la carpeta que:
   - tengan extensión `.xlsx` o `.xls`;
   - no sean archivos temporales de Excel (los que empiezan con `~$`);
   - cumplan el patrón en su nombre (sin extensión).

   ```vb
   Directory.GetFiles(carpeta, "*.xls*").Where(Function(f) (Path.GetExtension(f).Equals(".xlsx", StringComparison.OrdinalIgnoreCase) OrElse Path.GetExtension(f).Equals(".xls", StringComparison.OrdinalIgnoreCase)) AndAlso Not Path.GetFileName(f).StartsWith("~$") AndAlso Regex.IsMatch(Path.GetFileNameWithoutExtension(f), patron, RegexOptions.IgnoreCase)).ToArray()
   ```
3. **For Each archivo** en `archivos`.
4. **Utilice el archivo de Excel** con `archivo` (referencia: `archivo_excel`).
5. **Para cada hoja de Excel** en `archivo_excel` (variable de la hoja: `hoja`).
6. Se compara el nombre de la hoja **sin espacios y sin distinguir mayúsculas**:
   - `hoja.Name.Trim().Equals("clientes", StringComparison.OrdinalIgnoreCase)` → rama de clientes.
   - `hoja.Name.Trim().Equals("productos", StringComparison.OrdinalIgnoreCase)` → rama de productos.
   - Cualquier otra hoja (proveedores, reclamos, etc.) se ignora.

### 6.5 Tratamiento de la hoja "clientes"

Dentro de **Si la hoja es clientes → Then**:

1. **Leer rango**: lee toda la hoja (`Range = hoja`) a `dt_ClientesHoja`, con encabezados.
2. **Invocar código** (normalización de clientes). Argumentos:
   - `dt` (entrada/salida) = `dt_ClientesHoja`
   - `origen` (entrada) = `Path.GetFileName(archivo) + " | " + hoja.Name`

   Este código:
   - Quita los asteriscos y espacios de los encabezados (`Name*` → `Name`).
   - Traduce nombres técnicos de Odoo a los encabezados de la plantilla: `name→Name`, `is_company→Company Type`, `company_name→Related Company`, `vat→Tax ID`, `country_id→Country`, `state_id→State`, `zip→Zip`, `city→City`, `street→Street`, `street2→Street2`, `phone→Phone`, `email→Email`.
   - Elimina las filas totalmente vacías.
   - Agrega la columna `Origen` con el nombre del archivo y la hoja, para rastrear de dónde salió cada fila (por ejemplo `clientes-archivo de ejemplo.xlsx | clientes`).
3. **Fusionar tabla de datos**: agrega `dt_ClientesHoja` a `dt_ClientesTotal` con `MissingSchemaAction = Add`, para que las columnas nuevas se agreguen automáticamente.

### 6.6 Tratamiento de la hoja "productos"

Dentro de **Si la hoja es productos → Then** (secuencia "Productos"):

1. **Leer rango productos**: lee la hoja a `dt_ProductosHoja`.
2. **Normalizar hoja productos** (Invocar código), con los mismos argumentos `dt` y `origen`. Este código:
   - **Limpia encabezados** (quita `*` y espacios).
   - **Traduce encabezados alternativos** a los de la plantilla de Odoo, por ejemplo:
     - `Nombre`, `name` → `Name`
     - `Tipo`, `Tipo de producto`, `detailed_type` → `Product Type`
     - `Referencia interna`, `default_code` → `Internal Reference`
     - `Código de barras` → `Barcode`
     - `Precio de venta`, `list_price` → `Sales Price`
     - `Costo`, `standard_price` → `Cost`
     - `Peso` → `Weight`
     - `Descripción de venta` → `Sales Description`
     - `id`, `ID externo` → `External ID`
   - **Convierte todos los valores a texto** con formato invariante (punto decimal). Así **Fusionar tabla de datos** no falla cuando dos archivos traen la misma columna con tipos distintos (número en uno, texto en otro), y Odoo recibe los números siempre con punto.
   - **Corrige el código de barras**: Excel guarda los códigos de barras como números, y en el archivo de ejemplo `54398267125` venía como `54398267125.00001`. Si el valor es numérico, se redondea y se escribe sin decimales.
   - **Elimina filas vacías.**
   - **Agrega la columna `Origen`.**
3. **Fusionar productos**: agrega `dt_ProductosHoja` a `dt_ProductosTotal`.

**Comparación entre el archivo de entrada y la plantilla de Odoo:**

| Columna del archivo de entrada | ¿Está en la plantilla? | Qué hace el robot |
|---|---|---|
| External ID | ✅ (obligatoria) | Se valida, se usa para quitar duplicados y se exporta como `id` |
| Name | ✅ (obligatoria) | Se valida |
| Product Type | ✅ (obligatoria) | Se valida y se normaliza (`Goods`/`Service`/`Combo`) |
| Internal Reference | ✅ | Se conserva |
| Barcode | ✅ | Se corrige el formato |
| Sales Price | ✅ | Se conserva |
| Cost | ✅ | Se conserva |
| Weight | ✅ | Se conserva |
| Sales Description | ✅ | Se conserva |
| Product Values | ❌ | Se descarta (venía vacía) |
| Cantidad a la mano | ❌ | Se descarta (en Odoo el stock se carga con un ajuste de inventario, no en la ficha del producto) |
| Está publicado | ❌ | Se descarta |

### 6.7 Validación y limpieza de clientes

Después de recorrer todas las carpetas:

**a) Validar campos requeridos** (Invocar código). Argumentos:

| Argumento | Dirección | Valor |
|---|---|---|
| `dt` | Entrada/Salida | `dt_ClientesTotal` |
| `dtErrores` | Entrada/Salida | `dt_Errores` |
| `requeridas` | Entrada | `New String() {"Name", "Company Type"}` |
| `tipo` | Entrada | `"clientes"` |

- Si `dt_Errores` aún no tiene columnas, crea `Tipo`, `Origen` y `Detalle`.
- Recorre las filas **de abajo hacia arriba**, para poder borrar sin saltarse filas.
- Si a una fila le falta algún campo requerido, la registra en `dt_Errores` (`Falta: Name, ...`) y la quita de la tabla.

**b) Generar ID externo y quitar duplicados** (Invocar código):

- Agrega la columna `id` como primera columna.
- Para cada cliente arma un identificador a partir del **nombre**:
  1. pasa a minúsculas;
  2. quita acentos (`José Pérez` → `jose perez`);
  3. reemplaza todo lo que no sea letra o número por `_`;
  4. antepone `cliente_`.

  Ejemplo: `PRUEBA SS 1` → `cliente_prueba_ss_1`.
- Si el ID ya apareció antes en el consolidado, la fila se registra como `Duplicado` en errores y se elimina.

**¿Por qué un ID externo?** Odoo usa la columna `id` (ID externo) para saber si un registro ya existe. Sin ella, **cada importación crea contactos nuevos**, y si el robot se ejecuta dos veces el cliente queda duplicado. Con ella, la segunda importación **actualiza** el contacto existente.

**¿Por qué solo el nombre?** La mayoría de clientes solo trae nombre y tipo. Si el ID dependiera del email o de la referencia, al agregar un email más adelante el ID cambiaría y Odoo crearía un duplicado. Usando siempre el nombre, el ID es estable.

### 6.8 Validación y limpieza de productos

**a) Validar campos requeridos productos**: es el mismo código de 6.7a, con:
- `dt` = `dt_ProductosTotal`
- `requeridas` = `New String() {"External ID", "Name", "Product Type"}`
- `tipo` = `"productos"`

**b) Normalizar tipo y quitar duplicados productos** (Invocar código):
- Normaliza `Product Type` a los valores que acepta Odoo:

  | Valor en el archivo | Se convierte en |
  |---|---|
  | goods, bienes, bien, producto, product, consumible, consu, almacenable, storable | `Goods` |
  | service, servicio | `Service` |
  | combo | `Combo` |

- Si el tipo no se reconoce, la fila va a errores (`Product Type no válido: ...`).
- Si el `External ID` se repite, la segunda fila va a errores como `Duplicado` y se elimina.

En productos el External ID **ya viene en el archivo** (por ejemplo `PRUEBA_PRODUCT_SS_1`), así que no hace falta generarlo.

### 6.9 Archivo de errores

**Si hay errores** (`dt_Errores.Rows.Count > 0`):
- **Usar archivo de Excel** sobre `data\salida\errores.xlsx`.
- **Escribir rango** de `dt_Errores` en la hoja `errores`, con encabezados.

Ejemplo de contenido:

| Tipo | Origen | Detalle |
|---|---|---|
| clientes | clientes-archivo de ejemplo.xlsx \| clientes | Falta: Company Type |
| productos | productos - archivo de ejemplo.xls \| productos | Duplicado: PRUEBA_PRODUCT_SS_3 |

### 6.10 Generación de los consolidados

**Clientes:**
1. **Quitar columna Origen**: `Origen` solo sirve para trazabilidad y Odoo no la reconoce.
2. **Usar archivo de Excel** sobre `data\salida\clientes_consolidado.xlsx`, luego **Escribir rango** de `dt_ClientesTotal` en la hoja `clientes`, con encabezados.

**Productos:**
1. **Ajustar columnas a plantilla productos** (Invocar código):
   - Deja solo las 9 columnas de la plantilla, **en el mismo orden**: `External ID, Name, Product Type, Internal Reference, Barcode, Sales Price, Cost, Weight, Sales Description`. Si alguna falta, la crea vacía.
   - Renombra `External ID` a **`id`** (ver problema 8.8).
2. **Usar archivo de Excel** sobre `data\salida\productos_consolidado.xlsx`, luego **Escribir rango** de `dt_ProductosTotal` en la hoja `productos`.

**Registrar mensaje** (nivel Info):

```
Clientes consolidados: 4 | Productos consolidados: 7 | Errores: 0
```

<!-- IMAGEN 3: Captura de productos_consolidado.xlsx abierto en Excel -->
> 📷 **[Imagen 3 – `productos_consolidado.xlsx` generado por el robot]**

### 6.11 Carga automática a Odoo

**Para cada carga a Odoo** recorre una lista de dos elementos. Cada elemento es un `String()` con `{nombre, url de importación, ruta completa del archivo, cantidad de filas}`:

| # | Nombre | URL de importación | Archivo |
|---|---|---|---|
| 1 | clientes | `http://3.231.215.139/odoo/contacts/import?active_model=res.partner` | `data\salida\clientes_consolidado.xlsx` |
| 2 | productos | `http://3.231.215.139/odoo/action-498/import?active_model=product.template` | `data\salida\productos_consolidado.xlsx` |

En cada vuelta (variable `carga`):

1. **Si hay datos para cargar**: `CInt(carga(3)) > 0 AndAlso File.Exists(carga(2))`. Si no hay datos, registra una advertencia ("No hay ... para cargar en Odoo") y pasa a la siguiente vuelta.
2. **Chrome Odoo** (Usar aplicación/navegador):
   - Selector: `<html app='chrome.exe' url='*3.231.215.139*' />`. Se engancha a **cualquier pestaña** del servidor de Odoo, sin importar en qué página esté.
   - Si Chrome no está abierto, lo abre en la URL de importación.
3. **Ir a importar** (Ir a URL): va directo a `carga(1)`, la pantalla de importación del modelo correspondiente.
4. **Clic "Subir archivo de datos"**. Selector: `<webctrl aaname='Subir archivo de datos' tag='BUTTON' />`.
5. **Escribir en "Nombre de archivo"** (diálogo "Abrir" de Windows): escribe `carga(2)`, que es la **ruta completa** del archivo.
6. **Clic "Abrir"** en el diálogo de Windows.
7. **Clic "Importar"**. Selector: `<webctrl aaname='Importar' tag='BUTTON' />`, con:
   - **DelayBefore = 3 s**: espera a que Odoo termine de leer el archivo y emparejar las columnas.
   - **DelayAfter = 5 s**: deja terminar la importación antes de cerrar el ámbito del navegador.

Como la pantalla de importación de Odoo es la misma para todos los modelos, **las mismas actividades sirven para clientes y para productos**; solo cambian la URL y el archivo.

<!-- IMAGEN 4: Captura de la pantalla de importación de Odoo con el archivo cargado y las columnas emparejadas -->
> 📷 **[Imagen 4 – Pantalla de importación de Odoo con columnas emparejadas]**

<!-- IMAGEN 5: Captura de la lista de productos/contactos en Odoo después de la importación -->
> 📷 **[Imagen 5 – Registros importados en Odoo]**

## 7. Archivos de salida

| Archivo | Hoja | Contenido | Cuándo se genera |
|---|---|---|---|
| `data\salida\clientes_consolidado.xlsx` | `clientes` | `id` + columnas de clientes (Name, Company Type, Email, …) | Siempre |
| `data\salida\productos_consolidado.xlsx` | `productos` | `id, Name, Product Type, Internal Reference, Barcode, Sales Price, Cost, Weight, Sales Description` | Siempre |
| `data\salida\errores.xlsx` | `errores` | `Tipo, Origen, Detalle` | Solo si hubo errores |

Resultado con los archivos de prueba: **4 clientes**, **7 productos**, **0 errores**.

## 8. Problemas encontrados y cómo se resolvieron

### 8.1 `dt_Errores` declarada como `String`
- **Síntoma:** el flujo no compilaba porque se asignaba `New DataTable` a una variable `String`.
- **Solución:** se cambió el tipo de `dt_Errores` a `DataTable`.

### 8.2 "Invocar código" de normalización sin argumentos
- **Síntoma:** el código usaba `dt` y `origen`, pero la actividad no tenía argumentos definidos.
- **Solución:** se agregaron `dt` (entrada/salida) = `dt_ClientesHoja` y `origen` (entrada) = `Path.GetFileName(archivo) + " | " + hoja.Name`.

### 8.3 Error BC36639 al validar
- **Mensaje:** `error BC36639: El parámetro 'dt' de 'ByRef' no se puede usar en una expresión lambda.`
- **Causa:** los argumentos de entrada/salida de *Invocar código* se pasan por referencia (`ByRef`), y Visual Basic no permite usarlos dentro de un `Function(...)`.
- **Solución:** copiar el argumento a una variable local al inicio (`Dim tabla As DataTable = dt`) y usar `tabla` dentro de la lambda. Ambas apuntan a la misma tabla, así que los cambios se reflejan igual.

### 8.4 Filas viejas en los archivos de salida
- **Síntoma:** si una ejecución tenía menos filas que la anterior, quedaban filas antiguas al final.
- **Solución:** el paso "Preparar carpeta salida" borra los archivos de salida al inicio.

### 8.5 El clic en "Contactos" no funcionaba
- **Causas:**
  1. El ámbito de Chrome buscaba la pestaña por el título exacto `Bandeja de entrada`. Si Chrome estaba en otra página de Odoo, no la encontraba.
  2. El enlace "Contactos" está dentro del menú de aplicaciones, que el robot no abría.
  3. "Importar registros" está dentro del menú del engranaje, que tampoco se abría, y su selector (`menuitem`/`SPAN`) era demasiado genérico.
- **Solución:** se reemplazó toda la navegación por menús con **Ir a URL** directo a la página de importación, y el ámbito ahora busca cualquier pestaña cuyo URL contenga `3.231.215.139`.

### 8.6 Carga poco robusta del archivo
- **Problemas:**
  - En el diálogo "Abrir" solo se escribía el nombre del archivo, así que dependía de la última carpeta usada en Windows.
  - "Subir archivo de datos" e "Importar" tenían el mismo selector genérico (`<webctrl tag='BUTTON' type='button' />`), que coincide con el primer botón de la página.
- **Solución:** se escribe la ruta completa del archivo, y cada botón se identifica por su texto (`aaname`).

### 8.7 El botón "Importar" no hacía nada (solo funcionaba con breakpoint)
- **Causa:** al abrir el archivo, Odoo muestra una capa de "cargando" mientras lee el Excel y empareja las columnas. El botón ya existía, así que UiPath hacía clic al instante, pero el clic caía sobre esa capa y se perdía. Con el breakpoint, Odoo alcanzaba a terminar.
- **Solución:** `DelayBefore = 3` y `DelayAfter = 5` en "Clic 'Importar'".

### 8.8 Clientes y productos duplicados al importar dos veces (y error de código de barras)
- **Síntoma en clientes:** cada ejecución creaba los mismos contactos otra vez.
- **Síntoma en productos:** la segunda importación fallaba con "los códigos de barras ya fueron asignados".
- **Causa:** Odoo solo reconoce un registro existente por su **ID externo**. En clientes no había ID. En productos la columna se llamaba `External ID`, que Odoo en español no empareja automáticamente (espera `id` o "ID externo"). Por eso cada importación creaba productos nuevos, y el código de barras quedaba repetido.
- **Solución:**
  - Clientes: se genera la columna `id` a partir del nombre (sección 6.7b).
  - Productos: la columna se exporta con el nombre técnico **`id`**.
  - Limpieza única en Odoo: se eliminaron los registros de prueba creados antes sin ID externo. Archivarlos no basta, porque un producto archivado sigue ocupando su código de barras.

## 9. Cómo ejecutar el robot

1. Abrir Chrome e **iniciar sesión en Odoo** (`http://3.231.215.139/odoo`).
2. Colocar los archivos de entrada en `data\`, dentro de carpetas con el formato `<tipo> - <descripción>`.
3. **Cerrar** cualquier archivo de `data\salida\` que esté abierto en Excel.
4. Abrir el proyecto en UiPath Studio y ejecutar `Main.xaml` (**Ejecutar archivo**).
5. No usar el mouse ni el teclado mientras el robot interactúa con Chrome.
6. Revisar:
   - el panel de **Salida** (mensaje con el resumen);
   - `data\salida\errores.xlsx`, si existe;
   - Odoo, en Contactos y en Productos.

<!-- IMAGEN 6 (opcional): Panel de Salida de UiPath con el mensaje final -->
> 📷 **[Imagen 6 (opcional) – Mensaje final en el panel de Salida]**

## 10. Limitaciones y riesgos conocidos

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Dos clientes distintos con el mismo nombre | Se tratan como uno solo; el segundo queda en errores como "Duplicado" | Riesgo aceptado: la mayoría de clientes solo trae nombre |
| Cambiar el nombre de un cliente en el Excel | Odoo lo toma como un cliente nuevo | Corregir los nombres directamente en Odoo |
| Odoo lento o archivos muy grandes | "Importar" podría hacer clic antes de tiempo | Aumentar `DelayBefore` (5–6 s) |
| Código de barras ya usado por otro producto en Odoo | Odoo rechaza toda la importación | Eliminar o corregir el producto que lo tiene en Odoo |
| Archivos de salida abiertos en Excel | No se pueden borrar y el robot se detiene | Cerrarlos antes de ejecutar |
| Cambios en la interfaz de Odoo | Los selectores podrían dejar de funcionar | Volver a indicar el elemento en el Repositorio de objetos |
| Hoja vacía extra (`Hoja1`) en los consolidados | Odoo usa la primera hoja (`clientes`/`productos`), así que no afecta | Ninguna necesaria |

## 11. Anexo: código de las actividades "Invocar código"

### Preparar carpeta salida
```vb
Directory.CreateDirectory(rutaSalida)
For Each nombre As String In {"errores.xlsx", "clientes_consolidado.xlsx", "productos_consolidado.xlsx"}
    Dim ruta As String = Path.Combine(rutaSalida, nombre)
    If File.Exists(ruta) Then File.Delete(ruta)
Next
```

### Normalización de clientes (por hoja)
```vb
Dim mapa As New Dictionary(Of String, String)(StringComparer.OrdinalIgnoreCase) From {
  {"name","Name"},{"is_company","Company Type"},{"company_name","Related Company"},
  {"vat","Tax ID"},{"country_id","Country"},{"state_id","State"},{"zip","Zip"},
  {"city","City"},{"street","Street"},{"street2","Street2"},{"phone","Phone"},{"email","Email"}}

For Each c As DataColumn In dt.Columns
    c.ColumnName = c.ColumnName.Replace("*", "").Trim()
    If mapa.ContainsKey(c.ColumnName) Then c.ColumnName = mapa(c.ColumnName)
Next

For i As Integer = dt.Rows.Count - 1 To 0 Step -1
    If dt.Rows(i).ItemArray.All(Function(x) IsDBNull(x) OrElse x Is Nothing OrElse String.IsNullOrWhiteSpace(x.ToString)) Then dt.Rows.RemoveAt(i)
Next

dt.Columns.Add("Origen", GetType(String))
For Each r As DataRow In dt.Rows
    r("Origen") = origen
Next
```

### Normalizar hoja productos (por hoja)
```vb
Dim mapa As New Dictionary(Of String, String)(StringComparer.OrdinalIgnoreCase) From {
    {"id", "External ID"}, {"external id", "External ID"}, {"id externo", "External ID"},
    {"name", "Name"}, {"nombre", "Name"},
    {"product type", "Product Type"}, {"type", "Product Type"}, {"detailed_type", "Product Type"}, {"tipo", "Product Type"}, {"tipo de producto", "Product Type"},
    {"internal reference", "Internal Reference"}, {"default_code", "Internal Reference"}, {"referencia interna", "Internal Reference"}, {"referencia", "Internal Reference"},
    {"barcode", "Barcode"}, {"código de barras", "Barcode"}, {"codigo de barras", "Barcode"},
    {"sales price", "Sales Price"}, {"list_price", "Sales Price"}, {"precio de venta", "Sales Price"}, {"precio", "Sales Price"},
    {"cost", "Cost"}, {"standard_price", "Cost"}, {"costo", "Cost"}, {"coste", "Cost"},
    {"weight", "Weight"}, {"peso", "Weight"},
    {"sales description", "Sales Description"}, {"description_sale", "Sales Description"}, {"descripción de venta", "Sales Description"}, {"descripcion de venta", "Sales Description"}}

Dim nueva As New DataTable
For Each c As DataColumn In dt.Columns
    Dim nombre As String = c.ColumnName.Replace("*", "").Trim()
    If mapa.ContainsKey(nombre) Then nombre = mapa(nombre)
    If nueva.Columns.Contains(nombre) Then nombre = nombre & "_" & c.Ordinal.ToString
    nueva.Columns.Add(nombre, GetType(String))
Next

For Each r As DataRow In dt.Rows
    Dim valores(dt.Columns.Count - 1) As Object
    Dim tieneDatos As Boolean = False
    For j As Integer = 0 To dt.Columns.Count - 1
        Dim v As Object = r(j)
        Dim texto As String = ""
        If Not (IsDBNull(v) OrElse v Is Nothing) Then
            If TypeOf v Is IFormattable Then
                texto = CType(v, IFormattable).ToString(Nothing, System.Globalization.CultureInfo.InvariantCulture)
            Else
                texto = v.ToString
            End If
        End If
        texto = texto.Trim()
        If nueva.Columns(j).ColumnName = "Barcode" AndAlso texto <> "" Then
            Dim num As Double
            If Double.TryParse(texto, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, num) Then
                texto = Math.Round(num).ToString("0", System.Globalization.CultureInfo.InvariantCulture)
            End If
        End If
        If texto <> "" Then tieneDatos = True
        valores(j) = texto
    Next
    If tieneDatos Then nueva.Rows.Add(valores)
Next

nueva.Columns.Add("Origen", GetType(String))
For Each r As DataRow In nueva.Rows
    r("Origen") = origen
Next
dt = nueva
```

### Validar campos requeridos (clientes y productos)
```vb
If dtErrores.Columns.Count = 0 Then
    dtErrores.Columns.Add("Tipo") : dtErrores.Columns.Add("Origen") : dtErrores.Columns.Add("Detalle")
End If
Dim tabla As DataTable = dt
For i As Integer = tabla.Rows.Count - 1 To 0 Step -1
    Dim fila As DataRow = tabla.Rows(i)
    Dim faltan = requeridas.Where(Function(col) Not tabla.Columns.Contains(col) OrElse String.IsNullOrWhiteSpace(fila(col).ToString)).ToList()
    If faltan.Count > 0 Then
        dtErrores.Rows.Add(tipo, fila("Origen").ToString, "Falta: " & String.Join(", ", faltan))
        tabla.Rows.RemoveAt(i)
    End If
Next
```

### Generar ID externo y quitar duplicados (clientes)
```vb
Dim tabla As DataTable = dt
If Not tabla.Columns.Contains("id") Then
    tabla.Columns.Add("id", GetType(String)).SetOrdinal(0)
End If
Dim vistos As New HashSet(Of String)
Dim quitar As New List(Of DataRow)
For Each fila As DataRow In tabla.Rows
    Dim clave As String = fila("Name").ToString
    Dim normal As String = clave.Trim().ToLowerInvariant().Normalize(System.Text.NormalizationForm.FormD)
    normal = New String(normal.Where(Function(c) System.Globalization.CharUnicodeInfo.GetUnicodeCategory(c) <> System.Globalization.UnicodeCategory.NonSpacingMark).ToArray())
    normal = Regex.Replace(normal, "[^a-z0-9]+", "_").Trim("_"c)
    Dim idExterno As String = "cliente_" & normal
    If vistos.Contains(idExterno) Then
        dtErrores.Rows.Add(tipo, fila("Origen").ToString, "Duplicado: " & clave)
        quitar.Add(fila)
    Else
        vistos.Add(idExterno)
        fila("id") = idExterno
    End If
Next
For Each fila As DataRow In quitar
    tabla.Rows.Remove(fila)
Next
```

### Normalizar tipo y quitar duplicados productos
```vb
Dim tabla As DataTable = dt
Dim tipos As New Dictionary(Of String, String)(StringComparer.OrdinalIgnoreCase) From {
    {"goods", "Goods"}, {"bienes", "Goods"}, {"bien", "Goods"}, {"producto", "Goods"}, {"product", "Goods"},
    {"consumible", "Goods"}, {"consu", "Goods"}, {"almacenable", "Goods"}, {"storable", "Goods"},
    {"service", "Service"}, {"servicio", "Service"}, {"combo", "Combo"}}
Dim vistos As New HashSet(Of String)(StringComparer.OrdinalIgnoreCase)
Dim quitar As New List(Of DataRow)
For Each fila As DataRow In tabla.Rows
    Dim idExterno As String = fila("External ID").ToString.Trim()
    Dim tipoProducto As String = fila("Product Type").ToString.Trim()
    If Not tipos.ContainsKey(tipoProducto) Then
        dtErrores.Rows.Add(tipo, fila("Origen").ToString, "Product Type no válido: " & tipoProducto)
        quitar.Add(fila)
    ElseIf vistos.Contains(idExterno) Then
        dtErrores.Rows.Add(tipo, fila("Origen").ToString, "Duplicado: " & idExterno)
        quitar.Add(fila)
    Else
        vistos.Add(idExterno)
        fila("External ID") = idExterno
        fila("Product Type") = tipos(tipoProducto)
    End If
Next
For Each fila As DataRow In quitar
    tabla.Rows.Remove(fila)
Next
```

### Quitar columna Origen (clientes)
```vb
If dt.Columns.Contains("Origen") Then dt.Columns.Remove("Origen")
```

### Ajustar columnas a plantilla productos
```vb
Dim plantilla As String() = {"External ID", "Name", "Product Type", "Internal Reference", "Barcode", "Sales Price", "Cost", "Weight", "Sales Description"}
Dim tabla As DataTable = dt
For Each col As String In plantilla
    If Not tabla.Columns.Contains(col) Then tabla.Columns.Add(col, GetType(String))
Next
dt = tabla.DefaultView.ToTable(False, plantilla)
dt.Columns("External ID").ColumnName = "id"
```

---

*Documento elaborado por el **Integrante 1**.*
