import re

from django.contrib.auth.tokens import default_token_generator
from django.core.validators import RegexValidator
from django.db.models import Avg
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import CustomUser

from .constants import MAX_LENGTH_CHAR, MAX_LENGTH_MAIL, USERNAME_REGEX
from .utils import send_code_to_mail


class UserRegistrationSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(
        max_length=MAX_LENGTH_MAIL,
        required=True,
    )

    username = serializers.CharField(
        max_length=MAX_LENGTH_CHAR,
        required=True,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX,
                message='Имя пользователя может содержать '
                        'только буквы, цифры и следующие символы: '
                        '@/./+/-/_',
            ),
        ],
    )

    class Meta:
        fields = ('username', 'email')

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']

        existing_user_by_email = CustomUser.objects.filter(email=email).first()

        if existing_user_by_email:
            if existing_user_by_email.username != username:
                raise serializers.ValidationError(
                    {'error': 'User with this email already exists '
                              'but with a different username.'},
                    code=status.HTTP_400_BAD_REQUEST
                )
            return existing_user_by_email

        existing_user_by_username = CustomUser.objects.filter(
            username=username
        ).first()

        if existing_user_by_username:
            if existing_user_by_username.email != email:
                raise serializers.ValidationError(
                    {'error': 'User with this username already exists '
                              'but with a different email.'},
                    code=status.HTTP_400_BAD_REQUEST
                )
            return existing_user_by_username

        if existing_user_by_email and existing_user_by_username:
            raise serializers.ValidationError(
                {'error': 'User with this email and username '
                          'already exists .'},
                code=status.HTTP_400_BAD_REQUEST
            )

        user = CustomUser.objects.create(email=email, username=username)
        confirmation_code = default_token_generator.make_token(user)
        send_code_to_mail(email, confirmation_code)
        return user

    def validate(self, data):
        username = data.get('username')

        if username:
            if username == 'me' or not re.match(USERNAME_REGEX, username):
                raise ValidationError('<me> can not be a username')
        return data


class CustomTokenObtainSerializer(TokenObtainSerializer):
    """Сериализатор для получения пользовательского токена."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields['confirmation_code'] = serializers.CharField()
        self.fields.pop('password', None)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        if not username:
            raise serializers.ValidationError(
                {'username': 'Имя пользователя обязательно.'})
        user = CustomUser.objects.filter(
            username=attrs[self.username_field],
        ).first()
        if not user:
            raise NotFound({'detail': 'Пользователь не найден.'})
        if not confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Код подтверждения обязателен.'})
        if str(user.confirmation_code) != attrs['confirmation_code']:
            raise ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'},
                code='invalid_confirmation_code',
            )
        self.user = user
        user.save()
        return {'token': str(self.get_token(self.user).access_token)}


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользовательской модели."""

    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all()),
            RegexValidator(regex=USERNAME_REGEX)
        ],
        max_length=MAX_LENGTH_CHAR,
        required=True,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        max_length=MAX_LENGTH_MAIL,
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date', 'review', 'title'
        )


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            review = Review.objects.filter(
                title=self.context['view'].kwargs.get('title_id'),
                author=self.context['request'].user
            )
            if review.exists():
                raise serializers.ValidationError(
                    'Ваш отзыв на это произведение уже опубликован'
                )
        return data


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения информации о названии."""

    rating = serializers.SerializerMethodField()
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        return obj.reviews.aggregate(Avg('score', default=0)).get('score__avg')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи информации о названии."""

    rating = serializers.IntegerField(read_only=True)
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
    )
    category = serializers.SlugRelatedField(
        many=False,
        queryset=Category.objects.all(),
        slug_field='slug',
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
