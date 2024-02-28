from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Пользовательское разрешение,
    позволяющее все действия Администраторам.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorAdminModeratorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_moderator
            or request.user.is_admin
            or obj.author == request.user
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Пользовательское разрешение,
    позволяющее редактировать объект администраторам и
    смотреть всем.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (
                request.user.is_admin
            )
        )
