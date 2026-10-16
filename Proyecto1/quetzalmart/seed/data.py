"""Datos maestros de QuetzalMart (Integrante 3: Empleados, Compras, Materiales, Facturas).

Todos los nombres, NIT, DPI, teléfonos y correos son FICTICIOS.
"""

COMPANY = {
    "name": "QuetzalMart, S.A.",
    "street": "6a. Avenida 12-45, Zona 9",
    "city": "Guatemala",
    "zip": "01009",
    "vat": "9876543-2",
    "phone": "+502 2300 4500",
    "email": "info@quetzalmart.gt",
    "website": "https://www.quetzalmart.gt",
    "company_registry": "Reg. Mercantil 123456",
}

# ------------------------------------------------------------------ Sucursales
# key: (nombre almacén, código, país, ciudad, dirección, teléfono)
BRANCHES = {
    "GT": ("QuetzalMart Guatemala (Central)", "GT", "gt", "Guatemala", "6a. Avenida 12-45, Zona 9", "+502 2300 4500"),
    "MX": ("QuetzalMart México", "MX", "mx", "Tapachula, Chiapas", "Av. Central Norte 210, Centro", "+52 962 625 1100"),
    "SV": ("QuetzalMart El Salvador", "SV", "sv", "San Salvador", "Blvd. de Los Héroes 1520", "+503 2260 7700"),
}

# ------------------------------------------------------------------ RR. HH.
DEPARTMENTS = [
    ("DIR", "Dirección General y Finanzas"),
    ("COM", "Compras y Logística"),
    ("OPS", "Operaciones de Sucursal"),
    ("VEN", "Ventas y Atención al Cliente"),
    ("MKT", "Marketing y Tecnología"),
]

# key: (nombre del cargo, departamento, salario base GTQ, descripción)
JOBS = {
    "GG":  ("Gerente General", "DIR", 25000, "Dirige la estrategia de la cadena y supervisa a los gerentes de sucursal."),
    "CON": ("Contador General", "DIR", 9000, "Registra facturas, conciliaciones bancarias y reportes fiscales."),
    "GS":  ("Gerente de Sucursal", "OPS", 14000, "Administra la operación diaria, el personal y los indicadores de su sucursal."),
    "CAJ": ("Cajero", "OPS", 4000, "Atiende el punto de venta, cobros y cierre de caja."),
    "AC":  ("Agente de Compras", "COM", 7500, "Cotiza, negocia y emite órdenes de compra a proveedores."),
    "BOD": ("Bodeguero", "COM", 4200, "Recibe, almacena y controla el inventario de mercadería y materiales."),
    "EV":  ("Ejecutivo de Ventas", "VEN", 6000, "Atiende clientes corporativos, cotizaciones y la tienda en línea."),
    "MK":  ("Analista de Marketing Digital", "MKT", 8000, "Gestiona campañas, redes sociales, correo y Google Analytics."),
}

# (nombre completo, cargo, sucursal, género)
EMPLOYEES = [
    # ---- Guatemala (16)
    ("Carlos Eduardo Méndez Ortiz", "GG", "GT", "male"),
    ("Ana Lucía Herrera Pineda", "GS", "GT", "female"),
    ("María José Castillo Barrios", "CON", "GT", "female"),
    ("Luis Fernando Ramírez Solís", "CON", "GT", "male"),
    ("Jorge Alejandro Morales Cifuentes", "AC", "GT", "male"),
    ("Andrea Sofía López Juárez", "AC", "GT", "female"),
    ("Pedro Antonio Xicará Tuch", "BOD", "GT", "male"),
    ("José Manuel Cux Chávez", "BOD", "GT", "male"),
    ("Edgar Rolando Pérez Cotí", "BOD", "GT", "male"),
    ("Gabriela Alejandra Monzón Ruiz", "CAJ", "GT", "female"),
    ("Karla Patricia Ajú Batz", "CAJ", "GT", "female"),
    ("Diana Marisol Quiñónez Lima", "CAJ", "GT", "female"),
    ("Rodrigo Andrés Estrada Paz", "EV", "GT", "male"),
    ("Valeria Beatriz Orellana Toledo", "EV", "GT", "female"),
    ("Daniel Esteban García Archila", "MK", "GT", "male"),
    ("Sofía Isabel Recinos Maldonado", "MK", "GT", "female"),
    # ---- México (10)
    ("Alejandro Hernández Vázquez", "GS", "MX", "male"),
    ("Fernanda Guadalupe Torres Rivas", "CON", "MX", "female"),
    ("Miguel Ángel Sánchez Domínguez", "AC", "MX", "male"),
    ("Juan Carlos Flores Medina", "BOD", "MX", "male"),
    ("Ricardo Iván Gómez Salazar", "BOD", "MX", "male"),
    ("Óscar Daniel Cruz Navarro", "BOD", "MX", "male"),
    ("Paola Itzel Martínez Cervantes", "CAJ", "MX", "female"),
    ("Ximena Montserrat Reyes Aguilar", "CAJ", "MX", "female"),
    ("Brenda Yesenia Luna Ortega", "CAJ", "MX", "female"),
    ("Arturo Emiliano Vargas Ponce", "EV", "MX", "male"),
    # ---- El Salvador (10)
    ("Roberto Ernesto Alvarado Menjívar", "GS", "SV", "male"),
    ("Claudia Marcela Rivas Hernández", "AC", "SV", "female"),
    ("Mauricio Antonio Guevara Portillo", "BOD", "SV", "male"),
    ("Kevin Alexander Mejía Ayala", "BOD", "SV", "male"),
    ("Gloria Esperanza Romero Flores", "CAJ", "SV", "female"),
    ("Katherine Michelle Cañas Aguilar", "CAJ", "SV", "female"),
    ("Wendy Carolina Lemus Escobar", "CAJ", "SV", "female"),
    ("Fernando José Chicas Henríquez", "EV", "SV", "male"),
    ("Raquel Beatriz Funes Quintanilla", "EV", "SV", "female"),
    ("Héctor David Molina Argueta", "MK", "SV", "male"),
]

