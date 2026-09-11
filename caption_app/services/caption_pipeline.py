"""
Captik Caption Pipeline
------------------------
1. Transcribes the uploaded video with openai-whisper (word-level timestamps)
2. Groups words into short punchy caption chunks
3. Builds a styled .ass subtitle file using the project's font + template effect
4. Burns the captions into the video with ffmpeg
5. Updates the VideoProject with the transcript + output file + status
"""

import subprocess
from pathlib import Path

from django.conf import settings

from ..models import VideoProject
from .google_font_downloader import get_font_file

import whisper

_whisper_model = None


def _get_whisper_model():
    """Loads the whisper model once and reuses it (loading is slow)."""
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model("base")
    return _whisper_model


def _seconds_to_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"


def _ffmpeg_escape_path(path):
    """ffmpeg filtergraphs need special escaping, especially for Windows
    paths like C:\\Users\\... where the colon collides with filter syntax."""
    p = str(path).replace("\\", "/")
    p = p.replace(":", "\\:")
    return p


def _get_video_dimensions(path):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0", str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    w, h = result.stdout.strip().split(",")
    return int(w), int(h)


# Basic visual mapping for each CaptionTemplate.effect_type.
# ASS colours are &HAABBGGRR (alpha, blue, green, red).
EFFECT_STYLES = {
    'clean':    {'primary': '&H00FFFFFF', 'outline': '&H00000000', 'size': 48, 'border_style': 1, 'outline_w': 3, 'back': '&H00000000'},
    'neon':     {'primary': '&H00FFFF00', 'outline': '&H00FF00FF', 'size': 52, 'border_style': 1, 'outline_w': 4, 'back': '&H00000000'},
    'fire':     {'primary': '&H0000A5FF', 'outline': '&H000000D0', 'size': 52, 'border_style': 1, 'outline_w': 4, 'back': '&H00000000'},
    'emboss':   {'primary': '&H00D0D0D0', 'outline': '&H00303030', 'size': 46, 'border_style': 1, 'outline_w': 2, 'back': '&H00000000'},
    'gradient': {'primary': '&H00FFC531', 'outline': '&H00000000', 'size': 50, 'border_style': 1, 'outline_w': 3, 'back': '&H00000000'},
    'pill':     {'primary': '&H00000000', 'outline': '&H00000000', 'size': 44, 'border_style': 3, 'outline_w': 0, 'back': '&H80FFC531'},
    'podcast':  {'primary': '&H00FFFFFF', 'outline': '&H00000000', 'size': 60, 'border_style': 1, 'outline_w': 3, 'back': '&H00000000'},
}


def _group_words(word_segments, max_words=4):
    """Groups whisper word timestamps into short on-screen caption chunks."""
    chunks = []
    current = []
    for w in word_segments:
        current.append(w)
        if len(current) >= max_words:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def _build_ass_file(word_chunks, font_family, effect_type, ass_path, video_w, video_h):
    style = EFFECT_STYLES.get(effect_type, EFFECT_STYLES['clean'])

    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {video_w}\n"
        f"PlayResY: {video_h}\n"
        "ScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Caption,{font_family},{style['size']},{style['primary']},&H000000FF,"
        f"{style['outline']},{style['back']},-1,0,0,0,100,100,0,0,"
        f"{style['border_style']},{style['outline_w']},0,2,60,60,{int(video_h * 0.08)},1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    lines = [header]
    for chunk in word_chunks:
        start = chunk[0]['start']
        end = chunk[-1]['end']
        text = " ".join(w['word'].strip() for w in chunk).upper()
        lines.append(
            f"Dialogue: 0,{_seconds_to_ass_time(start)},{_seconds_to_ass_time(end)},"
            f"Caption,,0,0,0,,{text}\n"
        )

    Path(ass_path).write_text("".join(lines), encoding="utf-8")


def process_video(project_id):
    """Main entry point: transcribe + caption + burn for one VideoProject."""

    project = VideoProject.objects.get(id=project_id)
    project.status = 'processing'
    project.save(update_fields=['status'])

    try:
        input_path = Path(project.input_video.path)
        work_dir = input_path.parent
        base_name = input_path.stem

        # 1. Transcribe with word-level timestamps
        model = _get_whisper_model()
        result = model.transcribe(str(input_path), word_timestamps=True)

        word_segments = []
        for segment in result.get('segments', []):
            for w in segment.get('words', []):
                word_segments.append({
                    'word': w['word'],
                    'start': w['start'],
                    'end': w['end'],
                })

        project.transcript_data = result
        project.save(update_fields=['transcript_data'])

        if not word_segments:
            raise ValueError("No speech detected in this video.")

        # 2. Get the actual font file for burning (downloads + caches from Google Fonts)
        font_family = project.active_font
        font_path = get_font_file(font_family)
        fonts_dir = font_path.parent if font_path else None

        # 3. Build the styled .ass subtitle file
        video_w, video_h = _get_video_dimensions(input_path)
        effect_type = project.template.effect_type if project.template else 'clean'
        word_chunks = _group_words(word_segments, max_words=4)

        ass_path = work_dir / f"{base_name}_captions.ass"
        _build_ass_file(word_chunks, font_family, effect_type, ass_path, video_w, video_h)

        # 4. Burn captions into the video with ffmpeg
        output_rel = f"outputs/videos/{base_name}_captioned.mp4"
        output_abs = Path(settings.MEDIA_ROOT) / output_rel
        output_abs.parent.mkdir(parents=True, exist_ok=True)

        vf_filter = f"ass='{_ffmpeg_escape_path(ass_path)}'"
        if fonts_dir:
            vf_filter += f":fontsdir='{_ffmpeg_escape_path(fonts_dir)}'"

        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-vf", vf_filter,
            "-c:a", "copy",
            str(output_abs),
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

        project.output_video.name = output_rel
        project.status = 'completed'
        project.save(update_fields=['output_video', 'status'])

    except subprocess.CalledProcessError as e:
        print(f"[caption_pipeline] ffmpeg failed for project {project_id}: {e.stderr}")
        project.status = 'failed'
        project.save(update_fields=['status'])
    except Exception as e:
        print(f"[caption_pipeline] failed for project {project_id}: {e}")
        project.status = 'failed'
        project.save(update_fields=['status'])
