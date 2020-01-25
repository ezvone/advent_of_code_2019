import os
import sys
import subprocess
from itertools import count


for i in count(1):
    py_file = os.path.join(__file__, '..', f'solve{i}.py')
    if not os.path.exists(py_file):
        break
    print(f'Day {i}:')
    assert 0 == subprocess.call([sys.executable, py_file])

