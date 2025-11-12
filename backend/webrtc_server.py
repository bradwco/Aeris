import asyncio
import cv2
import aiohttp
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import av
import numpy as np


class OpenCVVideoTrack(VideoStreamTrack):
    def __init__(self, device=0, width=640, height=480, fps=20):
        super().__init__()
        self.cap = cv2.VideoCapture(device)
        if width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.fps = fps

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            # return black frame if capture failed
            img = 255 * np.zeros((480, 640, 3), dtype='uint8')
            frame = img
        # convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = av.VideoFrame.from_ndarray(frame, format='rgb24')
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame


pcs = set()


async def index(request):
    html = """
<!doctype html>
<html>
  <head><meta charset="utf-8"/></head>
  <body>
    <video id="video" autoplay playsinline controls style="width:100%;height:auto"></video>
    <script>
    async function start() {
      const pc = new RTCPeerConnection();
      pc.ontrack = function(event) {
        const el = document.getElementById('video');
        el.srcObject = event.streams[0];
      };
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      const res = await fetch('/offer', {method:'POST', body: JSON.stringify({sdp: offer.sdp, type: offer.type}), headers:{'Content-Type':'application/json'}});
      const answer = await res.json();
      await pc.setRemoteDescription(answer);
    }
    start();
    </script>
  </body>
</html>
"""
    return web.Response(content_type='text/html', text=html)


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on('connectionstatechange')
    async def on_connstatechange():
        if pc.connectionState == 'failed' or pc.connectionState == 'closed':
            await pc.close()
            pcs.discard(pc)

    track = OpenCVVideoTrack()
    pc.addTrack(track)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})


def main(host='0.0.0.0', port=8081):
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_post('/offer', offer)
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
