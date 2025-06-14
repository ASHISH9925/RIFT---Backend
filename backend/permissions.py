from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class RoleBasedAccessPermission(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '').split()
        if not auth_header or auth_header[0].lower() != 'bearer':
            return False

        if len(auth_header) == 1 or len(auth_header) > 2:
            return False

        token = auth_header[1]

        try:
            access_token = AccessToken(token)
            role = access_token.get('role', None)
            if not role:
                return False
            
            if role == 'user' and request.method == 'GET':
                return True
            elif role == 'agent' and request.method in ['POST','PATCH','UPDATE','DELETE']:
                return True
            else:
                return False
        except (InvalidToken, TokenError) as e:
            print(f"Token Error: {e}")  # Debug: Log the error
            return False
        

class FirstAgentPermission(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '').split()
        if not auth_header or auth_header[0].lower() != 'bearer':
            # If no token is provided, allow POST access (unregistered user)
            return request.method in ['POST','PATCH','UPDATE']

        if len(auth_header) == 1 or len(auth_header) > 2:
            return False

        token = auth_header[1]

        try:
            access_token = AccessToken(token)
            role = access_token.get('role', None)
            if not role:
                return False
            
            if role == 'user' and request.method == 'GET':
                return True
            elif not role and request.method in ['POST','PATCH','UPDATE']:  # Unregistered user
                return True
            else:
                return False
        except (InvalidToken, TokenError) as e:
            print(f"Token Error: {e}")  # Debug: Log the error
            return False