from rest_framework.permissions import BasePermission


class IsRateAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_perm("pgi_currencies.add_rate")
        )
