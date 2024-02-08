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
from projects.serializers import ProjectSerializer, IssueSerializer, CommentSerializer


# Create your views here.


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    # queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Project.objects.all()
        else:
            user = self.request.user
            return Project.objects.filter(Q(author=user) | Q(contributors__user=user))

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)

    @action(methods=['post'], detail=True)
    def add_contributor(self, request, pk=None):
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
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
