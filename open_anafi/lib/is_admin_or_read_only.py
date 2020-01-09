from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Blocks POST and DELETE methods to non admin users
    """
    authorized_method = ['POST', 'DELETE', 'UPDATE', 'PUT']
    def has_permission(self, request, view):
        if request.method in self.authorized_method and request.user.is_staff == False:
            return False
        return True