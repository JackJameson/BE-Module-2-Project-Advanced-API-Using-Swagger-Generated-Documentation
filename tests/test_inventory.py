from app import create_app
from app.models import db, Inventory
import unittest

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

        self.part = Inventory(name="Spark Plug", price=5.99)

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            db.session.add(self.part)
            db.session.commit()

            self.part_id = self.part.id

    def test_create_inventory_item(self):
        payload = {
            "name": "All-Terrain Tire", 
            "price": 120.50
        }
        response = self.client.post('/inventory/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "All-Terrain Tire")

    def test_create_invalid_inventory_item(self):
        payload = {"name": "Mystery Box"}
        response = self.client.post('/inventory/', json=payload)
        self.assertEqual(response.status_code, 400)

    def test_get_inventory_items(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json, list))
        self.assertEqual(len(response.json), 1)

    def test_get_inventory_item(self):
        response = self.client.get(f'/inventory/{self.part_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Spark Plug")

    def test_get_inventory_item_not_found(self):
        response = self.client.get('/inventory/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Inventory item not found")

    def test_update_inventory_item(self):
        update_payload = {
            "name": "Premium Spark Plug", 
            "price": 8.99
        }
        response = self.client.put(f'/inventory/{self.part_id}', json=update_payload)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Premium Spark Plug")
        self.assertEqual(response.json['price'], 8.99)

    def test_update_inventory_item_not_found(self):
        update_payload = {"name": "Ghost Part", "price": 0.00}
        response = self.client.put('/inventory/999', json=update_payload)
        self.assertEqual(response.status_code, 404)

    def test_delete_inventory_item(self):
        response = self.client.delete(f'/inventory/{self.part_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("deleted successfully", response.json['message'])

        get_response = self.client.get(f'/inventory/{self.part_id}')
        self.assertEqual(get_response.status_code, 404)