from app import app


def test_cart_flow():
    client = app.test_client()
    response = client.post('/cart/add/1', data={'quantity': 2}, follow_redirects=True)
    assert response.status_code == 200
    response = client.get('/cart')
    assert response.status_code == 200
    assert b'Pastel de Fresa' in response.data
