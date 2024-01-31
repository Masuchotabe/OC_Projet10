from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        if view.action == 'list':
            return request.user.is_admin

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if not request.user.is_authenticated:
            return False

        return obj == request.user or request.user.is_admin
