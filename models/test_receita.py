from unittest import TestCase

from models import CriarReceita


class TestCriarReceita(TestCase):
    def test_should_fail_when_no_name_is_provided(self):
        with self.assertRaises(ValueError) as context:
            CriarReceita(
                tipo='tipo',
                ingredientes=[],
                modo_de_preparo='modo de preparo',
                imagem='http://image.com'
            )

    def test_should_fail_when_no_tipo_is_provided(self):
        with self.assertRaises(ValueError) as context:
            CriarReceita(
                nome='nome',
                ingredientes=[],
                modo_de_preparo='modo de preparo',
                imagem='http://image.com'
            )

    def test_should_fail_when_no_ingredientes_is_provided(self):
        with self.assertRaises(ValueError) as context:
            CriarReceita(
                nome='nome',
                tipo='tipo',
                modo_de_preparo='modo de preparo',
                imagem='http://image.com'
            )

    def test_should_fail_when_no_imagem_is_provided(self):
        with self.assertRaises(ValueError) as context:
            CriarReceita(
                nome='nome',
                tipo='tipo',
                ingredientes=[],
                modo_de_preparo='modo de preparo'
            )

    def test_should_fail_when_imagem_is_not_a_valid_url(self):
        with self.assertRaises(ValueError) as context:
            CriarReceita(
                nome='nome',
                tipo='tipo',
                ingredientes=[],
                modo_de_preparo='modo de preparo',
                imagem='invalid_url'
            )

    def test_should_fail_when_imagem_is_a_valid_url_but_not_http(self):
        with self.assertRaises(ValueError) as context:
            CriarReceita(
                nome='nome',
                tipo='tipo',
                ingredientes=[],
                modo_de_preparo='modo de preparo',
                imagem='ftp://image.com'
            )

    def test_should_fail_when_imagem_is_a_valid_url_but_not_https(self):
        with self.assertRaises(ValueError) as context:
            CriarReceita(
                nome='nome',
                tipo='tipo',
                ingredientes=[],
                modo_de_preparo='modo de preparo',
                imagem='ftp://image.com'
            )

    def test_should_work_when_all_fields_are_provided(self):
        CriarReceita(
            nome='nome',
            tipo='tipo',
            ingredientes=[],
            modo_de_preparo='modo de preparo',
            imagem='http://image.com'
        )
        self.assertTrue(True)
