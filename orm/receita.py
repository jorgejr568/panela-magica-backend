from sqlalchemy import ForeignKey, String, Integer, JSON, Text, DateTime

from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from typing import List
from datetime import datetime, timezone

from orm.base import BaseOrm
from orm.user import User
import models


class Receita(BaseOrm):
    __tablename__ = 'receitas'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    tipo: Mapped[str] = mapped_column(String(30))
    ingredientes: Mapped[List['Ingrediente']] = relationship(cascade='all, delete-orphan')
    criador: Mapped[User] = relationship(User)
    criador_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    imagem: Mapped[str] = mapped_column(Text)
    modo_de_preparo: Mapped[str] = mapped_column(Text)
    data_de_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Receita {self.nome} - {self.id}>'

    def to_dto(self) -> 'models.Receita':
        return models.Receita(
            id=self.id,
            nome=self.nome,
            tipo=self.tipo,
            ingredientes=[ingrediente.to_dto() for ingrediente in self.ingredientes],
            modo_de_preparo=self.modo_de_preparo,
            data_de_criacao=int(self.data_de_criacao.astimezone(timezone.utc).timestamp()),
            criador=models.CriadorReceita.from_orm(self.criador),
            imagem=self.imagem
        )


class Ingrediente(BaseOrm):
    __tablename__ = 'ingredientes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    quantidade: Mapped[str] = mapped_column(String(50))
    receita_id: Mapped[int] = mapped_column(Integer, ForeignKey('receitas.id', ondelete='CASCADE', onupdate='CASCADE'))

    def __repr__(self):
        return f'<Ingrediente {self.nome} - {self.id}>'

    def to_dto(self) -> 'models.Ingrediente':
        return models.Ingrediente(
            id=self.id,
            nome=self.nome,
            quantidade=self.quantidade
        )


