from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from projects.models import Project, Issue
from projects.serializers import IssueDetailSerializer, CommentSerializer


class IsProjectContributor(permissions.BasePermission):

    def has_permission(self, request, view):
        project_id = None
        if view.action == 'list':
            return True
        if view.action in ['create', 'retrieve', 'update']:
            if view.get_serializer_class() == IssueDetailSerializer:
                project_id = request.data.get('project') or view.get_object().project_id
            elif view.get_serializer_class() == CommentSerializer:
                issue_id = request.data.get('issue') or view.get_object().issue_id
                project_id = Issue.objects.get(id=issue_id).project_id
            if project_id:
                project = get_object_or_404(Project, id=project_id)
                return project.contributors.filter(user=request.user).exists()
            return False

        return True


