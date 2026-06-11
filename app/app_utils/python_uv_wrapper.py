import subprocess
import sys

subprocess.run(['uv', 'run', 'python'] + sys.argv[1:])
