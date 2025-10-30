import unittest
from app import app, calculate_total_load, size_solar_panels, suggest_panels, size_batteries, size_inverter, size_mppt

class TestSolarCalculator(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_calculate_total_load(self):
        appliances = {
            'appliance_name': ['TV', 'Fridge'],
            'quantity': ['1', '1'],
            'wattage': ['100', '200'],
            'hours': ['5', '12']
        }
        self.assertAlmostEqual(calculate_total_load(appliances), 2900)

    def test_size_solar_panels(self):
        self.assertAlmostEqual(size_solar_panels(2900, 5.5), 685.45, places=2)

    def test_suggest_panels(self):
        suggestions = suggest_panels(685.45)
        self.assertIn('3 x 250W panels', suggestions)
        self.assertIn('2 x 350W panels', suggestions)
        self.assertIn('2 x 400W panels', suggestions)

    def test_size_batteries(self):
        self.assertAlmostEqual(size_batteries(2900, 24), 483.33, places=2)

    def test_size_inverter(self):
        appliances = {
            'appliance_name': ['TV', 'Fridge'],
            'quantity': ['1', '1'],
            'wattage': ['100', '200'],
            'hours': ['5', '12']
        }
        self.assertAlmostEqual(size_inverter(appliances), 375)

    def test_size_mppt(self):
        self.assertAlmostEqual(size_mppt(685.45, 24), 35.70, places=2)

    def test_index_route(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_calculate_route(self):
        result = self.app.post('/calculate', data={
            'appliance_name[]': ['TV', 'Fridge'],
            'quantity[]': ['1', '1'],
            'wattage[]': ['100', '200'],
            'hours[]': ['5', '12'],
            'address': 'Lagos, Nigeria',
            'system_voltage': '24'
        })
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Solar System Design Report', result.data)

if __name__ == '__main__':
    unittest.main()
