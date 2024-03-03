import datetime
import os
from unittest import TestCase
from unittest.mock import Mock, patch
import models
import orm
import receita_repository

mock_receita = orm.Receita(
    id=1,
    nome='Receita 1',
    tipo='Tipo 1',
    ingredientes=[
        orm.Ingrediente(
            id=1,
            nome='Ingrediente 1',
            quantidade='1 xícara'
        )
    ],
    modo_de_preparo="# Modo de preparo\n\nPasso 1\nPasso 2\nPasso 3\n\n# Observações\n\nObservação "
                    "1\nObservação 2\nObservação 3\n",
    criador='Criador 1',
    imagem='http://localhost/imagem.jpg',
    data_de_criacao=datetime.datetime.utcnow()
)


class TestReceitaRepositoryListarReceitas(TestCase):
    def test_listar_receitas(self):
        session = Mock()
        session.execute.return_value.scalars.return_value.all.return_value = [mock_receita]

        receitas = receita_repository.listar_receitas(session)

        self.assertEqual(receitas, [mock_receita.to_dto()])
        session.execute.assert_called_once()

    def test_listar_receitas_vazia(self):
        session = Mock()
        session.execute.return_value.scalars.return_value.all.return_value = []

        receitas = receita_repository.listar_receitas(session)

        self.assertEqual(receitas, [])
        session.execute.assert_called_once()

    def test_listar_receitas_falha(self):
        session = Mock()
        session.execute.side_effect = Exception('Erro')

        with self.assertRaises(Exception):
            receita_repository.listar_receitas(session)
        session.execute.assert_called_once()


class TestReceitaRepositoryBuscarReceitaPorId(TestCase):
    def test_buscar_receita_por_id(self):
        session = Mock()
        session.execute.return_value.scalar.return_value = mock_receita

        receita = receita_repository.buscar_receita_por_id(session, 1)

        self.assertEqual(receita, mock_receita.to_dto())
        session.execute.assert_called_once()

    def test_buscar_receita_por_id_nao_encontrada(self):
        session = Mock()
        session.execute.return_value.scalar.return_value = None

        receita = receita_repository.buscar_receita_por_id(session, 1)

        self.assertIsNone(receita)
        session.execute.assert_called_once()

    def test_buscar_receita_por_id_falha(self):
        session = Mock()
        session.execute.side_effect = Exception('Erro')

        with self.assertRaises(Exception):
            receita_repository.buscar_receita_por_id(session, 1)
        session.execute.assert_called_once()


class TestReceitaRepositoryCriarReceita(TestCase):
    @patch('receita_repository.uuid4')
    def test_criar_receita(self, mock_uuid4):
        def mock_add_fn(receita):
            receita.id = mock_receita.id
            receita.data_de_criacao = mock_receita.data_de_criacao

        session = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.add.side_effect = mock_add_fn

        receita = models.CriarReceita(
            nome='Receita 1',
            tipo='Tipo 1',
            ingredientes=[
                models.Ingrediente(
                    nome='Ingrediente 1',
                    quantidade='1 xícara'
                )
            ],
            modo_de_preparo="# Modo de preparo\n\nPasso 1\nPasso 2\nPasso 3\n\n# Observações\n\nObservação "
                            "1\nObservação 2\nObservação 3\n",
            criador='Criador 1',
            imagem=mock_receita.imagem,
        )

        nova_receita = receita_repository.criar_receita(session, receita)

        self.assertEqual(nova_receita, mock_receita.to_dto())
        session.add.assert_called_once()
        session.commit.assert_called_once()

    def test_criar_receita_falha(self):
        session = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.add.side_effect = Exception('Erro')

        receita = models.CriarReceita(
            nome='Receita 1',
            tipo='Tipo 1',
            ingredientes=[
                models.Ingrediente(
                    nome='Ingrediente 1',
                    quantidade='1 xícara'
                )
            ],
            modo_de_preparo="# Modo de preparo\n\nPasso 1\nPasso 2\nPasso 3\n\n# Observações\n\nObservação "
                            "1\nObservação 2\nObservação 3\n",
            criador='Criador 1',
            imagem='http://localhost/imagem.jpg',
        )

        with self.assertRaises(Exception):
            receita_repository.criar_receita(session, receita)
        session.add.assert_called_once()
        session.commit.assert_not_called()


