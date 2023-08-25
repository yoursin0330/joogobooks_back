from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import generics, filters

from .models import Book
from .serializers import BookSerializer

# Create your views here.
class IsBookAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        book = view.get_object()
        return request.user == book.user
    

class BookListView(APIView):
    
    def get(self, request):
        booklist = Book.objects.all()
        serializer = BookSerializer(booklist, many=True)
        return Response(serializer.data)

    
class BookCreateView(APIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user = request.user)
            # serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)


class BookUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBookAuthor]

    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            if request.user == book.user:
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class BookSearchView(generics.ListAPIView):
    queryset = Book.objects.all().order_by('uploaded_at')
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author', 'detail_info']
