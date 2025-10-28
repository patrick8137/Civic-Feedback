from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from .models import Feedback
import logging
import os

def analyzeSentiment(text):
    """Simple rule-based sentiment analysis"""
    positive_words = ['good', 'great', 'excellent', 'thank', 'beautiful', 'nice', 'love', 'appreciate', 'wonderful']
    negative_words = ['bad', 'poor', 'terrible', 'issue', 'problem', 'broken', 'damage', 'urgent', 'danger', 'not working']
    
    text = text.lower()
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    if positive_count > negative_count:
        return 'Positive'
    elif negative_count > positive_count:
        return 'Negative'
    return 'Neutral'

logger = logging.getLogger(__name__)

@api_view(['POST'])
def submit_feedback(request):
    try:
        logger.debug(f"Received feedback data: {request.data}")
        
        # Validate required fields
        required_fields = ['category', 'description']
        for field in required_fields:
            if not request.data.get(field):
                return Response(
                    {'success': False, 'message': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        feedback = Feedback.objects.create(
            user_type=request.data.get('user_type', 'citizen'),
            category=request.data.get('category'),
            description=request.data.get('description'),
            location=request.data.get('location', ''),
            status='pending'
        )
        logger.info(f"Created feedback with ID: {feedback.id}")
        return Response(
            {'success': True, 'message': 'Feedback submitted!'},
            status=status.HTTP_201_CREATED
        )
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return Response(
            {'success': False, 'message': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return Response(
            {'success': False, 'message': 'Error submitting feedback'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_feedback(request):
    try:
        logger.info("Fetching all feedback")
        feedback_list = Feedback.objects.all().order_by('-created_at')
        logger.info(f"Found {len(feedback_list)} feedback items")
        
        data = []
        for fb in feedback_list:
            try:
                feedback_item = {
                    'id': fb.id,
                    'user_type': fb.user_type,
                    'category': fb.category,
                    'description': fb.description,
                    'location': fb.location,
                    'status': fb.status.lower(),  # Ensure consistent casing
                    'created_at': fb.created_at.isoformat(),
                    'sentiment': analyzeSentiment(fb.description)
                }
                data.append(feedback_item)
            except Exception as item_error:
                logger.error(f"Error processing feedback item {fb.id}: {str(item_error)}")
                continue
        
        logger.info(f"Successfully processed {len(data)} feedback items")
        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching feedback: {str(e)}")
        return Response(
            {
                'error': 'Error fetching feedback data',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def stats(request):
    total = Feedback.objects.count()
    pending = Feedback.objects.filter(status='pending').count()
    return Response({'total': total, 'pending': pending})

@api_view(['POST'])
def update_status(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        feedback.status = request.data.get('status', feedback.status)
        feedback.save()
        return Response({'success': True, 'message': 'Status updated successfully'})
    except Feedback.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Feedback not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error updating feedback status: {str(e)}")
        return Response(
            {'success': False, 'message': 'Error updating status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def home(request):
    return render(request, 'index.html')
