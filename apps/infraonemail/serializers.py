from rest_framework import serializers
from apps.infraonemail.models import *


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Communication
