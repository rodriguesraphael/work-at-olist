from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from calls.models import Call, CallLog, CallInvoice


class CallSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = Call
        fields = ['id', 'source', 'destination']
        validators = [
            UniqueTogetherValidator(
                queryset=Call.objects.all(),
                fields=['id'],
                message="The fields 'call_id' must make a unique set."
            )
        ]


class AbstractCallLogSerializer(serializers.Serializer):
    EVENT_TYPES = [
        ('start', '1 - Start'),
        ('end', '2 - End')
    ]
    type = serializers.ChoiceField(choices=EVENT_TYPES, default='start')
    timestamp = serializers.DateTimeField()
    call_id = serializers.IntegerField(
        required=True,
        allow_null=True,
        help_text="Unique for each call record pair"
    )
    source = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=11,
        help_text="The subscriber phone number that originated the call"
    )
    destination = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=11,
        help_text="The phone number receiving the call"
    )

    def validate(self, data):
        source = data.get('source', False)
        destination = data.get('destination', False)
        if data['type'] == 'end':
            msg = ''
            if source:
                msg += "The 'source' field should be entered only " \
                       "when the record 'type' is 'start'. "
            if destination:
                msg += "The 'destination' field should be entered only " \
                       "when the record 'type' is 'start'."
            if msg:
                raise serializers.ValidationError(msg)
        if data['type'] == 'start':
            msg = ''
            if not source:
                msg += "The 'source' field must be entered when the " \
                       "record 'type' is 'start'. "
            if not destination:
                msg += "The 'destination' field must be entered when the " \
                       "record 'type' is 'start'. "
            if msg:
                raise serializers.ValidationError(msg)
        return data


class CallLogSerializer(serializers.ModelSerializer):

    call_id = serializers.PrimaryKeyRelatedField(
        queryset=Call.objects.all(),
        required=True,
        allow_null=True,
        help_text="Unique for each call record pair"
    )
    source = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    class Meta:
        model = CallLog
        fields = [
            'id', 'source', 'destination', 'type', 'call_id', 'timestamp'
        ]

    def get_destination(self, obj):
        return obj.destination

    def get_source(self, obj):
        return obj.source

    def validate(self, data):
        if data.get('type') == 'end':
            try:
                log_start = CallLog.objects.get(
                    call_id=data.get('call_id'),
                    type='start'
                )
            except CallLog.DoesNotExist:
                msg = "There is no start record for this call, " \
                      "the end of a call cannot be logged before it starts."
                raise serializers.ValidationError(msg)
            if data.get('timestamp').replace(tzinfo=None) <= \
                    log_start.timestamp.replace(tzinfo=None):
                msg = "The call end time cannot be earlier or equal than " \
                      "the start time."
                raise serializers.ValidationError(msg)
        return data


class CallInvoiceSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    call_start_date = serializers.SerializerMethodField()
    call_start_time = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = CallInvoice
        fields = [
            'call_id', 'price', 'duration', 'call_start_date',
            'call_start_time', 'destination'
        ]

    def get_price(self, obj):
        return obj.price_display

    def get_duration(self, obj):
        return obj.duration

    def get_call_start_date(self, obj):
        return obj.call_start_date

    def get_call_start_time(self, obj):
        return obj.call_start_time

    def get_destination(self, obj):
        return obj.destination
