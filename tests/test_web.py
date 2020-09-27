from tests.fixtures import *

from lada.dike import maintenance


def test_get_article(client):
    result = client.get("/article/")
    assert result.status_code == 200
