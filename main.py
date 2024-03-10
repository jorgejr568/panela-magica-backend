import json
from typing import List

from fastapi import FastAPI, File, UploadFile, Header, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

import models
import repositories.receita_repository
import services.user_service
from orm import SessionDep

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def auth_middleware(
        session: SessionDep,
        authorization: str = Header(..., description="Token de autorização", alias="X-Authorization"),
):
    try:
        return services.user_service.me(authorization, session=session)
    except services.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    except services.TokenExpiredError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


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
        auth=Depends(auth_middleware)
) -> models.Receita:
    request.assign_criador_id(auth.id)
    return repositories.receita_repository.criar_receita(session, request)


@app.post('/receitas/imagem')
async def post_imagem_receita(
        imagem: UploadFile = File(description="Imagem da receita (png, jpg, jpeg e até 2MB)"),
        _=Depends(auth_middleware),
) -> Response:
    if not repositories.receita_repository.imagem_receita_e_valida(imagem.file):
        return Response(status_code=400, content="Imagem inválida")
    return Response(content=json.dumps(repositories.receita_repository.salvar_imagem_receita(imagem)),
                    media_type="application/json")


@app.put('/receitas/{id_receita}')
async def put_receita(
        session: SessionDep,
        id_receita: int,
        request: models.CriarReceita,
        _=Depends(auth_middleware),
) -> models.Receita:
    return repositories.receita_repository.atualizar_receita(session, id_receita, request)


@app.delete('/receitas/{id_receita}')
async def delete_receita(session: SessionDep, id_receita: int, _=Depends(auth_middleware)) -> Response:
    repositories.receita_repository.deletar_receita(session, id_receita)
    return Response(status_code=204)


@app.post('/users/sign-in')
async def sign_in(
        session: SessionDep,
        request: services.SignInRequest,
) -> Response or models.User:
    try:
        return services.user_service.sign_in(request.username, request.password, session=session)
    except services.CredentialsNotMatchError:
        return Response(status_code=401, content="Credentials not match")


@app.get('/users/me')
async def me(user=Depends(auth_middleware)) -> 'services.MeResponse':
    return user