# Jefes de departamento (nombre del empleado)
DEPARTMENT_MANAGERS = {
    "DIR": "Carlos Eduardo Méndez Ortiz",
    "COM": "Jorge Alejandro Morales Cifuentes",
    "OPS": "Ana Lucía Herrera Pineda",
    "VEN": "Rodrigo Andrés Estrada Paz",
    "MKT": "Daniel Esteban García Archila",
}

# ------------------------------------------------------------------ Proveedores
# (nombre, NIT/RFC, país, ciudad, calle, teléfono, correo, [categorías que surte])
VENDORS = [
    ("Distribuidora Limpiamax, S.A.", "4521789-3", "gt", "Guatemala", "Calzada Roosevelt 22-43, Zona 11", "+502 2440 1020", "ventas@limpiamax.example.com", ["LIM"]),
    ("Químicos Industriales del Valle, S.A.", "3812456-0", "gt", "Villa Nueva", "Km 17.5 Carretera al Pacífico", "+502 6630 8800", "pedidos@quimvalle.example.com", ["LIM", "SEG"]),
    ("Empaques Centroamericanos, S.A.", "2290341-7", "gt", "Mixco", "Calzada San Juan 14-06, Zona 7", "+502 2433 5500", "info@empacasa.example.com", ["EMP"]),
    ("Plásticos y Bolsas La Ceiba, S.A. de C.V.", "0614-250390-101-2", "sv", "Soyapango", "Bulevar del Ejército Km 5", "+503 2277 3100", "ventas@laceiba.example.com", ["EMP"]),
    ("Librería y Papelería El Estudiante, S.A.", "1029384-5", "gt", "Guatemala", "9a. Calle 7-55, Zona 1", "+502 2232 6060", "corporativo@elestudiante.example.com", ["PAP"]),
    ("Suministros de Oficina Maya, S.A.", "5567123-9", "gt", "Quetzaltenango", "4a. Calle 12-30, Zona 3", "+502 7761 4400", "ventas@ofimaya.example.com", ["PAP"]),
    ("Tecnología POS Guatemala, S.A.", "7781290-1", "gt", "Guatemala", "Diagonal 6 10-01, Zona 10, Torre II", "+502 2385 9090", "soporte@posgt.example.com", ["POS"]),
    ("Sistemas de Cobro Azteca, S.A. de C.V.", "SCA090512KJ3", "mx", "Tuxtla Gutiérrez", "Blvd. Belisario Domínguez 1850", "+52 961 615 2000", "ventas@cobroazteca.example.com", ["POS"]),
    ("Seguridad Industrial Quetzal, S.A.", "6123457-4", "gt", "Guatemala", "Av. Petapa 45-20, Zona 12", "+502 2477 1212", "ventas@siquetzal.example.com", ["SEG"]),
    ("Ferretería El Volcán, S.A.", "8034561-2", "gt", "Escuintla", "1a. Avenida 3-21, Zona 1", "+502 7888 3030", "pedidos@elvolcan.example.com", ["MAN", "SEG"]),
    ("Ferretera Cuscatlán, S.A. de C.V.", "0614-110285-102-6", "sv", "Santa Tecla", "Calle Chiltiupán 18", "+503 2228 9000", "ventas@cuscatlan.example.com", ["MAN"]),
    ("Refrigeración Comercial del Pacífico, S.A.", "9045672-8", "gt", "Mazatenango", "Calzada Colombia 8-44", "+502 7872 5050", "ventas@refripacifico.example.com", ["REF"]),
    ("Exhibidores y Anaqueles Monterrey, S.A. de C.V.", "EAM120830QW1", "mx", "Monterrey", "Av. Constitución 3100 Pte.", "+52 81 8340 7700", "ventas@anamty.example.com", ["REF"]),
    ("Textiles y Uniformes Atitlán, S.A.", "3398210-6", "gt", "Sololá", "Calle Principal 5-10, Panajachel", "+502 7762 1919", "pedidos@uniatitlan.example.com", ["UNI"]),
    ("Confecciones San Miguel, S.A. de C.V.", "1217-040595-101-3", "sv", "San Miguel", "Av. Roosevelt Sur 307", "+503 2661 4545", "ventas@confesanmiguel.example.com", ["UNI"]),
    ("Multisuministros del Norte, S.A. de C.V.", "MSN150223AB7", "mx", "Tapachula", "Carretera Costera Km 3.5", "+52 962 642 3300", "ventas@multinorte.example.com", ["LIM", "EMP", "PAP"]),
]

