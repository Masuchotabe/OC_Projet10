from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from authentication.models import User
from authentication.serializers import UserSerializer
from authentication.permissions import UserPermission
from projects.models import Project, Issue, Comment
from projects.permissions import IsProjectContributor
from projects.serializers import ProjectListSerializer, ProjectDetailSerializer, IssueListSerializer, \
    IssueDetailSerializer, CommentSerializer


class ProjectViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]
    filterset_fields = ('type', 'name')

    def get_queryset(self):
        """
        Filtre les projets en fonction
        """
        if self.request.user.is_staff:
            projects = Project.objects.all()
        else:
            user = self.request.user
            projects = Project.objects.filter(Q(author=user) | Q(contributors__user=user))
        return projects.prefetch_related('contributors__user', 'author', 'issues')

    def get_serializer_class(self):
        """Retourne le serializer en fonction de l'action"""
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        """Permet d'ajouter le user connecté comme auteur lors de la création"""
        serializer.save(author=self.request.user)

    @action(methods=['post'], detail=True)
    def add_contributor(self, request, pk=None):
        """Route permettant l'ajout d'un contributeur sur un projet"""
        project = self.get_object()
        username = request.data.get('username')

        if username:
            user = get_object_or_404(User, username=username)
            project.add_contributor(user)
            serializer = self.get_serializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    permission_classes = [IsAuthenticated, IsProjectContributor]
    filterset_fields = ('tag', 'name', 'priority', 'project')

    def perform_create(self, serializer):
        """Permet d'ajouter le user connecté comme auteur lors de la création"""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Retourne le serializer en fonction de l'action"""
        if self.action == 'list':
            return IssueListSerializer
        return IssueDetailSerializer


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated, IsProjectContributor]

    def perform_create(self, serializer):
        """Permet d'ajouter le user connecté comme auteur lors de la création"""
        serializer.save(author=self.request.user)
