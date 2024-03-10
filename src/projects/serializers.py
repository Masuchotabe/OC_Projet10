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
        fields = ['user', 'id']


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


class ContributorField(serializers.Field):
    def to_representation(self, obj):
        if obj:
            return obj.user.username

    def to_internal_value(self, data):
        if isinstance(data, str):
            if UserModel.objects.filter(username=data).exists():
                return Contributor.objects.get_or_create(user=UserModel.objects.get(username=data))[0]
            else:
                raise serializers.ValidationError(_('Contributor does not exist with this username'))
        elif isinstance(data, int):
            if Contributor.objects.filter(id=data).exists():
                return Contributor.objects.get(id=data)
            else:
                raise serializers.ValidationError(_('Contributor does not exist'))


class IssueDetailSerializer(serializers.ModelSerializer):
    comments = HyperlinkedRelatedField(many=True, read_only=True, view_name='comment-detail')
    contributor = ContributorField()

    class Meta:
        model = Issue
        fields = ['name', 'project', 'description', 'tag', 'priority', 'comments', 'contributor']
        extra_kwargs = {
            'author': {'read_only': True},
            'comments': {'read_only': True},
        }

    def is_valid(self, raise_exception=False):
        return super().is_valid(raise_exception=raise_exception)

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
