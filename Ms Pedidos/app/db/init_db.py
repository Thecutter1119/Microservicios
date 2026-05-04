from app.db.session import engine, Base
from app.models.pedidos import Pedido, ItemPedido, HistorialEstado

def create_all_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creando tablas en la base de datos...")
    create_all_tables()
    print("¡Tablas creadas exitosamente!")
