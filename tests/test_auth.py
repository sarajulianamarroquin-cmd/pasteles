from app import app


def test_register_and_login():
    client = app.test_client()
    response = client.post('/register', data={'name': 'Ana', 'email': 'ana@test.com', 'password': 'secret123'}, follow_redirects=True)
    assert response.status_code == 200
    response = client.post('/login', data={'email': 'ana@test.com', 'password': 'secret123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Bienvenido' in response.data or b'SweetDreams' in response.data
