from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext as _

from utils import calculate_age

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'password', 'password2', 'birth_date', 'can_be_contacted', 'can_data_be_shared']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        """
        Création du user dans la base ( permet de gérer le hash du mot de passe via django)
        """
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            birth_date=validated_data['birth_date'],
            can_be_contacted=validated_data['can_be_contacted'],
            can_data_be_shared=validated_data['can_data_be_shared'],
        )
        return user

    def update(self, instance, validated_data={}):
        """Gestion de la mise à jour du password utilisateur"""
        instance = super().update(instance, validated_data)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
            instance.save()
        return instance

    def validate_birth_date(self, value):
        """Validation de la date de naissance, l'utilisateur doit avoir plus de 15 ans pour s'inscrire."""
        if calculate_age(value) < 15:
            raise serializers.ValidationError(_("User must be at least 15 years old to proceed."))
        return value

    def validate(self, attrs):
        """Validation du password."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


