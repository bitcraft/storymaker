import unittest

from mock import Mock

from pygoap.goals import *
from pygoap.precepts import *
from pygoap.memory import MemoryManager


class PreceptGoalTests(unittest.TestCase):
    def test_no_precepts(self):
        with self.assertRaises(ValueError):
            PreceptGoal()

    def test_non_precept_single(self):
        for i in ('a', 1, print, list()):
            with self.assertRaises(ValueError):
                PreceptGoal(i)

    def test_passed_list_constructor(self):
        with self.assertRaises(ValueError):
            PreceptGoal(list())

    def test_non_precepts(self):
        precepts = ['a', 1, print, TimePrecept(1)]
        with self.assertRaises(ValueError):
            PreceptGoal(*precepts)

    def test_valid_precept_single(self):
        precept = TimePrecept(1)
        PreceptGoal(precept)

    def test_valid_precepts_list(self):
        precepts = [TimePrecept(1), TimePrecept(2)]
        PreceptGoal(*precepts)

    def test_touch_update_memory(self):
        precepts = (TimePrecept(1), TimePrecept(2))
        g = PreceptGoal(*precepts)
        memory = Mock(spec=MemoryManager)
        g.touch(memory)
        memory.update.assert_called_once_with(precepts)


class EvalGoalTests(unittest.TestCase):
    mem = None

    def test_raises_nameerror_undefined_name(self):
        g = EvalGoal('a == 1')
        with self.assertRaises(NameError):
            g.test(self.mem)

    def test_raises_syntaxerror_invalid_operator(self):
        g = EvalGoal('1 <> 1')
        with self.assertRaises(SyntaxError):
            g.test(self.mem)

    def test_rases_valueerror_invalid_expression(self):
        with self.assertRaises(ValueError):
            EvalGoal('1 ==')

    def test_ne_true_cmp(self):
        g = EvalGoal('1 != 2')
        self.assertEqual(g.test(self.mem), True)

    def test_ne_false_cmp(self):
        g = EvalGoal('1 != 1')
        self.assertEqual(g.test(self.mem), False)

    def test_eq_true_cmp(self):
        g = EvalGoal('1 == 1')
        self.assertEqual(g.test(self.mem), True)

    def test_eq_false_cmp(self):
        g = EvalGoal('1 == 2')
        self.assertEqual(g.test(self.mem), False)

    def test_lt_true_cmp(self):
        g = EvalGoal('1 < 2')
        self.assertEqual(g.test(self.mem), True)

    def test_lt_false_cmp(self):
        g = EvalGoal('2 < 1')
        self.assertEqual(g.test(self.mem), False)

    def test_lt_eq_true_cmp(self):
        g = EvalGoal('1 <= 1')
        self.assertEqual(g.test(self.mem), True)
        g = EvalGoal('1 <= 2')
        self.assertEqual(g.test(self.mem), True)

    def test_lt_eq_false_cmp(self):
        g = EvalGoal('2 <= 1')
        self.assertEqual(g.test(self.mem), False)

    def test_gt_true_cmp(self):
        g = EvalGoal('2 > 1')
        self.assertEqual(g.test(self.mem), True)

    def test_gt_false_cmp(self):
        g = EvalGoal('1 > 2')
        self.assertEqual(g.test(self.mem), False)

    def test_gt_eq_true_cmp(self):
        g = EvalGoal('1 >= 1')
        self.assertEqual(g.test(self.mem), True)
        g = EvalGoal('2 >= 1')
        self.assertEqual(g.test(self.mem), True)

    def test_gt_eq_false_cmp(self):
        g = EvalGoal('1 >= 2')
        self.assertEqual(g.test(self.mem), False)


class AlwaysValidGoalTests(unittest.TestCase):
    mem = None

    def setUp(self):
        self.g = AlwaysValidGoal()

    def test_is_valid(self):
        self.assertEqual(self.g.test(self.mem), 1.0)

    def test_touch(self):
        pass


class NeverValidGoalTests(unittest.TestCase):
    mem = None

    def setUp(self):
        self.g = NeverValidGoal()

    def test_is_not_valid(self):
        self.assertEqual(self.g.test(self.mem), 0.0)

    def test_touch(self):
        pass
