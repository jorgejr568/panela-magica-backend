from sqlalchemy import ForeignKey, String, Integer, JSON, Text, DateTime

from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from typing import List
from datetime import datetime, timezone

from orm.base import BaseOrm
import models


class Receita(BaseOrm):
    __tablename__ = 'receitas'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    tipo: Mapped[str] = mapped_column(String(20))
    ingredientes: Mapped[List['Ingrediente']] = relationship(cascade='all, delete-orphan')
    criador: Mapped[str] = mapped_column(String(50))
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
            # it's a datetime object, so we need to convert it to a timestamp and use the UTC timezone
            data_de_criacao=int(self.data_de_criacao.astimezone(timezone.utc).timestamp()),
            criador=self.criador,
            imagem=self.imagem
        )


class Ingrediente(BaseOrm):
    __tablename__ = 'ingredientes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    quantidade: Mapped[str] = mapped_column(String(20))
    receita_id: Mapped[int] = mapped_column(Integer, ForeignKey('receitas.id'))



    def __repr__(self):
        return f'<Ingrediente {self.nome} - {self.id}>'

    def to_dto(self) -> 'models.Ingrediente':
        return models.Ingrediente(
            id=self.id,
            nome=self.nome,
            quantidade=self.quantidade
        )

