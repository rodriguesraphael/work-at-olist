from datetime import timedelta
from calls.validators import validate_phone_number
from django.core.validators import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Call(models.Model):
    source = models.CharField(
        max_length=11,
        validators=[validate_phone_number],
        help_text="The subscriber phone number that originated the call"
    )
    destination = models.CharField(
        max_length=11,
        validators=[validate_phone_number],
        help_text="The phone number receiving the call"
    )

    def save(self, *args, **kwargs):
        if self.destination == self.source:
            msg = 'Source and destination cannot contain the same value.'
            raise ValidationError(msg)
        super(Call, self).save(*args, **kwargs)


class CallLog(models.Model):
    EVENT_TYPES = (
        ('start', '1 - Start'),
        ('end', '2 - End')
    )

    type = models.CharField(
        choices=EVENT_TYPES,
        max_length=5,
        help_text="Indicate if it's a call 'start' or 'end' record"
    )
    timestamp = models.DateTimeField(
        help_text="The timestamp of when the event occurred"
    )
    call_id = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name='logs',
        help_text="Unique for each call record pair"
    )

    class Meta:
        unique_together = (('type', 'call_id'),)

    def __str__(self):
        if self.type == 'start':
            return "started at {timestamp}".format(timestamp=self.timestamp)
        elif self.type == 'end':
            return "ended at {timestamp}".format(timestamp=self.timestamp)

    def save(self, *args, **kwargs):
        if self.type == 'end':
            try:
                log_start = CallLog.objects.get(
                    call_id=self.call_id, type='start')
            except CallLog.DoesNotExist:
                msg = "There is no start record for this call, " \
                      "the end of a call cannot be logged before it starts."
                raise ValidationError(msg)
            if self.timestamp.replace(tzinfo=None) <= \
                    log_start.timestamp.replace(tzinfo=None):
                msg = "The call end time cannot be earlier or equal than " \
                      "the start time."
                raise ValidationError(_(msg))

        super(CallLog, self).save(*args, **kwargs)

    @property
    def destination(self):
        return self.call_id.destination

    @property
    def source(self):
        return self.call_id.source


class CallInvoice(models.Model):
    REDUCED_START = 22
    REDUCED_END = 6
    MINUTE_PRICE = 0.09
    STANDING_PRICE = 0.36

    call_id = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name="invoice"
    )
    timestamp_end = models.DateField(
        null=True
    )
    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True
    )

    class Meta:
        unique_together = ('call_id',)

    def save(self, *args, **kwargs):
        try:
            CallLog.objects.filter(call_id=self.call_id, type='end').get()
        except CallLog.DoesNotExist:
            msg = "You cannot create an invoice for a call without an end " \
                  "registration."
            raise ValidationError(msg)
        log_start = self.call_id.logs.get(type='start')
        log_end = self.call_id.logs.get(type='end')
        self.timestamp_end = log_end.timestamp
        self.price = self.compute_time_billing(
            self.STANDING_PRICE, log_start.timestamp, log_end.timestamp)
        super(CallInvoice, self).save(*args, **kwargs)

    @property
    def price_display(self):
        return "R$ %s" % self.price

    @property
    def call_start_date(self):
        if self.call_id.logs.filter(type='start').exists():
            log_start = self.call_id.logs.get(type='start')
            return log_start.timestamp.date()

    @property
    def call_start_time(self):
        if self.call_id.logs.filter(type='start').exists():
            log_start = self.call_id.logs.get(type='start')
            return log_start.timestamp.time()

    @property
    def started_at(self):
        if self.call_id.logs.filter(type='start').exists():
            log_start = self.call_id.logs.get(type='start')
            return log_start.timestamp

    @property
    def ended_at(self):
        if self.call_id.logs.filter(type='end').exists():
            log_end = self.call_id.logs.get(type='end')
            return log_end.timestamp

    @property
    def destination(self):
        return self.call_id.destination

    @property
    def duration(self):
        duration = self.ended_at - self.started_at
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        seconds += duration.microseconds / 1e6
        seconds = int(seconds)
        if days:
            hours += days * 24
        return "{}h{}m{}s".format(hours, minutes, seconds)

    def compute_time_billing(
            self, start_price, start_timestamp, end_timestamp):
        """
        :param start_price: starting price of the calculation
        :param start_timestamp: start date of calculation
        :param end_timestamp: end date of calculation
        :return: price
        """
        def reduced_fare_range(start_reduced, end_reduced, timestamp):
            # check if the past date is within the uncharged range
            if timestamp.hour >= start_reduced or timestamp.hour < end_reduced:
                return True

        def replace_date_to_normal_range(end_reduced, timestamp):
            # replace the date to normal billing time
            next_day = timestamp + timedelta(days=1)
            new_timestamp = timestamp.replace(
                day=next_day.day, month=next_day.month,
                hour=end_reduced, minute=0, second=0, microsecond=0
            )
            return new_timestamp

        def get_time_charged(start_reduced, timestamp):
            # calculates the time charged when the end of the call is
            # more than 22 hours of the call start day
            start_fare_range = timestamp.replace(
                hour=start_reduced, minute=0, second=0, microsecond=0)
            time_charged = int(
                (start_fare_range - timestamp).total_seconds() / 60)
            return time_charged

        reduced_start = self.REDUCED_START
        reduced_end = self.REDUCED_END
        start_timestamp = start_timestamp.replace(tzinfo=None)
        end_timestamp = end_timestamp.replace(tzinfo=None)
        price = start_price
        next_start_date = replace_date_to_normal_range(
            reduced_end, start_timestamp)
        if reduced_fare_range(reduced_start, reduced_end, start_timestamp):
            # check if the start date is at non-charged times
            if end_timestamp < next_start_date:
                # if the end date is also non-billing, no minutes are charged
                # and the starting price must be returned
                return price
            else:
                # If the call end date is greater than the no charge time, the
                # start date should be replaced with the next date and time in
                # the normal charge range and the method called
                # using recursion.
                price = self.compute_time_billing(
                    price, next_start_date, end_timestamp)
        elif reduced_fare_range(reduced_start, reduced_end, end_timestamp):
            # if the start date and time are not at no charge
            # times but the call end date and time are within the no
            # charge range
            minutes_normal = get_time_charged(reduced_start, start_timestamp)
            price += minutes_normal * self.MINUTE_PRICE
            if next_start_date > end_timestamp:
                # if the call end date and time is less than the next charge
                # start date and time, the calculated price must be returned
                return price
            price = self.compute_time_billing(
                price, next_start_date, end_timestamp)
        elif end_timestamp > next_start_date:
            # tests if the call end date and time are longer than the next
            # charged date and time
            minutes_bill = get_time_charged(reduced_start, start_timestamp)
            price += minutes_bill * self.MINUTE_PRICE
            price = self.compute_time_billing(
                price, next_start_date, end_timestamp)
        # elif start_timestamp.day == end_timestamp.day:
        else:
            # otherwise it is understood that the call occurred
            # entirely on the same day and at normal billing time.
            minutes_normal = int(
                (end_timestamp - start_timestamp).total_seconds() / 60)
            price += (minutes_normal * self.MINUTE_PRICE)
        return price
