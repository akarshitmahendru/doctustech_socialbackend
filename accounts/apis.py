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


class UserInfo(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        return serializers.UserGetSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        return response.Response({"msg": "Your Account has been successfully closed"})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data,
                                instance=instance,
                                partial=partial,
                                )

        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class SearchUsersAPI(generics.ListAPIView):
    queryset = models.User.objects.filter(is_active=True)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserGetSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'last_name', 'email',)


class InvitationAPI(generics.CreateAPIView):
    model = models.FriendRequests
    serializer_class = serializers.InvitationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            source = self.request.user
            target = models.User.objects.filter(id=serializer.validated_data.pop("target_id")).first()
            serializer.save(source=source, target=target)
            return response.Response({"msg": "Friend request successfully sent"},
                                     status=status.HTTP_200_OK
                                     )

        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class MyFriendRequests(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = models.FriendRequests

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.InvitationActionSerializer
        else:
            return serializers.MyFriendRequestsSerializer

    def get_queryset(self):
        user = self.request.user
        return self.model.objects.filter(target=user, status="sent").order_by("-requested_date", "-id")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            action = serializer.validated_data.pop("action")
            obj = self.model.objects.filter(id=serializer.validated_data.pop("invitation_id")).first()
            if action == "accept":
                obj.source.friends.add(obj.target)
                obj.target.friends.add(obj.source)
                obj.source.save()
                obj.target.save()
                obj.status = "accepted"
                obj.save()
            else:
                obj.status = "rejected"
                obj.save()
            return response.Response({"msg": "Action successfully taken on friend request."},
                                     status=status.HTTP_200_OK
                                     )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


