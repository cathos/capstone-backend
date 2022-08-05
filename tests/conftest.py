import pytest
from app import create_app
# from app import db

test_data_1 = '4c:20:07:00:ff:ff:ff:dd:00:00:00:00:84:79:04:00:20:18:01:00:01:f4:00:00:07:93:00:00:00:00:42:00:02:00:df:00'

test_status_data_1 = "0a:da:e7:41:00:c0:f2:3c:ad:1e:e7:41:00:00:00:00:cb:61:82:c2:00:00:00:00:02:06:00:00:00:00:54:43:49:f3:07:42:3d:0a:f5:41:00:0a:00:00:00:00:00:00:79:00:00:00:84:03:00:00:00:00:00:00:ff:ff:ff:aa"
test_status_data_2 = "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:c6:e3:8d:52:5d:17:00:00:00:00:00:00:00:00:00:00:00:00:00:00:1a:d2:9e:03:e6:00:aa:37:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:ff:ff:ff:bb"

@pytest.fixture
def app():
    # create the app with a test config dictionary
    app = create_app({"TESTING": True})

    with app.app_context():
        # db.create_all()
        yield app

    # close and remove the temporary database
    # with app.app_context():
        # db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def roaster_info():
    r_info = "some_roaster_info"
    return r_info


