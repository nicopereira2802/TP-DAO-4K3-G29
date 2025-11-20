class Mantenimiento:
    def __init__(self, id_mantenimiento, id_vehiculo, fecha_inicio, fecha_fin, descripcion):
        self.id_mantenimiento = id_mantenimiento
        self.id_vehiculo = id_vehiculo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.descripcion = descripcion

    def __str__(self):
        return (
            f"Mantenimiento(id={self.id_mantenimiento}, vehiculo={self.id_vehiculo}, "
            f"desde={self.fecha_inicio}, hasta={self.fecha_fin})"
        )
