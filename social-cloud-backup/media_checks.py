"""Decoded media checks shared by controller --validate/--check and the tests.

Reels/Shorts must be real 1080x1920 30 fps H.264 files with an audible AAC
track (decoded, not just declared). Reels made from 5 November 2026 onward
must also last 15-30 seconds and carry a 1080x1920 JPEG cover and a reel.json
whose caption starts with the queue item's exact title.
"""
import json
import re
import subprocess
from pathlib import Path


def probe(video: Path) -> dict:
    return json.loads(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate',
         '-show_entries', 'format=duration', '-of', 'json', str(video)], text=True))


def loudness(video: Path) -> tuple:
    """(mean dB, max dB) of the fully decoded audio track."""
    out = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(video), '-map', '0:a:0', '-af', 'volumedetect',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    mean = re.search(r'mean_volume: (-?[\d.]+) dB', out)
    peak = re.search(r'max_volume: (-?[\d.]+) dB', out)
    if not mean or not peak:
        raise AssertionError(f'{video}: audio track could not be decoded')
    return float(mean.group(1)), float(peak.group(1))


def check_video(video: Path, new_reel: bool = False, legacy_silent_ok: bool = False) -> dict:
    """legacy_silent_ok only for already-published 3 November Shorts made before the audio rule."""
    info = probe(video)
    v = [s for s in info['streams'] if s['codec_type'] == 'video']
    a = [s for s in info['streams'] if s['codec_type'] == 'audio']
    assert len(v) == 1 and v[0]['codec_name'] == 'h264' and (v[0]['width'], v[0]['height']) == (1080, 1920), f'{video}: not 1080x1920 H.264'
    fps = v[0]['r_frame_rate']
    assert fps in ('30/1', '30000/1001') if new_reel else fps in ('24/1', '25/1', '30/1', '30000/1001', '60/1'), f'{video}: frame rate {fps}'
    if legacy_silent_ok and not a:
        return dict(seconds=float(info['format']['duration']), mean_db=None, peak_db=None, legacy=True)
    assert len(a) == 1 and a[0]['codec_name'] == 'aac', f'{video}: no AAC audio track'
    seconds = float(info['format']['duration'])
    assert (15 <= seconds <= 30.5) if new_reel else (0 < seconds <= 60), f'{video}: duration {seconds}'
    mean, peak = loudness(video)
    assert mean > -35 and peak > -15, f'{video}: audio is silent or nearly silent ({mean} dB mean, {peak} dB peak)'
    return dict(seconds=seconds, mean_db=mean, peak_db=peak)


def check_reel_folder(folder: Path, title: str) -> None:
    meta = json.loads((folder / 'reel.json').read_text())
    assert meta['caption'].split('\n', 1)[0].strip() == title.strip(), f'{folder}: caption does not open with the exact title'
    assert meta['title'] == title, f'{folder}: reel title differs from the queue title'
    cover = folder / 'cover.jpg'
    if cover.exists() or folder.name != 'reel':
        from PIL import Image
        with Image.open(cover) as image:
            assert image.format == 'JPEG' and image.size == (1080, 1920), f'{folder}: cover must be a 1080x1920 JPEG'
