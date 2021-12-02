from django.contrib.auth import user_logged_in
from rest_framework import generics, response, status, permissions, filters, views
from . import serializers, models


class RegistrationAPI(generics.CreateAPIView):
    serializer_class = serializers.RegistrationSerializer
    model = models.User
    permission_classes = (
        permissions.AllowAny,
    )

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data.pop('confirm_password')
            user = self.model.objects.create_user(**serializer.validated_data)
            user.save()
            user.send_verification_email(request)
            response_dict = dict()
            response_dict['user_id'] = user.id
            return response.Response(response_dict, status=status.HTTP_200_OK)
        else:
            return response.Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(generics.CreateAPIView):
    serializer_class = serializers.VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_otp = serializer.user_otp
            user = user_otp.get_user()
            user.is_active = True
            user.save()
            models.UserOtp.objects.get_all_otp_of_user(user).delete()
            response_dict = dict()
            response_dict['auth_token'] = user.get_user_access_token()
            response_dict['user_id'] = user.id
            return response.Response(response_dict, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    """ Api for the user login """

    serializer_class = serializers.LoginSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request, *args, **kwargs):
        """
        login api
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.user  # take the user from serializer objects
            user_logged_in.send(
                sender=user.__class__, request=self.request, user=user)
            response_dict = dict()
            response_dict['auth_token'] = user.get_user_access_token()
            response_dict['user_id'] = user.id
            return response.Response(
                data=response_dict,
                status=status.HTTP_200_OK,
            )


class LogOutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user.get_user_access_token(revoke=True)
        return response.Response(
            {"msg": "You have been successfully logged out"},
            status=status.HTTP_200_OK
        )


class SearchUsersAPI(generics.ListAPIView):
    queryset = models.User.objects.filter(is_active=True)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserGetSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'last_name', 'email',)

