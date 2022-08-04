import pytest

# @pytest.mark.skip(reason="No way to test this feature yet")
def test_get_roaster_info(client):
    # Act
    response = client.get("/info")
    response_body = response.get_json()
    print(response_body)
    print(response.status_code)
    print(response)
    # Assert
    assert response.status_code == 200
    assert response_body == "info_response"