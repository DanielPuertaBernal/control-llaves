"""Casos de uso para docentes"""
from interfaces.docente_repository import DocenteRepository
from infrastructure.importers.docente_excel_importer import cargar_docentes_desde_archivo
from application.processing.docente_cleaner import limpiar_datos


class DocenteService:
    def __init__(self, repository: DocenteRepository):
        self.repository = repository

    def cargar_informacion_docentes(self, ruta_archivo):
        try:
            df = cargar_docentes_desde_archivo(ruta_archivo)

            columnas_requeridas = [
                'Numero de documento', 'Nombre', 'Facultad', 'Correo', 'Id Carnet'
            ]

            df.columns = df.columns.str.strip()

            columnas_faltantes = []
            for col in columnas_requeridas:
                if col not in df.columns:
                    col_normalizada = col.lower().replace(' ', '')
                    encontrada = False
                    for df_col in df.columns:
                        if df_col.lower().replace(' ', '') == col_normalizada:
                            df.rename(columns={df_col: col}, inplace=True)
                            encontrada = True
                            break
                    if not encontrada:
                        columnas_faltantes.append(col)

            if columnas_faltantes:
                return False, None, f"❌ Faltan columnas requeridas: {', '.join(columnas_faltantes)}"

            df = limpiar_datos(df)

            exito, mensaje = self.repository.guardar_docentes(df)
            if exito:
                return True, df, f"✅ Docentes cargados exitosamente: {len(df)} registros"
            return False, None, mensaje

        except Exception as e:
            return False, None, f"❌ Error al cargar archivo: {str(e)}"

    def obtener_docentes(self):
        return self.repository.obtener_docentes()

    def buscar_docente_por_documento(self, numero_documento):
        return self.repository.buscar_docente_por_documento(numero_documento)

    def buscar_docente_por_carnet(self, id_carnet):
        return self.repository.buscar_docente_por_carnet(id_carnet)

    def verificar_docentes_cargados(self):
        df = self.repository.obtener_docentes()
        return not df.empty, len(df)
