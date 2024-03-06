from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext as _
from rest_framework.relations import HyperlinkedRelatedField, HyperlinkedIdentityField

from projects.models import Project, Issue, Comment, Contributor

UserModel = get_user_model()


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Contributor
        fields = ['user']


class ProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ["id", "name", "description", "type"]
        depth = 1


class ProjectDetailSerializer(serializers.ModelSerializer):
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
        """Interdiction d'avoir 2 project avec le même nom."""
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError(_('Project with this name already exist'))
        return value

    def create(self, validated_data):
        project = super().create(validated_data)
        user = validated_data.get('author')
        project.add_contributor(user)
        return project


class IssueListSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='issue-detail')

    class Meta:
        model = Issue
        fields = ['name', 'project', 'priority', 'tag', 'url']


class IssueDetailSerializer(serializers.ModelSerializer):
    comments = HyperlinkedRelatedField(many=True, read_only=True, view_name='comment-detail')

    class Meta:
        model = Issue
        fields = '__all__'
        extra_kwargs = {
            'author': {'read_only': True},
        }

    def validate(self, data):
        """Validation du contributeur attribué à l'issue. Il doit être contributeur du projet."""
        project = data.get('project')
        contributor = data.get('contributor')

        if contributor and not project.contributors.filter(id=contributor.id).exists():
            raise serializers.ValidationError(_('This contributor is not contributing to this project.'))

        return data

    def create(self, validated_data):
        """
        Création de l'issue. S'il n'y a pas de contributeur associé,
        on associe automatiquement l'auteur comme contributeur.
        """
        if validated_data.get('contributor') is None:
            validated_data['contributor'] = Contributor.objects.get_or_create(user=validated_data['author'])[0]
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {
            'author': {'read_only': True},
        }
