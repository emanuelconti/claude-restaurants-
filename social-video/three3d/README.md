# 3D videos made with code (owner, 27 November 2026)

Boat-style 3D videos (YC F26 launch videos) built only with code: Three.js scene in one HTML file, rendered frame by frame with Playwright, encoded with ffmpeg. No paid generators, no stock footage needed.

Render (vertical 1080x1920 for Reels, TikTok, YouTube Shorts, Facebook Reels):

    npm i three@0.169.0          # once, in this folder
    SCENE=socialperks-city.html W=1080 H=1920 node render.js
    ffmpeg -framerate 30 -i frames/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart out.mp4

`node render.js 30,120,200,280` renders only those frames: look at them before the full render.
A scene exposes `window.renderAt(t)` (deterministic, t in seconds) and sets `window.ready`. Copy `socialperks-city.html` for a new scene; change the world, captions and colours, keep the contract.
