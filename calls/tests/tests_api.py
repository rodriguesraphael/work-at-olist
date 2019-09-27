from rest_framework.test import APITestCase, APIClient
from calls.models import CallLog, CallInvoice


class CallLogTestCase(APITestCase):

    def setUp(self):
        self.uri_call_log = '/call-log'
        self.client = APIClient()

    def test_post_call(self):
        data = {
            "source": "41987654321",
            "destination": "1196385274",
            "call_id": '1',
            "type": 'start',
            "timestamp": '2016-02-29T12:00:00Z'
        }
        call_start = self.client.post(self.uri_call_log, data, format='json')
        self.assertEqual(call_start.status_code, 201)
        data_end = {
            'type': 'end',
            'timestamp': '2016-02-29T14:00:00Z',
            'call_id': '1'
        }
        call_end = self.client.post(self.uri_call_log, data_end, format='json')
        self.assertEqual(call_end.status_code, 201)
        self.assertEqual(CallLog.objects.count(), 2)
        # Tests for automatic creation of a call invoice
        self.assertEqual(CallInvoice.objects.count(), 1)


class CallInvoiceTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.source = '41998986565'
        data_start = {
            'type': 'start',
            'source': self.source,
            'call_id': 1,
            'destination': '11998986565',
            'timestamp': '2018-02-28T21:57:13Z'
        }
        self.client.post('/call-log', data_start, format='json')
        data_end = {
            'type': 'end',
            'call_id': 1,
            'timestamp': '2018-03-01T22:10:56Z',
        }
        self.client.post('/call-log', data_end, format='json')

    def test_call_reference_month(self):
        response = self.client.get(
            '/call-invoice/{source}?date={date}'.format(
                source=self.source,
                date='032018'
            ),
            follow=True
        )
        self.assertEqual(len(response.data), 1)

    def test_call_invoice_not_found(self):
        response = self.client.get(
            '/call-invoice/{source}'.format(
                source='000000000'
            ),
            follow=True
        )
        self.assertEqual(response.status_code, 404)


class BadRequestsTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_error_post_call_without_source(self):
        data = {
            "destination": "1196385274",
            "type": 'start',
            "call_id": 1,
            "timestamp": '2016-02-29T12:00:00Z'
        }
        call_start = self.client.post('/call-log', data, format='json')
        self.assertEqual(call_start.status_code, 400)

    def test_error_post_call_without_destination(self):
        data = {
            "source": "41987654321",
            "type": 'start',
            "call_id": 1,
            "timestamp": '2016-02-29T12:00:00Z'
        }
        call_start = self.client.post('/call-log', data, format='json')
        self.assertEqual(call_start.status_code, 400)

    def test_invalid_source_and_destination_number(self):
        data = {
            "source": "abc",
            "destination": "xyz",
            "type": 'start',
            "call_id": 1,
            "timestamp": '2016-02-29T12:00:00Z'
        }
        call_start = self.client.post('/call-log', data, format='json')
        self.assertEqual(call_start.status_code, 400)

    def test_invalid_timestamp_post(self):
        data = {
            "source": "41987654321",
            "destination": "1196385274",
            "call_id": 1,
            "type": 'start',
            "timestamp": "invalid timestamp"
        }
        call_start = self.client.post('/call-log', data, format='json')
        self.assertEqual(call_start.status_code, 400)

    def test_end_timestamp_greater_start_timestamp(self):
        data = {
            "source": "41987654321",
            "destination": "1196385274",
            "call_id": 1,
            "type": 'start',
            "timestamp": '2016-02-29T12:00:00Z'
        }
        call_start = self.client.post('/call-log', data, format='json')
        self.assertEqual(call_start.status_code, 201)
        data_end = {
            'type': 'end',
            'timestamp': '2016-02-29T11:00:00Z',
            'call_id': 1
        }
        call_end = self.client.post('/call-log', data_end, format='json')
        self.assertEqual(call_end.status_code, 400)
