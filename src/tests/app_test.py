import unittest
import app as app_module
from app import app, inventories


class TestApp(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        inventories.clear()
        app_module.next_id = 1

    def tearDown(self):
        inventories.clear()

    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Varastot', response.data)

    def test_create_inventory(self):
        response = self.client.post('/inventory/create', data={
            'name': 'Test Inventory',
            'capacity': '100',
            'initial': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Inventory', response.data)
        self.assertEqual(len(inventories), 1)

    def test_create_inventory_without_name(self):
        response = self.client.post('/inventory/create', data={
            'name': '',
            'capacity': '100',
            'initial': '0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(inventories), 0)

    def test_create_inventory_with_invalid_capacity(self):
        response = self.client.post('/inventory/create', data={
            'name': 'Test',
            'capacity': '-10',
            'initial': '0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(inventories), 0)

    def test_view_inventory(self):
        self.client.post('/inventory/create', data={
            'name': 'Test Inventory',
            'capacity': '100',
            'initial': '50'
        })
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Inventory', response.data)

    def test_view_nonexistent_inventory(self):
        response = self.client.get('/inventory/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_update_inventory_name(self):
        self.client.post('/inventory/create', data={
            'name': 'Old Name',
            'capacity': '100',
            'initial': '0'
        })
        response = self.client.post('/inventory/1/update', data={
            'name': 'New Name'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Name', response.data)
        self.assertEqual(inventories[1]['name'], 'New Name')

    def test_add_to_inventory(self):
        self.client.post('/inventory/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial': '0'
        })
        response = self.client.post('/inventory/1/add', data={
            'amount': '25'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(inventories[1]['varasto'].saldo, 25)

    def test_remove_from_inventory(self):
        self.client.post('/inventory/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial': '50'
        })
        response = self.client.post('/inventory/1/remove', data={
            'amount': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(inventories[1]['varasto'].saldo, 30)

    def test_delete_inventory(self):
        self.client.post('/inventory/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial': '0'
        })
        self.assertEqual(len(inventories), 1)
        response = self.client.post(
            '/inventory/1/delete',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(inventories), 0)

    def test_add_invalid_amount(self):
        self.client.post('/inventory/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial': '0'
        })
        response = self.client.post('/inventory/1/add', data={
            'amount': '-5'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(inventories[1]['varasto'].saldo, 0)

    def test_remove_invalid_amount(self):
        self.client.post('/inventory/create', data={
            'name': 'Test',
            'capacity': '100',
            'initial': '50'
        })
        response = self.client.post('/inventory/1/remove', data={
            'amount': '-5'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(inventories[1]['varasto'].saldo, 50)
