from rest_framework import serializers
from .models import Martyr, MartyrMemory

class MartyrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Martyr
        fields = '__all__'



class MartyrMemorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = MartyrMemory
        fields = "__all__"
        read_only_fields = ["user", "martyr", "created_at"]
