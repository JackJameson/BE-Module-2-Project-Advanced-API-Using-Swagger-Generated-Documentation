from app import create_app
from app.models import db, Customer, Mechanic, ServiceTicket, Inventory
from app.utils.util import encode_token
import unittest
from datetime import date

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

        self.customer = Customer(name="Test Customer", email="cust@test.com", phone="1234567890", password="password")
        self.mechanic = Mechanic(name="Test Mechanic", email="mech@test.com", phone="1234567899", salary=50000)
        self.part = Inventory(name="Oil Filter", price=15.50)

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            db.session.add(self.customer)
            db.session.add(self.mechanic)
            db.session.add(self.part)
            db.session.commit()

            self.ticket = ServiceTicket(
                VIN="VIN123456789", 
                service_date=date(2025, 1, 1), 
                service_desc="Initial Service", 
                customer_id=self.customer.id
            )
            db.session.add(self.ticket)
            db.session.commit()

            self.customer_id = self.customer.id
            self.mechanic_id = self.mechanic.id
            self.part_id = self.part.id
            self.ticket_id = self.ticket.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_service_ticket(self):
        ticket_payload = {
            "VIN": "NEWVIN98765",
            "service_date": "2025-02-01",
            "service_desc": "Brake Change",
            "customer_id": self.customer_id
        }
        response = self.client.post('/service_tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['VIN'], "NEWVIN98765")

    def test_create_invalid_ticket(self):
        ticket_payload = {
            "VIN": "BADVIN",
            "service_date": "2025-02-01",
            "service_desc": "Brake Change"
        }
        response = self.client.post('/service_tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 400)

    def test_get_service_tickets(self):
        response = self.client.get('/service_tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json, list))
        self.assertEqual(len(response.json), 1)

    def test_assign_mechanic(self):
        url = f'/service_tickets/{self.ticket_id}/assign-mechanic/{self.mechanic_id}'
        response = self.client.put(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("successfully assigned", response.json['message'])

    def test_assign_mechanic_already_assigned(self):
        url = f'/service_tickets/{self.ticket_id}/assign-mechanic/{self.mechanic_id}'
        self.client.put(url)
        
        response = self.client.put(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("already assigned", response.json['error'])

    def test_remove_mechanic(self):
        assign_url = f'/service_tickets/{self.ticket_id}/assign-mechanic/{self.mechanic_id}'
        self.client.put(assign_url)

        remove_url = f'/service_tickets/{self.ticket_id}/remove-mechanic/{self.mechanic_id}'
        response = self.client.put(remove_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("successfully removed", response.json['message'])

    def test_get_my_service_tickets(self):
        token = encode_token(self.customer_id)
        headers = {'Authorization': f"Bearer {token}"}

        response = self.client.get('/service_tickets/my-tickets', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['VIN'], "VIN123456789")

    def test_edit_service_ticket(self):
        edit_payload = {
            "add_mechanic_ids": [self.mechanic_id],
            "remove_mechanic_ids": []
        }
        
        response = self.client.put(f'/service_tickets/{self.ticket_id}', json=edit_payload)
        
        self.assertEqual(response.status_code, 200)
        mechanic_list = response.json['mechanics']
        self.assertTrue(any(m['id'] == self.mechanic_id for m in mechanic_list))

    def test_add_part_to_ticket(self):
        url = f'/service_tickets/{self.ticket_id}/add-part/{self.part_id}'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("successfully added part", response.json['message'])