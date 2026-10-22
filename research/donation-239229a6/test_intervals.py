"""Exact rational-oracle controls for the arithmetic supporting this certificate."""
from fractions import Fraction
import random
import unittest
from integer_intervals import I, PI, SCALE, interval, sincos


def encloses(i,x):
    return Fraction(i.lo,SCALE)<=x<=Fraction(i.hi,SCALE)


class IntervalControls(unittest.TestCase):
    def test_signed_operations_against_fraction_endpoints(self):
        rng = random.Random(239229)
        for _ in range(500):
            a,b = sorted(Fraction(rng.randint(-1000,1000),rng.randint(1,1000)) for _ in range(2))
            c,d = sorted(Fraction(rng.randint(-1000,1000),rng.randint(1,1000)) for _ in range(2))
            x,y = I(interval(a).lo,interval(b).hi),I(interval(c).lo,interval(d).hi)
            for u in (a,b):
                self.assertTrue(encloses(x.square(),u*u))
                for v in (c,d):
                    self.assertTrue(encloses(x+y,u+v))
                    self.assertTrue(encloses(x-y,u-v))
                    self.assertTrue(encloses(x*y,u*v))
                    if c>0 or d<0:
                        self.assertTrue(encloses(x/y,u/v))

    def test_sqrt_exact_square_controls(self):
        for n in range(0,300):
            q = Fraction(n,137)
            self.assertTrue(encloses(interval(q*q).sqrt(),q))

    def test_trigonometric_identities_and_period_reduction(self):
        for turns in (-100,-2,0,1,100):
            for quarter,expected in [(0,(0,1)),(1,(1,0)),(2,(0,-1)),(3,(-1,0))]:
                s,c = sincos(PI*Fraction(4*turns+quarter,2))
                self.assertTrue(encloses(s,Fraction(expected[0])))
                self.assertTrue(encloses(c,Fraction(expected[1])))
                self.assertLess(s.hi-s.lo,10**14)
                self.assertLess(c.hi-c.lo,10**14)

    def test_reject_zero_divisor_and_invalid_sqrt(self):
        with self.assertRaises(ValueError):
            interval(1)/I(-1,1)
        with self.assertRaises(AssertionError):
            interval(-1).sqrt()


if __name__ == '__main__':
    unittest.main()
