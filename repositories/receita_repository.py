import os
from typing import Optional, BinaryIO, IO
from uuid import uuid4

import filetype
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


def imagem_receita_e_valida(imagem: IO) -> bool:
    max_size = 2 * 1024 * 1024
    allowed_formats = ['image/png', 'image/jpeg', 'image/jpg']

    file_info = filetype.guess(imagem.read(261))
    imagem.seek(0)

    if file_info is None:
        return False

    if file_info.mime not in allowed_formats:
        return False

    real_size = 0
    for chunk in iter(lambda: imagem.read(4096), b''):
        real_size += len(chunk)
        if real_size > max_size:
            return False

    return True


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
