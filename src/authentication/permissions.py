from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """ Permission liée à la lecture ou modification d'un USER.
    Seul un admin ou l'utilisateur lui meme peut modifier, lire ou supprimer l'objet
    La création ne nécessite pas de connexion.
    Seuls les admins peuvent lister les utilisateurs.
    """

    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        if view.action == 'list':
            return request.user.is_staff

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if not request.user.is_authenticated:
            return False

        return obj == request.user or request.user.is_staff
