import datetime
import models
import orm
from main import app
from fastapi.testclient import TestClient
from unittest import TestCase
from unittest.mock import patch

client = TestClient(app)


class TestHealth(TestCase):
    def test_health(self):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}


mock_receita = orm.Receita(
    id=1,
    nome='nome',
    tipo='tipo',
    criador='criador',
    imagem='http://imagem.com',
    modo_de_preparo='modo_de_preparo',
    ingredientes=[orm.Ingrediente(nome='nome', quantidade='quantidade')],
    data_de_criacao=datetime.datetime.utcnow(),
)

mock_receita_2 = orm.Receita(
    id=2,
    nome='nome',
    tipo='tipo',
    criador='criador',
    imagem='http://imagem.com',
    modo_de_preparo='modo_de_preparo',
    ingredientes=[orm.Ingrediente(nome='nome', quantidade='quantidade'), orm.Ingrediente(nome='nome2', quantidade='quantidade2')],
    data_de_criacao=datetime.datetime.utcnow(),
)

mock_criar_receita = models.CriarReceita(
    nome='nome',
    tipo='tipo',
    criador='criador',
    imagem='http://imagem.com',
    modo_de_preparo='modo_de_preparo',
    ingredientes=[models.Ingrediente(nome='nome', quantidade='quantidade'), models.Ingrediente(nome='nome2', quantidade='quantidade2')],
)


class TestGetReceitas(TestCase):
    @patch('repositories.receita_repository.listar_receitas', return_value=[mock_receita.to_dto(), mock_receita_2.to_dto()])
    def test_get_receitas(self, mock_listar_receitas):
        response = client.get('/receitas')
        assert response.status_code == 200
        assert response.json() == [mock_receita.to_dto().model_dump(), mock_receita_2.to_dto().model_dump()]

    @patch('repositories.receita_repository.listar_receitas', return_value=[])
    def test_get_receitas_vazia(self, mock_listar_receitas):
        response = client.get('/receitas')
        assert response.status_code == 200
        assert response.json() == []


class TestGetReceita(TestCase):
    @patch('repositories.receita_repository.buscar_receita_por_id', return_value=mock_receita.to_dto())
    def test_get_receita(self, mock_buscar_receita_por_id):
        response = client.get('/receitas/1')
        assert response.status_code == 200
        assert response.json() == mock_receita.to_dto().model_dump()

    @patch('repositories.receita_repository.buscar_receita_por_id', return_value=None)
    def test_get_receita_nao_encontrada(self, mock_buscar_receita_por_id):
        response = client.get('/receitas/1')
        assert response.status_code == 404


class TestPostReceita(TestCase):
    @patch('repositories.receita_repository.criar_receita', return_value=mock_receita.to_dto())
    def test_post_receita(self, mock_repo_criar_receita):
        response = client.post('/receitas', json=mock_criar_receita.model_dump())
        assert response.status_code == 200
        assert response.json() == mock_receita.to_dto().model_dump()

    @patch('repositories.receita_repository.criar_receita', side_effect=Exception('error'))
    def test_post_receita_erro(self, mock_repo_criar_receita):
        with self.assertRaises(Exception):
            client.post('/receitas', json=mock_criar_receita.model_dump())


class TestPostImagemReceita(TestCase):
    @patch('repositories.receita_repository.imagem_receita_e_valida', return_value=True)
    @patch('repositories.receita_repository.salvar_imagem_receita', return_value="http://imagem.com")
    def test_post_imagem_receita(self, mock_imagem_receita_e_valida, mock_salvar_imagem_receita):
        response = client.post('/receitas/imagem', files={'imagem': ('imagem.png', b'conteudo')})
        assert response.status_code == 200
        assert response.json() == "http://imagem.com"

    @patch('repositories.receita_repository.imagem_receita_e_valida', return_value=False)
    def test_post_imagem_receita_erro(self, mock_imagem_receita_e_valida):
        response = client.post('/receitas/imagem', files={'imagem': ('imagem.png', b'conteudo')})
        assert response.status_code == 400


class TestPutReceita(TestCase):
    @patch('repositories.receita_repository.atualizar_receita', return_value=mock_receita.to_dto())
    def test_put_receita(self, mock_atualizar_receita):
        response = client.put('/receitas/1', json=mock_criar_receita.model_dump())
        assert response.status_code == 200
        assert response.json() == mock_receita.to_dto().model_dump()

    @patch('repositories.receita_repository.atualizar_receita', return_value=None)
    def test_put_receita_erro(self, mock_atualizar_receita):
        with self.assertRaises(Exception):
            client.put('/receitas/1', json=mock_criar_receita.model_dump())

