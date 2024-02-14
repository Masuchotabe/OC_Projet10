from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext as _

from projects.models import Project, Issue, Comment, Contributor

UserModel = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {
            'contributors': {'read_only': True},
            'author': {'read_only': True},
        }

    def validate_name(self, value):
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError(_('Project with this name already exist'))
        return value

    def create(self, validated_data):
        project = super().create(validated_data)
        user = validated_data.get('author')
        project.add_contributor(user)
        return project


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'
        extra_kwargs = {
            'author': {'read_only': True},
        }

    def validate(self, data):
        project = data.get('project')
        contributor = data.get('contributor')

        if contributor and not project.contributors.filter(id=contributor.id).exists():
            raise serializers.ValidationError(_('This contributor is not contributing to this project.'))

        return data

    def create(self, validated_data):
        if validated_data.get('contributor') is None:
            validated_data['contributor'] = Contributor.objects.get_or_create(user=validated_data['author'])[0]
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
