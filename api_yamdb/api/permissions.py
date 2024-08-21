from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только для администратора"""

    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return (
                request.user.is_superuser
                or request.user.is_admin
            )
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """Чтения доступно только администратору"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_admin
        )


class IsAuthorModeratorAdmin(permissions.BasePermission):
    """Разрешения для авторов, модераторов и администраторов"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                obj.author == request.user
                or request.user.is_superuser
                or request.user.is_admin
                or request.user.is_moderator
            )
        return request.method in permissions.SAFE_METHODS
