from typing import List
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator


class Ingrediente(BaseModel):
    nome: str
    quantidade: str


class Receita(BaseModel):
    id: int
    nome: str
    tipo: str
    ingredientes: List[Ingrediente]
    modo_de_preparo: str
    data_de_criacao: int
    criador: 'CriadorReceita'
    imagem: str


class CriarReceita(BaseModel):
    nome: str
    tipo: str
    ingredientes: List[Ingrediente]
    modo_de_preparo: str
    _criador_id: int
    imagem: str

    @field_validator('imagem')
    @classmethod
    def imagem_deve_ser_valida(cls, v):
        if urlparse(v).scheme not in ('http', 'https'):
            raise ValueError('Imagem deve ser uma URL válida')

        return v

    def assign_criador_id(self, criador_id: int) -> 'CriarReceita':
        self._criador_id = criador_id
        return self

    def get_criador_id(self) -> int:
        return self._criador_id


class CriadorReceita(BaseModel):
    id: int
    nome: str

    @classmethod
    def from_orm(cls, user):
        return CriadorReceita(
            id=user.id,
            nome=user.name
        )
