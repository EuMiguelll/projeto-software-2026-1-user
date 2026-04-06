def test_get_user_404(client):

    # Teste de Recuperação
    get_response = client.get(f"/users/1")
    assert get_response.status_code == 404 

def test_create_and_get_user_and_delete_user(client):
    # Cria o usuário
    create_response = client.post("/users", json={
        "name": "João",
        "email": "joao@email.com"
    })
    assert create_response.status_code == 201
    user = create_response.get_json()
    user_id = user["id"]

    # Recupera o usuário
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["name"] == "João"
    assert get_response.get_json()["email"] == "joao@email.com"

    # Deleta o usuário
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    # Verifica que foi deletado
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

def test_create_and_delete_user(client):
    # Cria o usuário
    create_response = client.post("/users", json={
        "name": "Maria",
        "email": "maria@email.com"
    })
    assert create_response.status_code == 201
    user = create_response.get_json()
    user_id = user["id"]

    # Deleta o usuário
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    # Verifica que foi deletado
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

def test_create_two_users_and_list_and_delete_both_users(client):
    # Cria dois usuários
    create_response_1 = client.post("/users", json={
        "name": "Carlos",
        "email": "carlos@email.com"
    })
    assert create_response_1.status_code == 201
    user_1 = create_response_1.get_json()

    create_response_2 = client.post("/users", json={
        "name": "Ana",
        "email": "ana@email.com"
    })
    assert create_response_2.status_code == 201
    user_2 = create_response_2.get_json()

    # Lista os usuários
    list_response = client.get("/users")
    assert list_response.status_code == 200
    users = list_response.get_json()
    user_ids = [u["id"] for u in users]
    assert user_1["id"] in user_ids
    assert user_2["id"] in user_ids

    # Deleta ambos
    delete_response_1 = client.delete(f"/users/{user_1['id']}")
    assert delete_response_1.status_code == 204

    delete_response_2 = client.delete(f"/users/{user_2['id']}")
    assert delete_response_2.status_code == 204

    # Verifica que foram deletados
    get_response_1 = client.get(f"/users/{user_1['id']}")
    assert get_response_1.status_code == 404

    get_response_2 = client.get(f"/users/{user_2['id']}")
    assert get_response_2.status_code == 404