class TestReceitaRepositorySalvarImagemReceita(TestCase):
    @patch('receita_repository.uuid4')
    @patch('receita_repository.settings')
    @patch('builtins.open')
    def test_salvar_imagem_receita(self, mock_open, mock_settings, mock_uuid4):
        class MockSettings:
            def __init__(self, api_url, storage_path):
                self.api_url = api_url
                self.storage_path = storage_path
        mock_uuid4.return_value = '1234'
        mock_settings.return_value = MockSettings('http://localhost:8002', '/mock-settings')
        mock_open.return_value.__enter__.return_value = Mock()

        imagem = Mock()
        imagem.filename = 'imagem.jpg'
        imagem.file.read.return_value = b'conteudo'

        url = receita_repository.salvar_imagem_receita(imagem)

        self.assertEqual(url, 'http://localhost:8002/imagens-receitas/1234.jpg')
        mock_open.assert_called_once()
        imagem.file.read.assert_called_once()
        assert len(mock_settings.mock_calls) == 2
        mock_uuid4.assert_called_once()

        mock_open.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg', 'wb')
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(b'conteudo')

    @patch('receita_repository.uuid4')
    @patch('receita_repository.settings')
    @patch('builtins.open')
    def test_salvar_imagem_receita_com_erro(self, mock_open, mock_settings, mock_uuid4):
        class MockSettings:
            def __init__(self, api_url, storage_path):
                self.api_url = api_url
                self.storage_path = storage_path
        mock_uuid4.return_value = '1234'
        mock_settings.return_value = MockSettings('http://localhost:8002', '/mock-settings')
        mock_open.side_effect = Exception('Erro')

        imagem = Mock()
        imagem.filename = 'imagem.jpg'
        imagem.file.read.return_value = b'conteudo'

        with self.assertRaises(Exception):
            receita_repository.salvar_imagem_receita(imagem)
        mock_open.assert_called_once()
        imagem.file.read.assert_not_called()
        mock_settings.assert_called_once()
        mock_uuid4.assert_called_once()
        mock_open.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg', 'wb')
        mock_open.return_value.__enter__.return_value.write.assert_not_called()


