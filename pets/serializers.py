from rest_framework import serializers
from .models import CategorySex
from groups.serializers import GroupSerializer
from traits.serializers import TraitSerializer


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(
        choices = CategorySex.choices,
        default = CategorySex.NOT_INFORMED
    )
    group = GroupSerializer()
    traits = TraitSerializer(many=True)


class PetPutSerializer(PetSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False