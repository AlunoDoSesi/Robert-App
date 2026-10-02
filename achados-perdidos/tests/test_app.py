from io import BytesIO
from pathlib import Path

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "DATABASE": str(tmp_path / "test.db"),
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )


@pytest.fixture()
def client(app):
    return app.test_client()


def publish(client, **overrides):
    data = {
        "tipo": "perdido",
        "nome": "Chaveiro azul",
        "descricao": "Tem uma estrela prateada e duas chaves.",
        "local": "Biblioteca central",
        "contato": "ana@example.com",
    }
    data.update(overrides)
    return client.post("/cadastrar", data=data, follow_redirects=True)


def test_home_is_available(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"O que foi perdido pode" in response.data
    assert b"O mural est\xc3\xa1 pronto" in response.data


def test_publish_item_and_show_feedback(client):
    response = publish(client)
    assert response.status_code == 200
    assert b"Chaveiro azul" in response.data
    assert b"Item publicado no mural" in response.data


def test_filter_and_search(client):
    publish(client)
    publish(
        client,
        tipo="encontrado",
        nome="Carteira preta",
        descricao="Carteira encontrada perto do port\xc3\xa3o.",
        local="Port\xc3\xa3o principal",
    )

    found = client.get("/?tipo=encontrado")
    assert b"Carteira preta" in found.data
    assert b"Chaveiro azul" not in found.data

    searched = client.get("/?q=estrela")
    assert b"Chaveiro azul" in searched.data
    assert b"Carteira preta" not in searched.data


def test_item_can_be_marked_as_resolved(client):
    publish(client)
    response = client.post("/itens/1/resolver", follow_redirects=True)
    assert response.status_code == 200
    assert b"Aviso marcado como resolvido" in response.data
    assert b"Caso resolvido" in response.data


def test_image_upload_is_saved(client, app):
    response = client.post(
        "/cadastrar",
        data={
            "tipo": "encontrado",
            "nome": "Guarda-chuva",
            "descricao": "Guarda-chuva roxo.",
            "local": "Sala 2",
            "contato": "(11) 99999-0000",
            "imagem": (BytesIO(b"fake-image"), "guarda-chuva.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Guarda-chuva" in response.data
    assert any(Path(app.config["UPLOAD_FOLDER"]).iterdir())
