from rest_framework import serializers
from .models import Martyr

class MartyrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Martyr
        fields = '__all__'
