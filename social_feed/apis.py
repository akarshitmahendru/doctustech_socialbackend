from rest_framework import generics, permissions, status, response, parsers, viewsets, exceptions, filters
from .models import UserImage, UserLikesAndComment
from .serializers import UserUploadImagesSerializer, UserLikeAndDislikeSerializer, UserImageDataGetSerializer, \
    UserCommentsSerializer, LikeDataSerializer, CommentsDataSerializer
from accounts.models import User


class UploadImageAPI(viewsets.ModelViewSet):
    model = UserImage
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserUploadImagesSerializer
        else:
            return UserImageDataGetSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id,
                "request": self.request
                }

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if self.request.method == 'GET' and not self.kwargs.get('pk'):
            if user_id:
                return self.model.objects.filter(user_id=user_id,
                                                 is_active=True)
            else:
                return self.model.objects.filter(user_id=self.request.user.id,
                                                 is_active=True)
        else:
            return self.model.objects.all()

    def list(self, request, *args, **kwargs):
        resp_dict = dict()
        user_id = request.query_params.get("user_id")
        if user_id:
            user = User.objects.filter(id=int(user_id)).first()
        else:
            user = User.objects.filter(id=self.request.user.id).first()
        resp_dict["user_details"] = dict()
        if user:
            resp_dict["user_details"]["full_name"] = user.get_full_name()
            resp_dict["user_details"]["profile_picture"] = user.avatar.url if user.avatar else None
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer_class()
            serializer = serializer(queryset, many=True, context=self.get_serializer_context())
            resp_dict["data"] = serializer.data
        else:
            resp_dict["data"] = dict()
        return response.Response(
            resp_dict,
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=self.request.user)
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLikeActionAPI(generics.ListCreateAPIView):
    model = UserLikesAndComment
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('liked_by__name', 'liked_by__last_name')

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserLikeAndDislikeSerializer
        else:
            return LikeDataSerializer

    def get_queryset(self):
        image_id = self.request.query_params.get("image_id")
        if image_id:
            return self.model.objects.filter(image_obj_id=image_id,
                                             type_of_action='like',
                                             like_status=True)
        else:
            raise exceptions.ValidationError(
                "image_id is required in query parameters"
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            image_id = serializer.validated_data["image_obj_id"]
            user = self.request.user
            image = UserImage.objects.filter(id=image_id).first()
            qs = self.model.objects.filter(image_obj_id=image_id,
                                           type_of_action='like',
                                           liked_by=user.id,
                                           like_status=True).first()
            if qs:
                qs.like_status = False
                qs.save()
            else:
                self.model.objects.create(
                    image_obj=image,
                    type_of_action='like',
                    liked_by=user
                )
            no_of_likes = self.model.objects.filter(image_obj_id=image_id,
                                                    type_of_action='like',
                                                    like_status=True).count()
            return response.Response(
                {"no_of_likes": no_of_likes},
                status=status.HTTP_201_CREATED
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserCommentsAPI(generics.ListCreateAPIView):
    serializer_class = UserCommentsSerializer
    model = UserLikesAndComment
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('commented_by__full_name',)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCommentsSerializer
        else:
            return CommentsDataSerializer

    def get_queryset(self):
        image_id = self.request.query_params.get("image_id")
        if image_id:
            return self.model.objects.filter(image_obj_id=image_id,
                                             type_of_action='comment')
        else:
            raise exceptions.ValidationError(
                "image_id is required in query parameters"
            )

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            image_id = serializer.validated_data.pop("image_obj_id")
            user = self.request.user
            image = UserImage.objects.filter(id=image_id).first()
            serializer.save(image_obj=image, type_of_action='comment', commented_by=user)
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
