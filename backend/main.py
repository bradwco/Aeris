import os
import importlib.util

this_dir = os.path.dirname(__file__)
fd_path = os.path.join(this_dir, "face_detection", "face_detection.py")
spec = importlib.util.spec_from_file_location("face_detection", fd_path)
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

if hasattr(fd, "run"):
	fd.run()
else:
	import os
	import importlib.util
	import argparse

	this_dir = os.path.dirname(__file__)
	fd_path = os.path.join(this_dir, "face_detection", "face_detection.py")
	spec = importlib.util.spec_from_file_location("face_detection", fd_path)
	fd = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(fd)

	parser = argparse.ArgumentParser()
	parser.add_argument("--host", default="0.0.0.0")
	parser.add_argument("--port", default=8080, type=int)
	parser.add_argument("--device", default=0, type=int)
	args = parser.parse_args()

	if hasattr(fd, "run"):
		fd.run(host=args.host, port=args.port, device=args.device)
	else:
		import runpy
		runpy.run_path(fd_path, run_name="__main__")