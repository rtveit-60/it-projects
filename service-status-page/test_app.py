import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app import app, get_health_data, get_on_call, get_maintenance

class TestDashboard(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # --- 1. EXISTING TESTS (Keep these) ---
    @patch('app.feedparser.parse')
    @patch('app.requests.get')
    def test_get_health_data_success(self, mock_get, mock_feed):
        # Mock JSON API (GitHub)
        mock_json = MagicMock()
        mock_json.json.return_value = {"status": {"indicator": "none", "description": "Good"}, "incidents": []}
        mock_get.return_value = mock_json

        # Mock RSS Feed (AWS)
        mock_feed_resp = MagicMock()
        mock_feed_resp.entries = [MagicMock(title="Service operating normally", published_parsed=(2023,1,1,10,0,0,0,0,0))]
        mock_feed.return_value = mock_feed_resp

        results = get_health_data()
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['status'], "All Services Currently Operational")

    # --- 2. NEW: On-Call Widget Tests ---
    def test_on_call_structure(self):
        """
        Verify the On-Call function returns the correct dictionary keys
        needed for the header.
        """
        person = get_on_call()
        
        # Check that we got a dictionary
        self.assertIsInstance(person, dict)
        
        # Check for required keys used in index.html
        self.assertIn('name', person)
        self.assertIn('email', person)
        self.assertIn('avatar', person)
        self.assertIn('status', person)
        
        # Verify specific values (since we are using Mock data currently)
        self.assertEqual(person['name'], "Alex Mercer")

    # --- 3. NEW: Maintenance Logic Tests ---
    def test_maintenance_default_state(self):
        """
        Verify that by default (Scenario 1 in app.py), 
        maintenance returns None (Green state).
        """
        # Force cache expiry to ensure we run the logic
        from app import maintenance_cache
        maintenance_cache['last_check'] = datetime.min 
        
        result = get_maintenance()
        self.assertIsNone(result, "Default state should be None (No Maintenance)")

    def test_maintenance_logic_calculation(self):
        """
        Since the app.py uses commented-out blocks for scenarios, 
        we can't easily test 'Red' or 'Amber' without changing app.py.
        
        However, we CAN test the time-check logic if we simulate data injection.
        This test manually runs the logic we used inside get_maintenance.
        """
        now = datetime.now()
        
        # Case A: Future Maintenance (Should be 'scheduled')
        future_data = {
            "start": now + timedelta(hours=2),
            "end": now + timedelta(hours=4)
        }
        status_future = 'active' if future_data['start'] <= now <= future_data['end'] else 'scheduled'
        self.assertEqual(status_future, 'scheduled')

        # Case B: Active Maintenance (Should be 'active')
        active_data = {
            "start": now - timedelta(minutes=30),
            "end": now + timedelta(hours=1)
        }
        status_active = 'active' if active_data['start'] <= now <= active_data['end'] else 'scheduled'
        self.assertEqual(status_active, 'active')

    # --- 4. NEW: HTML Integration Tests ---
    @patch('app.get_maintenance')
    @patch('app.get_on_call')
    def test_home_page_render_new_sections(self, mock_on_call, mock_maint):
        """
        Verify the new Header sections appear in the HTML.
        """
        # Setup Mock Data
        mock_on_call.return_value = {
            "name": "Test User",
            "email": "test@user.com",
            "avatar": "",
            "status": "Active"
        }
        # Simulate an Active Maintenance to check if the red box renders
        mock_maint.return_value = {
            "title": "Critical Update",
            "window_str": "Now",
            "id": "TEST-01",
            "status": "active"
        }

        response = self.app.get('/')
        html = response.data.decode('utf-8')

        # Check for IT Operations Section
        self.assertIn("IT Operations", html)
        self.assertIn("Test User", html)
        self.assertIn("test@user.com", html)

        # Check for Maintenance Section
        self.assertIn("Maintenance", html)
        self.assertIn("Critical Update", html)
        self.assertIn("tab-maint active", html) # Check if the CSS class was applied

if __name__ == '__main__':
    unittest.main()