import unittest
from unittest.mock import patch, MagicMock
from app import app, get_health_data

class TestDashboard(unittest.TestCase):

    def setUp(self):
        # Set up a test client for our Flask app
        self.app = app.test_client()
        self.app.testing = True

    # --- TEST 1: The Core Logic (get_health_data) ---
    @patch('app.feedparser.parse')
    @patch('app.requests.get')
    def test_get_health_data_success(self, mock_get, mock_feed):
        """
        Simulate PERFECT conditions:
        - GitHub API returns 'indicator: none'
        - AWS RSS returns a normal title
        """
        
        # 1. Mock the JSON API Response (GitHub/Atlassian)
        mock_json_response = MagicMock()
        mock_json_response.json.return_value = {
            "status": {"indicator": "none", "description": "Good"},
            "incidents": []
        }
        mock_get.return_value = mock_json_response

        # 2. Mock the RSS Feed Response (AWS)
        mock_feed_response = MagicMock()
        mock_feed_response.entries = [
            MagicMock(title="Service is operating normally", published_parsed=(2023, 10, 27, 10, 0, 0, 0, 0, 0))
        ]
        mock_feed.return_value = mock_feed_response

        # 3. Run the actual function
        results = get_health_data()

        # 4. Assertions (The "Tests")
        
        # Check if we got results back
        self.assertTrue(len(results) > 0)
        
        # Check GitHub logic
        github_result = next((item for item in results if item["name"] == "GitHub"), None)
        self.assertIsNotNone(github_result)
        # Verify our "All Services" text override is working
        self.assertEqual(github_result['status'], "All Services Currently Operational")
        self.assertEqual(github_result['class'], "good")

        # Check AWS logic
        aws_result = next((item for item in results if item["name"] == "AWS EC2"), None)
        self.assertIsNotNone(aws_result)
        self.assertEqual(aws_result['status'], "All Services Currently Operational")

    # --- TEST 2: Error Handling ---
    @patch('app.requests.get')
    def test_api_failure(self, mock_get):
        """
        Simulate a CRASH:
        - The API times out or raises an exception
        """
        # Make requests.get raise an error
        mock_get.side_effect = Exception("Connection Timeout")

        results = get_health_data()

        # Find GitHub (which uses requests.get)
        github_result = next((item for item in results if item["name"] == "GitHub"), None)
        
        # It should handle the crash gracefully, not break the app
        self.assertEqual(github_result['status'], "API Error")
        self.assertEqual(github_result['class'], "critical")

    # --- TEST 3: The Route/Page Load ---
    @patch('app.get_health_data')
    def test_homepage_render(self, mock_health_data):
        """
        Simulate loading the webpage:
        - We mock the heavy lifting data function so the page loads instantly
        - We check if the HTML contains the right keywords
        """
        # Create fake data for the page to render
        mock_health_data.return_value = [{
            "name": "TestService",
            "region": "us-test",
            "status": "Testing OK",
            "class": "good",
            "logo": "",
            "feed": []
        }]

        # Request the home page ('/')
        response = self.app.get('/')

        # Assertions
        self.assertEqual(response.status_code, 200) # 200 OK means page loaded
        
        # Check if our HTML template rendered correctly
        self.assertIn(b"IT Services & Health Dashboard", response.data) # Check Title
        self.assertIn(b"TestService", response.data) # Check if our data appeared
        self.assertIn(b"Incoming Tickets", response.data) # Check if Sidebar appeared

if __name__ == '__main__':
    unittest.main()