import sys, pathlib, unittest

sys.path.append(str(pathlib.Path(__file__).parents[1].joinpath("project").resolve()))

import autoleave

class TestAutoLeave(unittest.TestCase):
    def test_getNumberOfPeople(self):
        self.assertEqual(autoleave.getNumberOfPeople("Contributors = 1"), 1)
        self.assertEqual(autoleave.getNumberOfPeople("Contributors = 12"), 12)
        
if __name__ == "__main__":
    unittest.main()