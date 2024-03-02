from unittest import TestCase
from unittest.mock import Mock, patch

import models
import orm
import receita_repository


class TestReceitaRepositoryListarReceitas(TestCase):
    def test_listar_receitas(self):
        session = Mock()
        receita = orm.Receita(
            id=1,
            nome='Receita 1',
            tipo=models.ReceitaTipo.PUDIM,
            ingredientes=[
                orm.Ingrediente(
                    id=1,
                    nome='Ingrediente 1',
                    quantidade='1 xícara'
                )
            ],
            modo_de_preparo=['Passo 1', 'Passo 2']
        )

        session.execute.return_value.scalars.return_value.all.return_value = [receita]

        receitas = receita_repository.listar_receitas(session)

        self.assertEqual(receitas, [receita.to_dto()])
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
        mock_receita = orm.Receita(
            id=1,
            nome='Receita 1',
            tipo=models.ReceitaTipo.PUDIM,
            ingredientes=[
                orm.Ingrediente(
                    id=1,
                    nome='Ingrediente 1',
                    quantidade='1 xícara'
                )
            ],
            modo_de_preparo=['Passo 1', 'Passo 2']
        )

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