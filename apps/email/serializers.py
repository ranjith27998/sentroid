from rest_framework import serializers
from apps.email.models import *


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Communication
