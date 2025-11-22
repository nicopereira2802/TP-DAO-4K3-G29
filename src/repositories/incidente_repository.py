from src.repositories.db_connection import get_connection
from src.domain.incidente import Incidente

class IncidenteRepository:

    @staticmethod
    def crear(incidente: Incidente):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO incidentes (id_alquiler, tipo, descripcion, monto, estado) VALUES (?, ?, ?, ?, ?)",
            (incidente.id_alquiler, incidente.tipo, incidente.descripcion, incidente.monto, incidente.estado)
        )
        conn.commit()
        incidente.id_incidente = cursor.lastrowid
        return incidente

    @staticmethod
    def listar():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidentes")
        filas = cursor.fetchall()
        incidentes = []
        for f in filas:
            incidentes.append(Incidente(
                id_incidente=f[0], id_alquiler=f[1], tipo=f[2],
                descripcion=f[3], monto=f[4], estado=f[5]
            ))
        return incidentes

    @staticmethod
    def obtener_por_id(id_incidente):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidentes WHERE id_incidente = ?", (id_incidente,))
        f = cursor.fetchone()
        if not f: return None
        return Incidente(
            id_incidente=f[0], id_alquiler=f[1], tipo=f[2],
            descripcion=f[3], monto=f[4], estado=f[5]
        )

    @staticmethod
    def actualizar(incidente: Incidente):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE incidentes SET estado = ? WHERE id_incidente = ?",
            (incidente.estado, incidente.id_incidente)
        )
        conn.commit()
    
    @staticmethod
    def listar_por_alquiler(id_alquiler):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidentes WHERE id_alquiler = ?", (id_alquiler,))
        filas = cursor.fetchall()
        incidentes = []
        for f in filas:
            incidentes.append(Incidente(
                id_incidente=f[0], id_alquiler=f[1], tipo=f[2],
                descripcion=f[3], monto=f[4], estado=f[5]
            ))
        return incidentes