# Proveedores de OUTSOURCING (servicios) -> útiles para los contratos del Integrante 1
OUTSOURCING_VENDORS = [
    ("Seguridad Privada Centinela, S.A.", "4410982-1", "gt", "Guatemala", "20 Calle 5-35, Zona 10", "+502 2367 4000", "contratos@centinela.example.com", "SRV-SEG", "Servicio mensual de seguridad privada (por sucursal)", 18500.0),
    ("Limpieza Profesional Brillo Total, S.A.", "5523019-7", "gt", "Guatemala", "Av. Las Américas 9-50, Zona 13", "+502 2331 7171", "servicios@brillototal.example.com", "SRV-LIM", "Servicio mensual de limpieza profesional (por sucursal)", 9800.0),
    ("Transportes Logísticos Quetzal Express, S.A.", "6634120-3", "gt", "Amatitlán", "Km 28 Carretera al Pacífico", "+502 6633 2020", "operaciones@qexpress.example.com", "SRV-TRA", "Servicio de transporte y distribución entre sucursales (viaje)", 4200.0),
    ("Servicios Informáticos NubeTech, S.A.", "7745231-0", "gt", "Guatemala", "Diagonal 6 13-08, Zona 10", "+502 2205 8800", "soporte@nubetech.example.com", "SRV-TI", "Soporte técnico, hosting y mantenimiento del ERP (mensual)", 6500.0),
]

# ------------------------------------------------------------------ Materiales (64)
MATERIAL_ROOT = "Materiales de Sucursal"
MATERIAL_CATEGORIES = {
    "LIM": "Limpieza e Higiene",
    "EMP": "Empaque y Bolsas",
    "PAP": "Papelería y Oficina",
    "POS": "Equipo de Punto de Venta",
    "SEG": "Seguridad Industrial",
    "MAN": "Mantenimiento y Ferretería",
    "REF": "Refrigeración y Exhibición",
    "UNI": "Uniformes e Identificación",
}

