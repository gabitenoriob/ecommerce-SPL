from sqlalchemy.orm import Session
import models, schema

def get_pedido(db: Session, pedido_id: int):
    return db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()

def get_pedidos_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Pedido).filter(models.Pedido.user_id == user_id).offset(skip).limit(limit).all()

def create_pedido(db: Session, pedido: schema.PedidoCreate, valor_total: float):
    db_pedido = models.Pedido(
        user_id=pedido.user_id,
        valor_total=valor_total,
        status=schema.StatusPedido.pendente # Status inicial
    )
    db.add(db_pedido)
    db.flush() # Para obter o ID do pedido antes de criar os itens

    for item_data in pedido.items:
        db_item = models.ItemPedido(
            **item_data.model_dump(),
            pedido_id=db_pedido.id
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_pedido)
    return db_pedido

def update_pedido_status(db: Session, pedido_id: int, status: schema.StatusPedido):
    db_pedido = get_pedido(db, pedido_id)
    if db_pedido:
        db_pedido.status = status
        db.commit()
        db.refresh(db_pedido)
    return db_pedido
