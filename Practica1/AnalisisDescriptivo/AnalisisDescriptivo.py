import os
import pandas as pd
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
    
    VentasEfectivo = DfCompras[DfCompras['id_metodo_pago'] == 0]['monto_compra'].sum()
    
    UsoBoletines = DfCompras['boletin'].sum()
    UsoVales = DfCompras['vale'].sum()
    
    DfCompleto['grupo_edad'] = pd.cut(DfCompleto['edad'], bins=[0, 18, 35, 50, 100], labels=['Menores de 18', '19-35', '36-50', 'Mayores de 50'])
    ComprasPorEdad = DfCompleto.groupby('grupo_edad', observed=False)['monto_compra'].sum().reset_index()
    ComprasPorGenero = DfCompleto.groupby('id_genero')['monto_compra'].sum().reset_index()
    ComprasConPromociones = DfCompleto.groupby(['boletin', 'vale'])['monto_compra'].sum().reset_index()
    
    with open("Resultados.md", "w") as Archivo:
        Archivo.write("# Resultados del Analisis Descriptivo\n\n")
        
        Archivo.write("## Estadisticas Basicas\n")
        Archivo.write(DfEstadisticas.to_markdown(index=False))
        
        Archivo.write("\n\n## Analisis de Tendencias\n")
        Archivo.write(f"- Mes de Mayores Ventas: Mes {MesMayorVentas['mes_compra']} con monto de {MesMayorVentas['monto_compra']}\n")
        Archivo.write(f"- Mes de Menores Ventas: Mes {MesMenorVentas['mes_compra']} con monto de {MesMenorVentas['monto_compra']}\n")
        Archivo.write(f"- Ventas totales en efectivo: {VentasEfectivo}\n")
        Archivo.write(f"- Uso total de boletines: {UsoBoletines}\n")
        Archivo.write(f"- Uso total de vales: {UsoVales}\n")
        
        Archivo.write("\n### Navegadores mas usados\n")
        Archivo.write(NavegadoresUsados.to_markdown(index=False))
        
        Archivo.write("\n\n## Segmentacion de Clientes\n")
        
        Archivo.write("### Por Edad\n")
        Archivo.write(ComprasPorEdad.to_markdown(index=False))
        
        Archivo.write("\n### Por Genero\n")
        Archivo.write(ComprasPorGenero.to_markdown(index=False))
        
        Archivo.write("\n### Por Uso de Promociones (Boletin, Vale)\n")
        Archivo.write(ComprasConPromociones.to_markdown(index=False))

if __name__ == "__main__":
    EjecutarAnalisisDescriptivo()
