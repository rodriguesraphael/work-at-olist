import datetime
from django.db.models import Q
from calls.serializers import \
    CallLogSerializer, CallInvoiceSerializer, \
    CallSerializer, AbstractCallLogSerializer
from calls.models import CallInvoice
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status


class CallLogViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = AbstractCallLogSerializer

    def create(self, request, *args, **kwargs):
        abstract_serializer = AbstractCallLogSerializer(data=request.data)
        if not abstract_serializer.is_valid():
            return Response(
                abstract_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.data.get('type') == 'start':
            call_data = {
                'id': request.data.get('call_id'),
                'source': request.data.get('source'),
                'destination': request.data.get('destination')
            }
            call_serializer = CallSerializer(data=call_data)
            if not call_serializer.is_valid():
                return Response(
                    call_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            call_serializer.save()
        serializer = CallLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CallInvoiceViewSet(viewsets.ViewSet, viewsets.GenericViewSet):
    queryset = CallInvoice.objects.all()
    serializer_class = CallInvoiceSerializer
    lookup_field = 'source'

    def retrieve(self, request, source=None):
        date = self.request.GET.get('date', None)
        today = datetime.date.today()
        first_day = today.replace(day=1)
        if source is None:
            msg = "You need to enter the calling phone number"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        if date is None:
            date_ref = first_day - datetime.timedelta(days=1)
        else:
            date_ref = datetime.datetime.strptime(date, '%m%Y')
            if date_ref.date() >= first_day:
                msg = "You cannot request an invoice for a " \
                      "month that is not yet completed."
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        call_invoices = CallInvoice.objects.filter(
            Q(call_id__source=source),
            Q(timestamp_end__year=date_ref.year),
            Q(timestamp_end__month=date_ref.month)
        )
        ctx = {'request': request}
        serializer = CallInvoiceSerializer(
            call_invoices, context=ctx, many=True)
        if serializer.data:
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
