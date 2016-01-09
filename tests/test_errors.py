from tests.base import DemoTest

class TestErrors(DemoTest):
    def test_non_mapped_url_returns_404_error(self):
        response = self.client.get('abc1234')
        self.assert404(response)
        self.assertTrue(self.check_content_type(response))

    def test_invalid_request_returns_422_error(self):
        response = self.client.post('api/users', data=dict(invalid_key='not real data'))
        self.assertStatus(response, 422)
        self.assertEqual(response.json, dict(message='422: Unprocessable Entity'))
