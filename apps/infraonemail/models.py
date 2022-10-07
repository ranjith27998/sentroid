from django.db import models
from datetime import datetime


class Communication(models.Model):
    id = models.AutoField(primary_key=True)
    sent_time = models.DateTimeField(null=True, default=datetime.now)
    creation_time = models.DateTimeField(null=True, default=datetime.now)
    is_deleted = models.BooleanField(default=False)
    subject = models.CharField(max_length=250, blank=True)
    to_address = models.TextField()
    cc_address = models.TextField(null=True, blank=True)
    bcc_address = models.TextField(null=True, blank=True)
    from_address = models.EmailField(max_length=250)
    content = models.TextField(null=True, blank=True)
    txt_content = models.TextField(null=True, blank=True)
    is_attachment = models.BooleanField(default=False)
    status = models.IntegerField()  # 1 for delivered 2 for not delivered
    conversations_flag = models.SmallIntegerField()  # 1: Sent, 2: Received
    is_system_gen = models.BooleanField(default=False)
    sentiment_type = models.IntegerField()

    class Meta:
        db_table = 'tbl_communication'
