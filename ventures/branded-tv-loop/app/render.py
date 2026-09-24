import subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .db import DATA_DIR

W, H = 1920, 1080

def _font(size, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size)

def _bg(c1=(24,30,28), c2=(58,38,30)):
    im = Image.new("RGB", (W, H), c1)
    px = im.load()
    for y in range(H):
        t = y / max(1, H-1)
        row = tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))
        for x in range(W):
            px[x,y] = row
    return im

def _wrap(draw, text, font_obj, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0,0), test, font=font_obj)[2] <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def render_order(order_id, order, intake):
    order_dir = DATA_DIR / "orders" / str(order_id)
    slides_dir = order_dir / "slides"
    order_dir.mkdir(parents=True, exist_ok=True)
    slides_dir.mkdir(parents=True, exist_ok=True)

    public_name = intake["public_name"] or order["business_name"] or "Your Restaurant"
    promotions = json.loads(intake["promotions_json"] or "[]")
    scenes = [
        ("WELCOME", public_name, "Your restaurant. Your screen. Your message."),
        ("FEATURED", promotions[0] if len(promotions) > 0 else "Today's special", "Ask our team for details."),
        ("PROMOTION", promotions[1] if len(promotions) > 1 else "Promote your best offer", "Update this anytime."),
        ("SOCIAL", intake["social_handles"] or "Follow us online", "Stay connected."),
        ("EVENTS", intake["events_text"] or "Upcoming events", "Keep customers informed."),
        ("THANK YOU", public_name, "Thanks for visiting."),
    ]

    logo = None
    if intake["logo_path"] and Path(intake["logo_path"]).exists():
        try:
            logo = Image.open(intake["logo_path"]).convert("RGBA")
            logo.thumbnail((360, 180))
        except Exception:
            logo = None

    slide_paths = []
    for i, (kicker, title, sub) in enumerate(scenes, 1):
        im = _bg()
        d = ImageDraw.Draw(im)
        d.text((110, 100), "RC BRANDED TV LOOP", font=_font(28, True), fill=(226,160,95))
        d.text((110, 300), kicker, font=_font(42, True), fill=(226,160,95))
        ftitle = _font(78, True)
        lines = _wrap(d, str(title), ftitle, 1250)
        y = 385
        for line in lines[:3]:
            d.text((110, y), line, font=ftitle, fill=(248,244,235))
            y += 95
        d.text((115, min(y+25, 780)), str(sub), font=_font(34), fill=(218,212,202))
        if logo:
            im.paste(logo, (W-logo.width-100, 90), logo)
        p = slides_dir / f"scene_{i}.png"
        im.save(p)
        slide_paths.append(p)

    inputs, filters = [], []
    for i, p in enumerate(slide_paths):
        inputs += ["-loop", "1", "-t", "10", "-i", str(p)]
        filters.append(f"[{i}:v]scale={W}:{H},fps=30,format=yuv420p,fade=t=in:st=0:d=0.5,fade=t=out:st=9.5:d=0.5[v{i}]")
    concat_inputs = "".join(f"[v{i}]" for i in range(len(slide_paths)))
    filter_complex = ";".join(filters) + f";{concat_inputs}concat=n={len(slide_paths)}:v=1:a=0[vout]"
    out = order_dir / "branded_tv_loop.mp4"
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", filter_complex,
           "-map", "[vout]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    return out

def qa_video(path):
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=width,height,r_frame_rate,duration", "-of", "json", str(path)]
    r = subprocess.run(cmd, check=True, capture_output=True, text=True)
    s = json.loads(r.stdout)["streams"][0]
    width, height = int(s["width"]), int(s["height"])
    dur = float(s.get("duration") or 0)
    num, den = s.get("r_frame_rate", "0/1").split("/")
    fps = float(num) / max(float(den), 1)
    passed = width == 1920 and height == 1080 and 59 <= dur <= 61 and 29 <= fps <= 31
    return {"passed": passed, "width": width, "height": height, "duration": dur, "fps": fps}
