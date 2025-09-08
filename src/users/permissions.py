from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешаем доступ пользователю с ролью администратора."""

    def has_permission(self, request, view):
        return request.user.role == 'admin'


class IsStaff(permissions.BasePermission):
    """Разрешаем доступ только персоналу"""

    def has_permission(self, request, view):
        return request.user.is_staff


class IsStaffOrSelf(permissions.BasePermission):
    """Разрешаем доступ только персоналу или пользователю, запрашивающему свои данные"""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj


class IsOwner(permissions.BasePermission):
    """Разрешаем доступ владельцу объекта."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