# (categoría, nombre, costo GTQ)  -> código interno MAT-<CAT>-<nn>
MATERIALS = [
    ("LIM", "Detergente líquido multiusos (galón)", 65.00),
    ("LIM", "Cloro concentrado (galón)", 38.00),
    ("LIM", "Desinfectante aroma lavanda (galón)", 55.00),
    ("LIM", "Jabón líquido para manos (galón)", 72.00),
    ("LIM", "Papel higiénico jumbo (fardo 12 rollos)", 210.00),
    ("LIM", "Toallas de papel interfoliadas (caja)", 165.00),
    ("LIM", "Bolsas para basura 30 galones (paquete 50)", 85.00),
    ("LIM", "Trapeador de microfibra", 48.00),
    ("EMP", "Bolsa plástica tipo camiseta mediana (millar)", 180.00),
    ("EMP", "Bolsa biodegradable grande (millar)", 260.00),
    ("EMP", "Bolsa de papel kraft #20 (paquete 500)", 220.00),
    ("EMP", "Caja de cartón corrugado 40x30x30 cm", 9.50),
    ("EMP", "Cinta adhesiva transparente 48 mm (rollo)", 12.00),
    ("EMP", "Film stretch para paletizar 18\" (rollo)", 95.00),
    ("EMP", "Bandeja de duroport para carnes (paquete 500)", 175.00),
    ("EMP", "Etiqueta térmica 4x6 para envíos (rollo 250)", 68.00),
    ("PAP", "Papel bond tamaño carta (resma 500 hojas)", 42.00),
    ("PAP", "Rollo de papel térmico 80 mm para POS", 6.50),
    ("PAP", "Bolígrafo azul (caja 12)", 24.00),
    ("PAP", "Folder manila tamaño carta (caja 100)", 85.00),
    ("PAP", "Archivador de palanca tamaño oficio", 28.00),
    ("PAP", "Tóner para impresora láser", 610.00),
    ("PAP", "Marcador permanente negro (caja 12)", 60.00),
    ("PAP", "Grapas estándar (caja 5000)", 9.00),
    ("POS", "Lector de código de barras USB", 425.00),
    ("POS", "Impresora térmica de tickets 80 mm", 1350.00),
    ("POS", "Cajón monedero metálico", 690.00),
    ("POS", "Terminal punto de venta táctil 15\"", 5800.00),
    ("POS", "Etiquetadora de precios manual", 145.00),
    ("POS", "Rollos de etiquetas para precios (paquete 10)", 55.00),
    ("POS", "Báscula electrónica con impresora de etiquetas", 4200.00),
    ("POS", "Combo teclado y mouse USB", 175.00),
    ("SEG", "Guantes de nitrilo (caja 100)", 95.00),
    ("SEG", "Mascarilla desechable (caja 50)", 45.00),
    ("SEG", "Chaleco reflectivo", 38.00),
    ("SEG", "Botas de seguridad con punta de acero", 385.00),
    ("SEG", "Extintor PQS 10 lb", 450.00),
    ("SEG", "Botiquín de primeros auxilios completo", 320.00),
    ("SEG", "Rótulo de salida de emergencia", 35.00),
    ("SEG", "Faja lumbar para carga", 120.00),
    ("MAN", "Foco LED 18 W", 32.00),
    ("MAN", "Tubo LED T8 120 cm", 58.00),
    ("MAN", "Pintura látex blanca (cubeta 5 galones)", 640.00),
    ("MAN", "Extensión eléctrica 10 m", 95.00),
    ("MAN", "Juego de destornilladores", 135.00),
    ("MAN", "Cinta de aislar (rollo)", 8.00),
    ("MAN", "Candado de seguridad 60 mm", 110.00),
    ("MAN", "Escalera de aluminio 6 peldaños", 980.00),
    ("REF", "Termómetro digital para refrigerador", 85.00),
    ("REF", "Gas refrigerante R-134a (cilindro 13.6 kg)", 1250.00),
    ("REF", "Cortina de PVC para cuarto frío (rollo)", 1450.00),
    ("REF", "Canasta plástica de supermercado", 48.00),
    ("REF", "Carrito de supermercado metálico", 1650.00),
    ("REF", "Anaquel metálico tipo góndola 5 niveles", 2400.00),
    ("REF", "Portaprecios de acrílico para góndola (paquete 20)", 160.00),
    ("REF", "Hielera industrial 120 L", 1150.00),
    ("UNI", "Camisa polo con logo QuetzalMart", 95.00),
    ("UNI", "Gabacha con logo QuetzalMart", 65.00),
    ("UNI", "Gorra con logo QuetzalMart", 40.00),
    ("UNI", "Pantalón de trabajo tipo cargo", 145.00),
    ("UNI", "Chumpa térmica para cuarto frío", 380.00),
    ("UNI", "Gafete de PVC con porta gafete", 18.00),
    ("UNI", "Delantal impermeable para carnicería", 75.00),
    ("UNI", "Redecilla para cabello (paquete 100)", 35.00),
]

# ------------------------------------------------------------------ Metas de la rúbrica
TARGET_PURCHASES = 105        # >= 100 compras confirmadas, recibidas y facturadas
TARGET_SERVICE_PURCHASES = 12 # de esas, órdenes de servicios de outsourcing
TARGET_RFQS = 12              # solicitudes de cotización a proveedores (apoyo a 1.02)
PAY_RATIO = 0.8               # % de facturas de proveedor pagadas
DATE_FROM = "2026-04-01"
DATE_TO = "2026-10-05"
RANDOM_SEED = 2026
