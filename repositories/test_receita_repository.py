import datetime
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
    imagem='Imagem 1',
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