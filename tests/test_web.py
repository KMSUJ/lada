from tests.fixtures import *


def test_get_article(client):
    result = client.get("/article/")
    assert result.status_code == 200
