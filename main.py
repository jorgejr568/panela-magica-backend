import os
from typing import List, Annotated

from fastapi import FastAPI, Response, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from starlette.responses import FileResponse

import models
import repositories.receita_repository
from orm import Session

from settings import settings

engine = create_engine(settings().database_url, echo=True).connect()

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
    if engine.closed:
        return Response({
            'error': 'Database connection is closed'
        }, status_code=503)

    return {"health": "ok"}


@app.get('/receitas')
async def get_receitas() -> List[models.Receita]:
    return repositories.receita_repository.listar_receitas(Session(engine))


@app.get('/receitas/{id_receita}')
async def get_receita(id_receita: int) -> models.Receita:
    return repositories.receita_repository.buscar_receita_por_id(Session(engine), id_receita)


@app.post('/receitas')
async def post_receita(
        request: models.CriarReceita,
) -> models.Receita:
    return repositories.receita_repository.criar_receita(Session(engine), request)


@app.post('/receitas/imagem')
async def post_imagem_receita(
        imagem: UploadFile = File(...),
) -> str:
    return repositories.receita_repository.salvar_imagem_receita(imagem)


@app.get('/imagens-receitas/{imagem}')
async def get_imagem_receita(imagem: str):
    filename = settings().storage_path + '/imagens-receitas/' + imagem
    if not os.path.exists(filename):
        return Response(status_code=404)

    return FileResponse(filename)


@app.put('/receitas/{id_receita}')
async def put_receita(
        id_receita: int,
        request: models.CriarReceita,
) -> models.Receita:
    return repositories.receita_repository.atualizar_receita(Session(engine), id_receita, request)


@app.delete('/receitas/{id_receita}')
async def delete_receita(id_receita: int):
    return repositories.receita_repository.deletar_receita(Session(engine), id_receita)


@app.on_event('shutdown')
async def on_shutdown():
    print('Shutting down')
    engine.close()
    print('Engine closed')
