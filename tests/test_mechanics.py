from app import create_app
from app.models import db, Mechanic
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(
            name="Fix-It Felix", 
            email="felix@repair.com", 
            phone="555-1234", 
            salary=50000.00
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "Wreck-It Ralph",
            "email": "ralph@destroy.com",
            "phone": "555-9999",
            "salary": 45000.00
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Wreck-It Ralph")

    def test_create_invalid_mechanic(self):
        mechanic_payload = {
            "name": "Incomplete Ian",
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)

    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json, list))
        self.assertEqual(len(response.json), 1)

    def test_get_single_mechanic(self):
        response = self.client.get('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Fix-It Felix")

    def test_get_mechanic_not_found(self):
        response = self.client.get('/mechanics/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Mechanic not found")

    def test_update_mechanic(self):
        update_payload = {
            "name": "Felix Jr.",
            "email": "felix@repair.com", 
            "phone": "555-1234", 
            "salary": 55000.00
        }
        response = self.client.put('/mechanics/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Felix Jr.")
        self.assertEqual(response.json['salary'], 55000.00)

    def test_update_mechanic_not_found(self):
        update_payload = {"name": "Ghost"}
        response = self.client.put('/mechanics/999', json=update_payload)
        self.assertEqual(response.status_code, 404)

    def test_delete_mechanic(self):
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn("deleted successfully", response.json['message'])

        get_response = self.client.get('/mechanics/1')
        self.assertEqual(get_response.status_code, 404)

    def test_top_mechanics(self):
        response = self.client.get('/mechanics/top')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json, list))

    def test_search_mechanic(self):
        response = self.client.get('/mechanics/search?name=Felix')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['name'], "Fix-It Felix")

    def test_search_mechanic_no_results(self):
        response = self.client.get('/mechanics/search?name=Bowser')
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(len(response.json), 0)