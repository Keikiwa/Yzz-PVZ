import os, sys
import urllib.request
from PIL import Image, ImageSequence

BASE_URL = "https://cdn.jsdelivr.net/gh/Plants-vs-Zombies-MODDED/game@main/"
CACHE_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\download_cache"
PLANTS_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\assets\plants"

def download_file(rel_url, local_name):
    url = BASE_URL + rel_url
    path = os.path.join(CACHE_DIR, local_name)
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return path
    print(f"Downloading {local_name} from {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        with open(path, "wb") as f:
            f.write(resp.read())
    return path

def extract_gif_to_frames(gif_path, out_dir, prefix="idle"):
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(gif_path)
    
    # Clean old simple dummy files in out_dir
    # Remove files if they are small dummy files
    frames = []
    # To properly extract transparent GIF frames in PIL:
    # A GIF frame might have disposal method or rely on canvas
    last_frame = None
    for idx, frame in enumerate(ImageSequence.Iterator(im)):
        # Convert to RGBA
        frame_rgba = frame.convert("RGBA")
        
        # In PVZ web gifs, background is often palette index with alpha=0 or transparent
        # If the gif has transparency palette:
        if "transparency" in frame.info:
            trans_idx = frame.info["transparency"]
            # get palette
            pal = frame.getpalette()
            # If convert RGBA already handled it:
            # Let's inspect transparency
            pass
            
        out_name = f"{prefix}_{idx}.png"
        out_path = os.path.join(out_dir, out_name)
        frame_rgba.save(out_path)
        frames.append(out_path)
    print(f"Extracted {len(frames)} frames to {out_dir} with prefix {prefix}")
    return frames

print("Script template ready.")
