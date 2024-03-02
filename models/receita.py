from enum import Enum

from pydantic import BaseModel
from typing import List



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
