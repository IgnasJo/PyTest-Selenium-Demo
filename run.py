import pytest

# Run through standard python executer
# -n 2 : parallelize to 2 instances if possible
# -rP : print full report
# -v : verbose
pytest.main(['-rP', '-v'])