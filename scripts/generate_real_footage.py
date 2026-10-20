import os
import subprocess
import urllib.request
from pathlib import Path

# Resolve ffmpeg binary
ffmpeg_paths = [
    Path(r"C:\Users\USER\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"),
    Path("ffmpeg")
]
ffmpeg_bin = str(next((p for p in ffmpeg_paths if p.exists()), "ffmpeg"))

footage_dir = Path("tests/fixtures/footage")
footage_dir.mkdir(parents=True, exist_ok=True)

# High-resolution commercial stock photos with rich visual content
clips = {
    "money_finance.mp4": {
        "url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1920&q=80",
        "direction": "in"
    },
    "cloud_computing.mp4": {
        "url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=80",
        "direction": "out"
    },
    "office_workspace.mp4": {
        "url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80",
        "direction": "pan_right"
    },
    "trust_growth.mp4": {
        "url": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1920&q=80",
        "direction": "in"
    },
    "analytics_chart.mp4": {
        "url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1920&q=80",
        "direction": "out"
    },
    "nature_sky.mp4": {
        "url": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1920&q=80",
        "direction": "pan_up"
    }
}

for name, info in clips.items():
    print(f"--> Downloading image for {name}...")
    temp_jpg = footage_dir / f"{name}.jpg"
    out_mp4 = footage_dir / name
    
    req = urllib.request.Request(info["url"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(temp_jpg, "wb") as f:
        f.write(resp.read())
        
    print(f"--> Encoding cinematic video {name} with Ken Burns motion...")
    direction = info["direction"]
    if direction == "in":
        zoom_expr = "zoompan=z='min(zoom+0.0012,1.20)':d=180:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
    elif direction == "out":
        zoom_expr = "zoompan=z='if(lte(zoom,1.0),1.20,max(1.001,zoom-0.0012))':d=180:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
    elif direction == "pan_right":
        zoom_expr = "zoompan=z=1.12:d=180:x='min(x+1.5,iw-iw/zoom)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
    else:
        zoom_expr = "zoompan=z='min(zoom+0.001,1.15)':d=180:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"

    vf = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,{zoom_expr}"
    
    cmd = [
        ffmpeg_bin, "-y",
        "-loop", "1",
        "-i", str(temp_jpg),
        "-vf", vf,
        "-t", "6",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        str(out_mp4)
    ]
    subprocess.run(cmd, check=True)
    if temp_jpg.exists():
        temp_jpg.unlink()
    print(f"SUCCESS: {name} rendered ({out_mp4.stat().st_size:,} bytes)")

print("\n=== ALL REAL CINEMATIC B-ROLL CLIPS GENERATED ===")
