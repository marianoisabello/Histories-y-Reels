import subprocess, numpy as np, onnxruntime as ort, sys
W, H = 1080, 1920
src, out_a, out_f = sys.argv[1], sys.argv[2], sys.argv[3]
sess = ort.InferenceSession('/home/claude/models/rvm.onnx', providers=['CPUExecutionProvider'])
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc_a = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'ffv1', out_a], stdin=subprocess.PIPE)
enc_f = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-crf', '10', '-preset', 'veryfast', '-pix_fmt', 'yuv444p', out_f], stdin=subprocess.PIPE)
rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
dr = np.array([0.25], np.float32)
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    x = (img.astype(np.float32) / 255).transpose(2, 0, 1)[None]
    fgr, pha, *rec = sess.run(None, {'src': x, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3], 'downsample_ratio': dr})
    enc_a.stdin.write((pha[0, 0] * 255).clip(0, 255).astype(np.uint8).tobytes())
    enc_f.stdin.write((fgr[0].transpose(1, 2, 0) * 255).clip(0, 255).astype(np.uint8).tobytes())
    n += 1
    if n % 50 == 0:
        print(n, flush=True)
enc_a.stdin.close(); enc_f.stdin.close(); enc_a.wait(); enc_f.wait()
print('done', n)
