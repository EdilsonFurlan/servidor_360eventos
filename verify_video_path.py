from videos.models import Video, Event
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import uuid

User = get_user_model()
# Create or get a user
user, created = User.objects.get_or_create(email='testuser_video_path@example.com', defaults={'nome': 'Test User'})

# Create an event
event = Event.objects.create(name='Test Event Path', user=user, event_date='01/01/2024')

# Create a video
video = Video.objects.create(
    event=event, 
    user=user, 
    unique_id=str(uuid.uuid4()), 
    video_file=ContentFile(b'content', name='test_path.mp4')
)

print(f"Video Path: {video.video_file.name}")

expected_path = f"{user.id}/{event.id}/test_path.mp4"
if video.video_file.name == expected_path:
    print("SUCCESS: Path matches expected format.")
else:
    print(f"FAILURE: Path does not match. Expected: {expected_path}")
