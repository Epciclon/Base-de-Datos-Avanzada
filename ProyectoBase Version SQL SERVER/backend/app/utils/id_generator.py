"""
Utilidad para generar IDs incrementales manualmente
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Type

def get_next_id(db: Session, model: Type, id_field: str) -> int:
    """
    Obtiene el siguiente ID disponible para una tabla
    
    Args:
        db: Sesión de base de datos
        model: Modelo SQLAlchemy
        id_field: Nombre del campo ID en el modelo
    
    Returns:
        int: Siguiente ID disponible
    """
    try:
        # Obtener el ID máximo actual
        max_id = db.query(func.max(getattr(model, id_field))).scalar()
        
        # Si no hay registros, empezar desde 1
        if max_id is None:
            return 1
        
        # Retornar el siguiente ID
        return max_id + 1
        
    except Exception:
        # En caso de error, empezar desde 1
        return 1
