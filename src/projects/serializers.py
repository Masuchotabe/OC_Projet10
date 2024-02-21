from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext as _
from rest_framework.relations import HyperlinkedRelatedField

from projects.models import Project, Issue, Comment, Contributor

UserModel = get_user_model()


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Ou serializers.PrimaryKeyRelatedField() selon vos besoins

    class Meta:
        model = Contributor
        fields = ['user']


class ProjectListSerializer(serializers.ModelSerializer):
    contributors = ContributorSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()
    issues = HyperlinkedRelatedField(view_name='issue-detail', many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "author", "contributors", "type"]
        extra_kwargs = {
            'contributors': {'read_only': True},
            'author': {'read_only': True},
        }
        depth = 1

class ProjectSerializer(serializers.ModelSerializer):
    contributors = ContributorSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()
    issues = HyperlinkedRelatedField(view_name='issue-detail', many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "author", "contributors", "type", "issues"]
        extra_kwargs = {
            'contributors': {'read_only': True},
            'author': {'read_only': True},
        }
        depth = 1

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
