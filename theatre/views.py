from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    extend_schema_view
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayImageSerializer,
    PlayDetailSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationSerializer,
    ReservationListSerializer,
    TheatreHallSerializer,
)

from theatre.models import (
    Genre,
    Actor,
    Play,
    Performance,
    Reservation,
    TheatreHall,
)


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    @extend_schema(
        summary="Get a list of genres",
        description="Returns a list of all genres available in the database.",
        responses={200: GenreSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new genre",
        description="Creates a new genre by accepting JSON with parameters.",
        request=GenreSerializer,
        responses={201: GenreSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

    @extend_schema(
        summary="Get the cast list",
        description="Returns a list of all actors.",
        responses={200: ActorSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new actor",
        description="Creates a new actor. Requires JSON with parameters.",
        request=ActorSerializer,
        responses={201: ActorSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer

    @extend_schema(
        summary="Get a list of theatre venues",
        description="Returns a list of all theatre halls.",
        responses={200: TheatreHallSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new theatre room",
        description="Creates a new room by accepting JSON with parameters.",
        request=TheatreHallSerializer,
        responses={201: TheatreHallSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema_view(
    retrieve=extend_schema(
        summary="Get a play by id",
        description="Get information about a specific play by ID."
    ),
    update=extend_schema(
        summary="Update a play by id",
        description="Update information about a specific play by ID."
    ),
    partial_update=extend_schema(
        summary="Partial update a play by id",
        description="Partially update information about a "
                    "particular play by ID."
    ),
)
class PlayViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Play.objects.prefetch_related("genres", "actors")
    serializer_class = PlaySerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the movies with filters"""
        title = self.request.query_params.get("title")
        genres = self.request.query_params.get("genres")
        actors = self.request.query_params.get("actors")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if genres:
            genres_ids = self._params_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genres_ids)

        if actors:
            actors_ids = self._params_to_ints(actors)
            queryset = queryset.filter(actors__id__in=actors_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        if self.action == "upload_image":
            return PlayImageSerializer

        return PlaySerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    @extend_schema(
        summary="Upload an image for a specific play",
        description=(
                "This endpoint allows administrators to upload "
                "an image for a specific play. "
                "The `id` in the URL corresponds to the play ID."
        ),
        request=PlayImageSerializer,
        responses={200: PlayImageSerializer},
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific play"""
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get a list of plays",
        description="Returns a list of plays that can be filtered by "
                    "parameters: actors (id), genres (id), title (string).",
        request=PlaySerializer,
        responses={201: PlaySerializer},
        parameters=[
            OpenApiParameter(
                name="actors",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by actor id (ex. ?actors=2,3)",
            ),
            OpenApiParameter(
                name="genres",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by genre id (ex. ?genres=2,3)",
            ),
            OpenApiParameter(
                name="title",
                type={"type": "string"},
                description="Filtering by part of the title or full title "
                            "(ex. ?title=Inc)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new play",
        description="A play is created by passing the parameters: "
                    "title, description, genres, actors and image link.",
        request=PlaySerializer,
        responses={201: PlaySerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema_view(
    retrieve=extend_schema(
        summary="Get a performance by id",
        description="Get information about a specific performance by ID."
    ),
    update=extend_schema(
        summary="Update a performance by id",
        description="Update information about a specific performance by ID."
    ),
    partial_update=extend_schema(
        summary="Partial update a performance by id",
        description="Partially update information about a "
                    "particular performance by ID."
    ),
    destroy=extend_schema(
        summary="Delete a performance by id",
        description="Delete a performance by ID."
    )
)
class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = (
        Performance.objects.all()
        .select_related("play", "theatre_hall")
        .annotate(
            tickets_available=(
                F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )
        )
    )
    serializer_class = PerformanceListSerializer

    def get_queryset(self):
        date = self.request.query_params.get("date")
        play_id_str = self.request.query_params.get("play")

        queryset = self.queryset


        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        if play_id_str:
            queryset = queryset.filter(play_id=int(play_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        if self.action == "retrieve":
            return PerformanceDetailSerializer

        return PerformanceSerializer

    @extend_schema(
        summary="Get a list of performances",
        description="Returns a list of performances filtered by play "
                    "and data parameters.",
        request=PerformanceSerializer,
        responses={201: PerformanceSerializer},
        parameters=[
            OpenApiParameter(
                name="play",
                type={"type": "number"},
                description="Filter by play id (ex. ?play=2)",
            ),
            OpenApiParameter(
                name="date",
                type={"type": "string", "format": "date"},
                description="Filter by date in '%Y-%m-%d' format "
                            "(ex. ?date=2019-02-01)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new performance",
        description="A performance is created by passing the parameters: "
                    "show time, play and theatre hall.",
        request=PerformanceSerializer,
        responses={201: PerformanceSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__play", "tickets__performance__theatre_hall"
    )
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationSerializer

        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Get a list of reservations",
        description="Returns a list of all reservations belonging to "
                    "the current user.",
        responses={200: ReservationListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new reservation",
        description="Allows the user to create a new reservation. "
                    "JSON with reservation data is required.",
        request=ReservationSerializer,
        responses={201: ReservationSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
