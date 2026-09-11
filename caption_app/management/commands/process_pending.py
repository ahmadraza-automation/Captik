from django.core.management.base import BaseCommand
from caption_app.models import VideoProject
from caption_app.services.caption_pipeline import process_video


class Command(BaseCommand):
    help = "Transcribe and burn captions for every VideoProject stuck in 'pending' status."

    def handle(self, *args, **options):
        pending = VideoProject.objects.filter(status='pending')
        count = pending.count()
        self.stdout.write(f"Found {count} pending project(s).")

        for project in pending:
            self.stdout.write(f"Processing: {project.title} (id={project.id})...")
            process_video(project.id)
            project.refresh_from_db()
            self.stdout.write(self.style.SUCCESS(f" -> {project.status}"))
