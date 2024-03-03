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
    criador: str
    imagem: str


class CriarReceita(BaseModel):
    nome: str
    tipo: str
    ingredientes: List[Ingrediente]
    modo_de_preparo: str
    criador: str
    imagem: str

    @field_validator('imagem')
    @classmethod
    def imagem_deve_ser_valida(cls, v):
        if urlparse(v).scheme not in ('http', 'https'):
            raise ValueError('Imagem deve ser uma URL válida')

        return v
