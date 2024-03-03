import os
from typing import List, Annotated

from fastapi import FastAPI, Response, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.responses import FileResponse

import models
import repositories.receita_repository
from orm import Session, SessionDep

from settings import settings


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def read_root():
    return {"health": "ok"}


@app.get('/receitas')
async def get_receitas(session: SessionDep) -> List[models.Receita]:
    return repositories.receita_repository.listar_receitas(session)


@app.get('/receitas/{id_receita}')
async def get_receita(session: SessionDep, id_receita: int) -> models.Receita or Response:
    receita = repositories.receita_repository.buscar_receita_por_id(session, id_receita)
    if not receita:
        return Response(status_code=404)

    return receita


@app.post('/receitas')
async def post_receita(
        session: SessionDep,
        request: models.CriarReceita,
) -> models.Receita:
    return repositories.receita_repository.criar_receita(session, request)


@app.post('/receitas/imagem')
async def post_imagem_receita(
        imagem: UploadFile = File(...),
) -> str:
    return repositories.receita_repository.salvar_imagem_receita(imagem)


@app.put('/receitas/{id_receita}')
async def put_receita(
        session: SessionDep,
        id_receita: int,
        request: models.CriarReceita,
) -> models.Receita:
    return repositories.receita_repository.atualizar_receita(session, id_receita, request)


@app.delete('/receitas/{id_receita}')
async def delete_receita(session: SessionDep, id_receita: int):
    return repositories.receita_repository.deletar_receita(session, id_receita)
