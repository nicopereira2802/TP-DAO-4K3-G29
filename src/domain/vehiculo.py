# src/domain/vehiculo.py

class Vehiculo:
    def __init__(
        self,
        id_vehiculo,
        patente,
        marca,
        modelo,
        anio,
        tipo,
        precio_por_dia,
        activo=True,
        estado="DISPONIBLE",  # NUEVO CAMPO
    ):
        self.id_vehiculo = id_vehiculo
        self.patente = patente
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.tipo = tipo
        self.precio_por_dia = precio_por_dia
        self.activo = activo
        self.estado = estado  # disponible / alquilado / mantenimiento, etc.

    def __str__(self):
        return (
            f"Vehiculo(id={self.id_vehiculo}, patente={self.patente}, "
            f"marca={self.marca}, modelo={self.modelo}, "
            f"activo={self.activo}, estado={self.estado})"
        )
