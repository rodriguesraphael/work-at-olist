from datetime import datetime
from django.test import TestCase
from calls.models import Call, CallLog, CallInvoice


def parse_date(date_string):
    date_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
    return date_obj


class CallModelsTestCase(TestCase):
    def setUp(self):
        # create calls
        # call 1
        call_1 = Call.objects.create(
            source="41987654321",
            destination="1196385274"
        )
        CallLog.objects.create(
            type='start',
            timestamp=parse_date('2016-02-29T12:00:00Z'),
            call_id=call_1
        )
        CallLog.objects.create(
            type='end',
            timestamp=parse_date('2016-02-29T14:00:00Z'),
            call_id=call_1
        )
        # call 2
        call_2 = Call.objects.create(
            source="41987654321",
            destination="1196385274"
        )
        CallLog.objects.create(
            type='start',
            timestamp=parse_date('2017-12-11T15:07:13Z'),
            call_id=call_2
        )
        CallLog.objects.create(
            type='end',
            timestamp=parse_date('2017-12-11T15:14:56Z'),
            call_id=call_2
        )
        # call 3
        call_3 = Call.objects.create(
            source="41987654321",
            destination="1196385274"
        )
        CallLog.objects.create(
            type='start',
            timestamp=parse_date('2017-12-12T22:47:56Z'),
            call_id=call_3
        )
        CallLog.objects.create(
            type='end',
            timestamp=parse_date('2017-12-12T22:50:56Z'),
            call_id=call_3
        )
        # call 4
        call_4 = Call.objects.create(
            source="41987654321",
            destination="1196385274"
        )
        CallLog.objects.create(
            type='start',
            timestamp=parse_date('2017-12-12T21:57:13Z'),
            call_id=call_4
        )
        CallLog.objects.create(
            type='end',
            timestamp=parse_date('2017-12-12T22:10:56Z'),
            call_id=call_4
        )

        # call 5
        call_5 = Call.objects.create(
            source="41987654321",
            destination="1196385274"
        )
        CallLog.objects.create(
            type='start',
            timestamp=parse_date('2017-12-12T04:57:13Z'),
            call_id=call_5
        )
        CallLog.objects.create(
            type='end',
            timestamp=parse_date('2017-12-12T06:10:56Z'),
            call_id=call_5
        )

        # call 6
        call_6 = Call.objects.create(
            source="1196385274",
            destination="41987654321"
        )
        CallLog.objects.create(
            type='start',
            timestamp=parse_date('2017-12-13T21:57:13Z'),
            call_id=call_6
        )
        CallLog.objects.create(
            type='end',
            timestamp=parse_date('2017-12-14T22:10:56Z'),
            call_id=call_6
        )

        # call 7
        call_7 = Call.objects.create(
            source="1196385274",
            destination="41987654321"
        )
        CallLog.objects.create(
            type='start',
            timestamp=parse_date('2017-12-12T15:07:58Z'),
            call_id=call_7
        )
        CallLog.objects.create(
            type='end',
            timestamp=parse_date('2017-12-12T15:12:56Z'),
            call_id=call_7
        )

        # call 8
        call_8 = Call.objects.create(
            source="1196385274",
            destination="41987654321"
        )
        CallLog.objects.create(
            type='start',
            timestamp=parse_date('2018-02-28T21:57:13Z'),
            call_id=call_8
        )
        CallLog.objects.create(
            type='end',
            timestamp=parse_date('2018-03-01T22:10:56Z'),
            call_id=call_8,
        )

    def test_call_models_object_count(self):
        calls = Call.objects.count()
        self.assertEqual(calls, 8)
        call_logs = CallLog.objects.count()
        self.assertEqual(call_logs, 16)
        call_invoices = CallInvoice.objects.count()
        # for each call terminated an invoice must be created
        self.assertEqual(call_invoices, 8)

    def test_should_return_attributes_call(self):
        fields_call = ('source', 'destination')
        for field in fields_call:
            with self.subTest():
                self.assertTrue(hasattr(Call, field))

    def test_should_return_attributes_call_log(self):
        fields_call_log = ('type', 'timestamp', 'call_id')
        for field in fields_call_log:
            with self.subTest():
                self.assertTrue(hasattr(CallLog, field))

    def test_should_return_attributes_call_invoice(self):
        fields_call_invoice = (
            'call_id', 'price', 'price_display', 'call_start_date',
            'call_start_time', 'destination', 'duration'
        )
        for field in fields_call_invoice:
            with self.subTest():
                self.assertTrue(hasattr(CallInvoice, field))
