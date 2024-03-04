import datetime
import os
import random
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
        session.rollback.assert_called_once()


class TestReceitaRepositorySalvarImagemReceita(TestCase):
    @patch('receita_repository.uuid4')
    @patch('clients.s3_client.upload_file')
    def test_salvar_imagem_receita(self, mock_s3_client, mock_uuid4):
        mock_uuid4.return_value = '1234'
        mock_s3_client.return_value = 'http://localhost:8002/imagens-receitas/1234.jpg'

        imagem = Mock()
        imagem.filename = 'imagem.jpg'
        imagem.file = b'conteudo'

        url = receita_repository.salvar_imagem_receita(imagem)

        self.assertEqual(url, 'http://localhost:8002/imagens-receitas/1234.jpg')
        mock_uuid4.assert_called_once()
        mock_s3_client.assert_called_once_with(imagem.file, 'imagens-receitas/1234.jpg')

    @patch('receita_repository.uuid4')
    @patch('clients.s3_client.upload_file')
    def test_salvar_imagem_receita_com_erro(self, mock_s3_client, mock_uuid4):
        mock_uuid4.return_value = '1234'
        mock_s3_client.side_effect = Exception('Erro')

        imagem = Mock()
        imagem.filename = 'imagem.jpg'
        imagem.file = b'conteudo'

        with self.assertRaises(Exception):
            receita_repository.salvar_imagem_receita(imagem)
        mock_uuid4.assert_called_once()
        mock_s3_client.assert_called_once_with(imagem.file, 'imagens-receitas/1234.jpg')


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


class TestReceitaRepositoryImagemReceitaEValida(TestCase):
    @patch('receita_repository.filetype')
    def test_imagem_receita_e_valida(self, mock_filetype):
        imagem = Mock()
        imagem.seek = Mock()
        imagem.read.side_effect = [b'conteudo', b'']
        mock_filetype.guess.return_value.mime = 'image/jpeg'

        valido = receita_repository.imagem_receita_e_valida(imagem)

        self.assertTrue(valido)

        imagem.seek.assert_called_once_with(0)
        self.assertEqual(imagem.read.call_count, 2)
        self.assertEqual(imagem.read.call_args_list, [((261,),), ((4096,),)])
        mock_filetype.guess.assert_called_once_with(b'conteudo')

    @patch('receita_repository.filetype')
    def test_imagem_receita_e_valida_sem_mime(self, mock_filetype):
        imagem = Mock()
        imagem.seek = Mock()
        imagem.read.side_effect = [b'conteudo', b'']
        mock_filetype.guess.return_value = None

        valido = receita_repository.imagem_receita_e_valida(imagem)

        self.assertFalse(valido)

        imagem.seek.assert_called_once_with(0)
        imagem.read.assert_called_once_with(261)
        mock_filetype.guess.assert_called_once_with(b'conteudo')

    @patch('receita_repository.filetype')
    def test_imagem_receita_e_valida_mime_invalido(self, mock_filetype):
        imagem = Mock()
        imagem.seek = Mock()
        imagem.read.side_effect = [b'conteudo', b'']
        mock_filetype.guess.return_value.mime = 'image/gif'

        valido = receita_repository.imagem_receita_e_valida(imagem)

        self.assertFalse(valido)

        imagem.seek.assert_called_once_with(0)
        imagem.read.assert_called_once_with(261)
        mock_filetype.guess.assert_called_once_with(b'conteudo')

    @patch('receita_repository.filetype')
    def test_imagem_receita_e_valida_tamanho_invalido(self, mock_filetype):
        imagem = Mock()
        imagem.seek = Mock()
        big_file = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(2 * 1024 * 1024 + 1)])
        chunks = [big_file[i:i + 4096] for i in range(0, len(big_file), 4096)]
        imagem.read.side_effect = [b'conteudo', *chunks]
        mock_filetype.guess.return_value.mime = 'image/jpeg'

        valido = receita_repository.imagem_receita_e_valida(imagem)

        self.assertFalse(valido)

        imagem.seek.assert_called_once_with(0)
        self.assertEqual(imagem.read.call_count, 1 + (2 * 1024 * 1024) // 4096 + 1)
