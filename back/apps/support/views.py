from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import SupportTicket, ChatMessage
from .serializers import SupportTicketSerializer, ChatMessageSerializer
import requests
import json

class SupportTicketCreateView(generics.CreateAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AdminTicketListView(generics.ListAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.select_related('user', 'order').prefetch_related('images').order_by('-created_at')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_assistant(request):
    user_message = request.data.get('message')
    session_id = request.data.get('session_id') # Optional, for future use

    if not user_message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Save user message
    ChatMessage.objects.create(
        user=request.user, 
        message=user_message, 
        is_from_user=True,
        session_id=session_id
    )

    # OpenAI interaction
    if not settings.OPENAI_API_KEY:
        return Response({'error': 'OpenAI API key not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Construct conversation history (last 5 messages for context)
    # This is a basic implementation. For production, you might want to summarize or limit tokens more strictly.
    previous_messages = ChatMessage.objects.filter(user=request.user, session_id=session_id).order_by('-timestamp')[:10]
    messages_payload = [{"role": "system", "content": "You are a helpful customer support assistant for YuanCity."}]
    
    # Add history in reverse order (oldest first)
    for msg in reversed(previous_messages):
        role = "user" if msg.is_from_user else "assistant"
        messages_payload.append({"role": role, "content": msg.message})

    # Ensure the current message is definitely in the payload if not saved/retrieved yet (it is saved above but race conditions etc)
    # Actually since we query DB above, it should include the latest message.
    # But just in case we missed it due to DB lag (unlikely in atomic request but still), 
    # the 'previous_messages' query includes the one we just created.
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages_payload,
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        ai_message = result['choices'][0]['message']['content']

        # Save AI response
        ChatMessage.objects.create(
            user=request.user, 
            message=ai_message, 
            is_from_user=False,
            session_id=session_id
        )

        return Response({'response': ai_message})

    except requests.exceptions.RequestException as e:
        # Log error
        print(f"OpenAI API Error: {e}")
        return Response({'error': 'Error communicating with AI service'}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        print(f"Error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)
