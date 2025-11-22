from src.domain.vehiculo import Vehiculo

class VehiculoFactory:
    """
    Implementación del Patrón Factory Method.
    Centraliza la lógica de creación de objetos Vehiculo.
    """

    @staticmethod
    def get_vehiculo(tipo: str, **kwargs) -> Vehiculo:
        """
        Método de fábrica estático.
        Recibe el tipo de vehículo y sus datos (kwargs), y retorna la instancia correcta.
        """
        tipo_normalizado = (tipo or "").strip().lower()
        
        # Aquí defines los tipos permitidos en tu sistema
        tipos_validos = ["auto", "camioneta", "moto"]
        
        if tipo_normalizado not in tipos_validos:
            # La fábrica rechaza tipos desconocidos, protegiendo la integridad del sistema
            raise ValueError(f"El tipo de vehículo '{tipo}' no es válido.")

        # Retornamos la entidad Vehiculo configurada
        return Vehiculo(tipo=tipo_normalizado, **kwargs)