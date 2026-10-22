"""Small exact-integer outward interval arithmetic for this research audit.

No float/libm operations occur here. Endpoints are integers scaled by 10**50.
This is inspectable research code, not a formally verified arithmetic library.
"""
from fractions import Fraction
from math import factorial, isqrt

SCALE = 10**50


def ceildiv(a, b):
    assert b > 0
    return -((-a)//b)


class I:
    __slots__ = ('lo','hi')

    def __init__(self, lo, hi):
        assert type(lo) is int and type(hi) is int and lo <= hi
        self.lo, self.hi = lo, hi

    @classmethod
    def rational(cls, value):
        value = Fraction(value)
        return cls(value.numerator*SCALE//value.denominator,
                   ceildiv(value.numerator*SCALE,value.denominator))

    def __add__(self, other):
        other = interval(other)
        return I(self.lo+other.lo,self.hi+other.hi)

    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi,-self.lo)

    def __sub__(self, other):
        return self+-interval(other)

    def __rsub__(self, other):
        return interval(other)+-self

    def __mul__(self, other):
        if type(other) is int:
            return I(min(self.lo*other,self.hi*other),max(self.lo*other,self.hi*other))
        other = interval(other)
        values = (self.lo*other.lo,self.lo*other.hi,self.hi*other.lo,self.hi*other.hi)
        return I(min(values)//SCALE,ceildiv(max(values),SCALE))

    __rmul__ = __mul__

    def __truediv__(self, other):
        if type(other) is int and other > 0:
            return I(self.lo//other,ceildiv(self.hi,other))
        other = interval(other)
        if other.hi < 0:
            return (-self)/(-other)
        if other.lo <= 0:
            raise ValueError('Division interval contains zero')
        pairs = [(a*SCALE,b) for a in (self.lo,self.hi) for b in (other.lo,other.hi)]
        return I(min(a//b for a,b in pairs),max(ceildiv(a,b) for a,b in pairs))

    def square(self):
        low = 0 if self.lo <= 0 <= self.hi else min(self.lo*self.lo,self.hi*self.hi)
        high = max(self.lo*self.lo,self.hi*self.hi)
        return I(low//SCALE,ceildiv(high,SCALE))

    def sqrt(self):
        assert self.lo >= 0
        low = isqrt(self.lo*SCALE)
        high = isqrt(self.hi*SCALE)
        if high*high < self.hi*SCALE:
            high += 1
        return I(low,high)

    def absolute(self):
        return I(0 if self.lo <= 0 <= self.hi else min(abs(self.lo),abs(self.hi)),
                 max(abs(self.lo),abs(self.hi)))

    def endpoints(self):
        def decimal(n):
            sign = '-' if n < 0 else ''
            a = abs(n)
            return f'{sign}{a//SCALE}.{a%SCALE:050d}'
        return [decimal(self.lo),decimal(self.hi)]


def interval(value):
    return value if isinstance(value,I) else I.rational(value)


def arctan_bounds(inverse, terms):
    partial = sum((Fraction((-1)**k,(2*k+1)*inverse**(2*k+1)) for k in range(terms)),Fraction())
    other = partial+Fraction((-1)**terms,(2*terms+1)*inverse**(2*terms+1))
    return min(partial,other),max(partial,other)


def pi_interval():
    a,b = arctan_bounds(5,50), arctan_bounds(239,15)
    lo,hi = 16*a[0]-4*b[1],16*a[1]-4*b[0]
    return I(I.rational(lo).lo,I.rational(hi).hi)


PI = pi_interval()
TAYLOR_RADIUS = ceildiv(SCALE*4**56,factorial(56))


def sincos(angle):
    """Enclose sine/cosine using 28 Taylor terms and a degree-55 remainder."""
    angle = interval(angle)
    pi_sum = PI.lo+PI.hi
    shift = (angle.lo+angle.hi+pi_sum)//(2*pi_sum)
    x = angle-PI*(2*shift)
    if max(abs(x.lo),abs(x.hi)) > 4*SCALE:
        raise ValueError('Reduced angle too wide for this bounded Taylor rule')
    xx = x.square()
    st,ct = x,interval(1)
    sine,cosine = st,ct
    for k in range(1,28):
        st = -(st*xx)/((2*k)*(2*k+1))
        ct = -(ct*xx)/((2*k-1)*(2*k))
        sine,cosine = sine+st,cosine+ct
    return (I(sine.lo-TAYLOR_RADIUS,sine.hi+TAYLOR_RADIUS),
            I(cosine.lo-TAYLOR_RADIUS,cosine.hi+TAYLOR_RADIUS))
