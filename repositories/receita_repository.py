import os
from typing import Optional
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select, delete

from clients import s3_client
from models import CriarReceita
from orm import Receita, Ingrediente, Session
from settings import settings


def listar_receitas(session: Session):
    stmt = select(Receita).order_by(Receita.id.desc())
    receitas = session.execute(stmt).scalars().all()
    return [receita.to_dto() for receita in receitas]


def buscar_receita_por_id(session: Session, id_receita: int):
    receita = session.execute(select(Receita).filter(Receita.id == id_receita)).scalar()
    return receita.to_dto() if receita else None


def criar_receita(session: Session, receita: CriarReceita) -> Receita:
    try:
        nova_receita = Receita(
            nome=receita.nome,
            tipo=receita.tipo,
            criador=receita.criador,
            imagem=receita.imagem,
            modo_de_preparo=receita.modo_de_preparo,
            ingredientes=[Ingrediente(nome=ingrediente.nome, quantidade=ingrediente.quantidade) for ingrediente in receita.ingredientes]
        )

        session.add(nova_receita)
        session.commit()
        return nova_receita.to_dto()
    except Exception as e:
        session.rollback()
        raise e


def salvar_imagem_receita(imagem: UploadFile) -> str:
    name = "{}.{}".format(uuid4(), imagem.filename.split('.')[-1])
    return s3_client.upload_file(imagem.file, 'imagens-receitas/' + name)


def atualizar_receita(session: Session, id_receita: int, receita: CriarReceita) -> Receita:
    try:
        receita_banco = session.execute(select(Receita).filter(Receita.id == id_receita)).scalar()
        receita_banco.nome = receita.nome
        receita_banco.tipo = receita.tipo
        receita_banco.criador = receita.criador
        receita_banco.imagem = receita.imagem
        receita_banco.modo_de_preparo = receita.modo_de_preparo
        receita_banco.ingredientes = [Ingrediente(nome=ingrediente.nome, quantidade=ingrediente.quantidade) for ingrediente in receita.ingredientes]
        session.commit()
        session.refresh(receita_banco)
        return receita_banco.to_dto()
    except Exception as e:
        session.rollback()
        raise e


def deletar_receita(session: Session, id_receita: int):
    try:
        session.execute(delete(Receita).filter(Receita.id == id_receita))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def buscar_imagem_receita(imagem: str) -> Optional[str]:
    filename = settings().storage_path + '/imagens-receitas/' + imagem
    if not os.path.exists(filename) or not os.path.isfile(filename) or not os.access(filename, os.R_OK):
        return None
    return filename