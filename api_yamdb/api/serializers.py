from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import PastOrPresentYearValidator
from users.validators import CustomUsernameValidator

from .constants import MAX_LENGTH_CHAR, MAX_LENGTH_MAIL
from .utils import send_confirmation_email

User = get_user_model()


class UserSignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(
        max_length=MAX_LENGTH_MAIL,
        required=True,
    )
    username = serializers.CharField(
        max_length=MAX_LENGTH_CHAR,
        required=True,
        validators=(CustomUsernameValidator(),),
    )

    class Meta:
        fields = ('username', 'email')

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')

        existing_user_by_email = User.objects.filter(email=email).first()
        existing_user_by_username = User.objects.filter(
            username=username
        ).first()

        if existing_user_by_email and (existing_user_by_email.username
                                       != username):
            raise serializers.ValidationError(
                {
                    'email': [
                        'User with this email already exists but with '
                        'a different username.'
                    ],
                    'username': []  # Пустой массив для username
                },
                code=status.HTTP_400_BAD_REQUEST
            )

        if existing_user_by_username and (existing_user_by_username.email
                                          != email):
            raise serializers.ValidationError(
                {
                    'username': [
                        'User with this username already exists but with '
                        'a different email.'
                    ],
                    'email': []  # Пустой массив для email
                },
                code=status.HTTP_400_BAD_REQUEST
            )

        user = (
            existing_user_by_email
            or existing_user_by_username
            or User.objects.create(
                email=email, username=username
            )
        )

        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()

        send_confirmation_email(email, confirmation_code)
        return user

    def validate(self, data):
        errors = {}
        username = data.get('username')
        email = data.get('email')

        if username:
            existing_user_by_username = User.objects.filter(
                username=username
            ).first()
            if existing_user_by_username and (existing_user_by_username.email
                                              != email):
                errors['username'] = [
                    'User with this username already exists but with '
                    'a different email.'
                ]

        if email:
            existing_user_by_email = User.objects.filter(
                email=email
            ).first()
            if existing_user_by_email and (existing_user_by_email.username
                                           != username):
                errors['email'] = [
                    'User with this email already exists but with '
                    'a different username.'
                ]

        if errors:
            raise ValidationError(errors)

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

        user = get_object_or_404(User, username=username)

        if user.confirmation_code != confirmation_code:
            confirmation_code = default_token_generator.make_token(user)
            user.confirmation_code = confirmation_code
            user.save()
            send_confirmation_email(user.email, confirmation_code)
            raise ValidationError('Неправильный код подтверждения')

        token = RefreshToken.for_user(user)
        return {'token': str(token.access_token)}


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользовательской модели."""

    username = serializers.CharField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
            CustomUsernameValidator()
        ),
        max_length=MAX_LENGTH_CHAR,
        required=True,
    )

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        max_length=MAX_LENGTH_MAIL,
        required=True,
    )

    class Meta:
        model = User
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

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date',
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


class TitleSerializerSafe(serializers.ModelSerializer):
    """Сериализатор для чтения информации о названии."""

    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleSerializerNonSafe(serializers.ModelSerializer):
    """Сериализатор для записи информации о названии."""

    year = serializers.IntegerField(
        validators=(PastOrPresentYearValidator(date.today().year),)
    )
    rating = serializers.IntegerField(
        default=None, allow_null=True, read_only=True
    )
    description = serializers.CharField(required=False)
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

    def validate_genre(self, value):
        """Проверка, что список жанров не пустой."""
        if not value:
            raise ValidationError("Список жанров не может быть пустым.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['genre'] = [
            {'name': genre.name, 'slug': genre.slug}
            for genre in instance.genre.all()
        ]
        representation['category'] = {
            'name': instance.category.name,
            'slug': instance.category.slug
        }
        return representation
