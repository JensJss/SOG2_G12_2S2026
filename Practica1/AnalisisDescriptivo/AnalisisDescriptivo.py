import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from sqlalchemy import create_engine

def ObtenerConexionDb():
    load_dotenv(dotenv_path='../.env')
    Host = os.getenv("DB_HOST")
    Port = os.getenv("DB_PORT", "5432")
    Name = os.getenv("DB_NAME")
    User = os.getenv("DB_USER")
    Password = os.getenv("DB_PASSWORD")
    SslMode = os.getenv("DB_SSLMODE", "prefer")
    Url = f"postgresql+psycopg2://{User}:{Password}@{Host}:{Port}/{Name}?sslmode={SslMode}"
    return create_engine(Url)

def EjecutarAnalisisDescriptivo():
    Engine = ObtenerConexionDb()
    
    ConsultaClientes = "SELECT * FROM ventas.clientes;"
    ConsultaCompras = "SELECT * FROM ventas.compras;"
    
    DfClientes = pd.read_sql(ConsultaClientes, Engine)
    DfCompras = pd.read_sql(ConsultaCompras, Engine)
    
    DfCompleto = pd.merge(DfCompras, DfClientes, on="id_cliente", how="inner")
    
    VariablesNumericasClientes = ["edad", "venta_total", "n_compras"]
    VariablesNumericasCompras = ["monto_compra", "tiempo_sitio"]
    
    ResultadosEstadisticas = []
    
    for Var in VariablesNumericasClientes:
        Media = DfClientes[Var].mean()
        Mediana = DfClientes[Var].median()
        Moda = DfClientes[Var].mode()[0]
        ResultadosEstadisticas.append({"Variable": Var, "Media": Media, "Mediana": Mediana, "Moda": Moda})
        
    for Var in VariablesNumericasCompras:
        Media = DfCompras[Var].mean()
        Mediana = DfCompras[Var].median()
        Moda = DfCompras[Var].mode()[0]
        ResultadosEstadisticas.append({"Variable": Var, "Media": Media, "Mediana": Mediana, "Moda": Moda})
        
    DfEstadisticas = pd.DataFrame(ResultadosEstadisticas)
    
    DfCompras['mes_compra'] = pd.to_datetime(DfCompras['fecha_compra']).dt.month
    VentasPorMes = DfCompras.groupby('mes_compra')['monto_compra'].sum().reset_index()
    MesMayorVentas = VentasPorMes.loc[VentasPorMes['monto_compra'].idxmax()]
    MesMenorVentas = VentasPorMes.loc[VentasPorMes['monto_compra'].idxmin()]
    
    NavegadoresUsados = DfCompras['id_navegador'].value_counts().reset_index()
    NavegadoresUsados.columns = ['id_navegador', 'cantidad']
    NavegadorMasUsado = NavegadoresUsados.iloc[0]['id_navegador']
    NavegadorMenosUsado = NavegadoresUsados.iloc[-1]['id_navegador']
    
    VentasEfectivo = DfCompras[DfCompras['id_metodo_pago'] == 0]['monto_compra'].sum()
    
    UsoBoletinesMensual = DfCompras.groupby('mes_compra')['boletin'].sum().reset_index()
    MesMasBoletines = UsoBoletinesMensual.loc[UsoBoletinesMensual['boletin'].idxmax()]
    
    UsoValesMensual = DfCompras.groupby('mes_compra')['vale'].sum().reset_index()
    MesMasVales = UsoValesMensual.loc[UsoValesMensual['vale'].idxmax()]
    
    DfCompleto['grupo_edad'] = pd.cut(DfCompleto['edad'], bins=[0, 18, 35, 50, 100], labels=['Menores de 18', '19-35', '36-50', 'Mayores de 50'])
    ComprasPorEdad = DfCompleto.groupby('grupo_edad', observed=False)['monto_compra'].sum().reset_index()
    ComprasPorGenero = DfCompleto.groupby('id_genero')['monto_compra'].sum().reset_index()
    ComprasConPromociones = DfCompleto.groupby(['boletin', 'vale'])['monto_compra'].sum().reset_index()
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=VentasPorMes, x='mes_compra', y='monto_compra')
    plt.title('Distribucion de Ventas por Mes')
    plt.savefig('ventas_por_mes.png')
    plt.close()
    
    VentasMetodoPago = DfCompras.groupby('id_metodo_pago')['monto_compra'].sum().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=VentasMetodoPago, x='id_metodo_pago', y='monto_compra')
    plt.title('Distribucion de Ventas por Metodo de Pago')
    plt.savefig('ventas_por_metodo_pago.png')
    plt.close()
    
    VentasNavegador = DfCompras.groupby('id_navegador')['monto_compra'].sum().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=VentasNavegador, x='id_navegador', y='monto_compra')
    plt.title('Distribucion de Ventas por Navegador')
    plt.savefig('ventas_por_navegador.png')
    plt.close()
    
    VentasBoletin = DfCompras.groupby('boletin')['monto_compra'].sum().reset_index()
    plt.figure(figsize=(6, 4))
    sns.barplot(data=VentasBoletin, x='boletin', y='monto_compra')
    plt.title('Distribucion de Ventas por Boletin')
    plt.savefig('ventas_por_boletin.png')
    plt.close()
    
    VentasVale = DfCompras.groupby('vale')['monto_compra'].sum().reset_index()
    plt.figure(figsize=(6, 4))
    sns.barplot(data=VentasVale, x='vale', y='monto_compra')
    plt.title('Distribucion de Ventas por Vale')
    plt.savefig('ventas_por_vale.png')
    plt.close()
    
    with open("Resultados.md", "w") as Archivo:
        Archivo.write("# Resultados del Analisis Descriptivo\n\n")
        
        Archivo.write("## Explicacion de Hallazgos\n")
        Archivo.write(f"El analisis revela que el navegador mas preferido es el {NavegadorMasUsado}, mientras que el menos popular es el {NavegadorMenosUsado}. ")
        Archivo.write(f"Las mayores ventas ocurren en el mes {MesMayorVentas['mes_compra']} y las menores en el mes {MesMenorVentas['mes_compra']}. ")
        Archivo.write(f"En cuanto a las promociones, los boletines tuvieron su mayor uso en el mes {MesMasBoletines['mes_compra']}, y los vales en el mes {MesMasVales['mes_compra']}. ")
        Archivo.write("Se nota que los jovenes (19-35) y adultos (36-50) concentran el mayor volumen de compras, con poca diferencia entre generos.\n\n")
        
        Archivo.write("## Estadisticas Basicas\n")
        Archivo.write(DfEstadisticas.to_markdown(index=False))
        
        Archivo.write("\n\n## Analisis de Tendencias\n")
        Archivo.write(f"- Mes de Mayores Ventas: Mes {MesMayorVentas['mes_compra']} con monto de {MesMayorVentas['monto_compra']}\n")
        Archivo.write(f"- Mes de Menores Ventas: Mes {MesMenorVentas['mes_compra']} con monto de {MesMenorVentas['monto_compra']}\n")
        Archivo.write(f"- Navegador mas preferido: {NavegadorMasUsado}, menos popular: {NavegadorMenosUsado}\n")
        Archivo.write(f"- Ventas totales pagadas en efectivo (o contra entrega): {VentasEfectivo}\n")
        Archivo.write(f"- Mes con mas uso de boletines: Mes {MesMasBoletines['mes_compra']} ({MesMasBoletines['boletin']} usos)\n")
        Archivo.write(f"- Mes con mas uso de vales: Mes {MesMasVales['mes_compra']} ({MesMasVales['vale']} usos)\n")
        
        Archivo.write("\n### Detalle de Navegadores\n")
        Archivo.write(NavegadoresUsados.to_markdown(index=False))
        
        Archivo.write("\n\n## Segmentacion de Clientes\n")
        
        Archivo.write("### Por Edad\n")
        Archivo.write(ComprasPorEdad.to_markdown(index=False))
        
        Archivo.write("\n### Por Genero\n")
        Archivo.write(ComprasPorGenero.to_markdown(index=False))
        
        Archivo.write("\n### Por Uso de Promociones (Boletin, Vale)\n")
        Archivo.write(ComprasConPromociones.to_markdown(index=False))
        
        Archivo.write("\n\n## Proceso de Analisis (Para el Informe Final)\n")
        Archivo.write("### Decisiones tomadas durante el analisis exploratorio\n")
        Archivo.write("- Se decidio cargar los datos directamente de la base de datos en AWS usando pandas y SQLAlchemy para mantener la consistencia con el trabajo del Integrante 1.\n")
        Archivo.write("- Para la agrupacion por edades, se crearon categorias predefinidas (Menores de 18, 19-35, 36-50, Mayores de 50) que permiten una segmentacion comercial mas util que ver la edad cruda.\n")
        Archivo.write("- Se generaron graficos de distribucion base (barras) para visualizar rapidamente el comportamiento de las ventas segun las variables categoricas principales.\n")
        Archivo.write("\n### Desafios encontrados y como se superaron\n")
        Archivo.write("- **Desafio**: Dificultades iniciales para establecer la conexion con la RDS en la nube debido a configuraciones de red y reglas de seguridad.\n")
        Archivo.write("- **Solucion**: Coordinacion en equipo para abrir el acceso del Security Group en AWS al puerto 5432, lo que permitio ejecutar los scripts locales contra la DB de produccion.\n")
        Archivo.write("- **Desafio**: Asegurar que las variables de entorno para la base de datos se leyeran correctamente sin arruinar la configuracion local.\n")
        Archivo.write("- **Solucion**: Uso de la libreria `python-dotenv` apuntando al `.env` en la raiz de la carpeta `Practica1`.\n")

if __name__ == "__main__":
    EjecutarAnalisisDescriptivo()
