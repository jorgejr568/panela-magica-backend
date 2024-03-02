from typing import List

from fastapi import FastAPI, Response
from sqlalchemy import create_engine

import models
import repositories.receita_repository
from orm import Session

from settings import settings


engine = create_engine(settings().database_url, echo=True).connect()

app = FastAPI()


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


@app.on_event('shutdown')
async def on_shutdown():
    print('Shutting down')
    engine.close()
    print('Engine closed')
