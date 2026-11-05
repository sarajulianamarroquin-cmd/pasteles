from app import app


def test_products_page():
    client = app.test_client()
    response = client.get('/products')
    assert response.status_code == 200
    assert b'Nuestros Productos' in response.data


def test_index_page():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'SweetDreams' in response.data
