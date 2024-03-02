from orm import Receita, Ingrediente, Session, select


def listar_receitas(session: Session):
    stmt = select(Receita).order_by(Receita.id.desc())
    receitas = session.execute(stmt).scalars().all()
    return [receita.to_dto() for receita in receitas]


def buscar_receita_por_id(session: Session, id_receita: int):
    receita = session.execute(select(Receita).filter(Receita.id == id_receita)).scalar()
    return receita.to_dto() if receita else None

