from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import CaptionTemplate, VideoProject
from .services.font_engine import search_fonts

def font_search_view(request):
    """
    AJAX endpoint used by the font-picker search box
    GET /fonts/search/?q=pop -> {"fonts": ["Poppins", ...]}
    """
    query = request.GET.get('q', '')
    results = search_fonts(query)[:50]
    return JsonResponse({'fonts': results})

def dashboard_view(request):
    templates = CaptionTemplate.objects.filter(is_active=True)
    projects = VideoProject.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled video')
        input_video = request.FILES.get('input_video')
        template_id = request.POST.get('template_id')
        selected_font = request.POST.get('selected_font', '')

        if input_video:
            template = CaptionTemplate.objects.filter(id=template_id).first()
            VideoProject.objects.create(
                user=request.user if request.user.is_authenticated else None,
                title=title,
                input_video=input_video,
                template=template,
                selected_font=selected_font,
                status='pending'
            )
            return redirect('dashboard')

    return render(request, 'caption_app/dashboard.html', {
        'templates': templates,
        'projects': projects,
    })