class TestReceitaRepositoryBuscarImagemReceita(TestCase):
    @patch('receita_repository.settings')
    @patch('os.path')
    @patch('os.access')
    def test_buscar_imagem_receita(self, mock_access, mock_os_path, mock_settings):
        class MockSettings:
            def __init__(self, storage_path):
                self.storage_path = storage_path
        mock_settings.return_value = MockSettings('/mock-settings')
        mock_os_path.exists.return_value = True
        mock_os_path.isfile.return_value = True
        mock_access.return_value = True

        absolute_path = receita_repository.buscar_imagem_receita('1234.jpg')

        self.assertEqual(absolute_path, '/mock-settings/imagens-receitas/1234.jpg')
        mock_os_path.exists.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg')
        mock_os_path.isfile.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg')
        mock_access.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg', os.R_OK)
        mock_settings.assert_called_once()

    @patch('receita_repository.settings')
    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.access')
    def test_buscar_imagem_receita_nao_encontrada(self, mock_access, mock_isfile, mock_exists, mock_settings):
        class MockSettings:
            def __init__(self, storage_path):
                self.storage_path = storage_path
        mock_settings.return_value = MockSettings('/mock-settings')
        mock_exists.return_value = False

        absolute_path = receita_repository.buscar_imagem_receita('1234.jpg')

        self.assertIsNone(absolute_path)
        mock_exists.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg')
        mock_isfile.assert_not_called()
        mock_access.assert_not_called()
        mock_settings.assert_called_once()

    @patch('receita_repository.settings')
    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.access')
    def test_buscar_imagem_receita_com_erro(self, mock_access, mock_isfile, mock_exists, mock_settings):
        class MockSettings:
            def __init__(self, storage_path):
                self.storage_path = storage_path
        mock_settings.return_value = MockSettings('/mock-settings')
        mock_exists.return_value = True
        mock_isfile.return_value = False


        absolute_path = receita_repository.buscar_imagem_receita('1234.jpg')

        self.assertIsNone(absolute_path)
        mock_exists.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg')
        mock_isfile.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg')
        mock_access.assert_not_called()
        mock_settings.assert_called_once()

    @patch('receita_repository.settings')
    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.access')
    def test_buscar_imagem_receita_sem_permissao(self, mock_access, mock_isfile, mock_exists, mock_settings):
        class MockSettings:
            def __init__(self, storage_path):
                self.storage_path = storage_path
        mock_settings.return_value = MockSettings('/mock-settings')
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_access.return_value = False

        absolute_path = receita_repository.buscar_imagem_receita('1234.jpg')

        self.assertIsNone(absolute_path)
        mock_exists.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg')
        mock_isfile.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg')
        mock_access.assert_called_once_with('/mock-settings/imagens-receitas/1234.jpg', os.R_OK)
        mock_settings.assert_called_once()


class TestReceitaRepositoryDeletarReceita(TestCase):
    def test_deletar_receita(self):
        session = Mock()
        session.execute = Mock()
        session.commit = Mock()

        receita_repository.deletar_receita(session, 1)

        session.execute.assert_called_once()
        session.commit.assert_called_once()

    def test_deletar_receita_falha(self):
        session = Mock()
        session.execute = Mock()
        session.commit = Mock()
        session.execute.side_effect = Exception('Erro')

        with self.assertRaises(Exception):
            receita_repository.deletar_receita(session, 1)
        session.execute.assert_called_once()
        session.commit.assert_not_called()
        session.rollback.assert_called_once()


class TestReceitaRepositoryAtualizarReceita(TestCase):
    def test_atualizar_receita(self):
        session = Mock()
        session.execute.return_value.scalar.return_value = mock_receita
        session.commit = Mock()

        receita = models.CriarReceita(
            nome='Receita 1',
            tipo='Tipo 1',
            ingredientes=[
                models.Ingrediente(
                    nome='Ingrediente 1',
                    quantidade='1 xícara'
                )
            ],
            modo_de_preparo="# Modo de preparo\n\nPasso 1\nPasso 2\nPasso 3\n\n# Observações\n\nObservação "
                            "1\nObservação 2\nObservação 3\n",
            criador='Criador 1',
            imagem='http://localhost/imagem.jpg',
        )

        nova_receita = receita_repository.atualizar_receita(session, 1, receita)

        self.assertEqual(nova_receita, mock_receita.to_dto())
        session.execute.assert_called_once()
        session.commit.assert_called_once()

    def test_atualizar_receita_falha(self):
        session = Mock()
        session.execute.side_effect = Exception('Erro')

        receita = models.CriarReceita(
            nome='Receita 1',
            tipo='Tipo 1',
            ingredientes=[
                models.Ingrediente(
                    nome='Ingrediente 1',
                    quantidade='1 xícara'
                )
            ],
            modo_de_preparo="# Modo de preparo\n\nPasso 1\nPasso 2\nPasso 3\n\n# Observações\n\nObservação "
                            "1\nObservação 2\nObservação 3\n",
            criador='Criador 1',
            imagem='http://localhost/imagem.jpg',
        )

        with self.assertRaises(Exception):
            receita_repository.atualizar_receita(session, 1, receita)
        session.execute.assert_called_once()
        session.commit.assert_not_called()
        session.rollback.assert_called_once()