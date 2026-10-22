# What the finite-neighborhood interval audit establishes

For the canonical six-bit interpretation of the inherited fresh-08 witness,
every one of the specified 2,928 neighbors either fails the project's analytical
calibration-bound gate or has strictly worse continuous-angle weighted objective.
This is an author-checked mathematical-model result from inspectable exact-integer
interval code. It is not formal verification of the software or a global optimum.

## Exact problem interpretation

Positions are `x_j=(2j-15)/4`, `j=0,...,15`, in wavelengths; amplitudes are one.
The phase of bin `q_j` is exactly `2*pi*q_j/64`. Steering and notch angles are
the exact decimal numbers in the pinned portfolio JSON, interpreted in degrees.
The stored float phases agree with these bins to less than 1e-13 radians.
The certificate makes the canonical quantized interpretation explicit; it does
not pretend that the stored decimal approximations are the exact number pi.

Define

`F(u) = (1/16) sum_j exp(i*(2*pi*x_j*u + 2*pi*q_j/64))`,
`P(u) = |F(u)|^2`, and `eta=P(u0)` where `u0=sin(steer_angle)`.

The objective is the maximum of `P(u)/eta` on both sidelobe regions and
`16*P(u)/eta` on the notch interval. Region endpoints use the same mathematical
guard 0.15 and published angles. This is a normalized power objective.
The nominal beamwidth and pointing constraints are additional project gates;
excluding a neighbor by gain or objective already excludes improvement under
all gates, so those additional constraints need not be certified for each rejected
neighbor. The incumbent's nominal feasibility remains the unchanged evaluator's
author-checked result.

There are `16*63=1008` single-coordinate alternatives and
`choose(16,2)*4*4=1920` changes of +/-1 or +/-2 bins on each of two distinct
coordinates. Their phase vectors are distinct modulo 64. Larger coordinated
changes and other geometries are outside the statement.

## Arithmetic and transcendental bounds

`integer_intervals.py` represents an interval as two integers divided by
`S=10^50`. Addition and subtraction are exact endpoint operations. Multiplication
and division take the extrema of endpoint products/quotients and round outwards
with integer floor/ceiling. A square crossing zero has lower endpoint zero.
Square roots use integer `isqrt` on the scaled endpoint, adding one when needed
for the upper endpoint. No platform sine, cosine or floating-point rounding mode
supplies a proof bound.

Pi is enclosed using Machin's identity
`pi=16*atan(1/5)-4*atan(1/239)`. Each arctangent is enclosed by its rational
alternating-series partial sum and the partial sum plus its next term, using
50 and 15 terms respectively. All terms are exact `Fraction` values before
outward conversion to scaled integers. The identity itself follows from
`tan(2*atan(1/5))=5/12`, `tan(4*atan(1/5))=120/119`, and hence
`tan(4*atan(1/5)-atan(1/239))=1`, with the angle in the first quadrant.

For sine and cosine, any chosen integer multiple of `2*pi` is subtracted.
The resulting interval is required to lie within `[-4,4]`. The code evaluates
28 terms of each Maclaurin series: sine through degree 55 and cosine through
degree 54. Regard the latter as the degree-55 polynomial with zero odd
coefficient. Taylor's remainder for either function is bounded by
`4^56/56!`, because every derivative has absolute value at most one on the real
axis. The rounded-up radius is added to both ends. Recurrence evaluation uses
outward interval operations throughout; cancellation does not silently discard
rounding error. These bounds also cover uncertainty in pi and in the argument.
The analytic remainder is about 7.30e-42; a scale of 10^50 does not imply
50 correct decimal digits. Primary references are NIST DLMF's
[arctangent series](https://dlmf.nist.gov/4.24.E3),
[sine/cosine series](https://dlmf.nist.gov/4.19), and
[Taylor remainder](https://dlmf.nist.gov/1.4.E36).

The arithmetic tests compare signed operations against an exact rational oracle
over 500 interval cases, check exact-square roots, and test trigonometric values
and period reduction at multiples of pi/2. These are implementation controls,
not a formal proof of the Python interpreter or all possible inputs.

## Calibration gate without inverse trigonometric evaluation

The pinned analytical bound is

`B(eta) = max(0, cos(acos(sqrt(eta)) + delta))^2`,

where the zero branch applies once the angle reaches pi/2, and

`delta = pi/90 + 2*pi*abs(u0)*0.005 + asin(0.03)`.

This shorthand's max formulation is used only on the relevant angle range;
the source definition and its proof are in `trial/coherence.py` and
`trial/MATH.md`. For `m=0.85` and `0 < delta < acos(sqrt(m))`, the gate
`B(eta)>=m` is equivalent to

`eta >= (sqrt(m)*cos(delta) + sqrt(1-m)*sin(delta))^2`.

The code checks the angle conditions. It obtains sine/cosine of delta by angle
addition, using `sin(asin(0.03))=0.03` and
`cos(asin(0.03))=sqrt(1-0.03^2)`. Thus no numerical acos or asin is needed.
The threshold interval is retained in the certificate. The optimizer's extra
0.005 slack and its 1e-9 numerical padding are not imposed in this exclusion:
the proof covers the full mathematical gate.

For 1,508 neighbors, the nominal-efficiency interval upper endpoint is below
the threshold interval lower endpoint. They fail the pinned sufficient-bound
gate. This does not prove that the real perturbed array's physical efficiency
would fall below 0.85; a sufficient lower bound can be conservative.

## Continuous-angle incumbent upper bound

For equal amplitudes, `|F|<=1`, `|F'|<=2*pi*mean(|x|)`, and
`|F''|<=(2*pi)^2*mean(x^2)`. Since
`P''=2*(|F'|^2+Re(conj(F)*F''))`, a uniform bound is

`M=2*((2*pi*mean(|x|))^2 + (2*pi)^2*mean(x^2))`.

Here `mean(|x|)=2` and `mean(x^2)=85/16`; M is evaluated outwards.
For twice differentiable P on any grid cell of width h, its linear interpolant
differs from P by at most `M*h^2/8`. Therefore the largest certified grid-node
upper bound plus this correction bounds P everywhere in the region. This
argument does not assume every stationary point was located.
See NIST DLMF's [linear interpolation formula](https://dlmf.nist.gov/3.3.E14)
and [one-eighth error constant](https://dlmf.nist.gov/3.3.E15).

The interval script builds 6,140, 4,063 and 319 nodes for the left sidelobe,
right sidelobe and notch regions, respectively, with at most 1/6000 separation
in direction cosine. Each endpoint and interior node is an outward interval
covering its exact mathematical location. Dividing by the incumbent desired
power lower bound and applying the region weights gives a total score upper
bound of

`0.03473444010039710098354946692969690810289752014208`.

This is slightly wider than the existing float64 evaluator's upper estimate;
it is obtained without relying on that estimate.

## Point lower bounds exclude the other 1,420 neighbors

For each neighbor above the calibration threshold, a single point inside one
weighted region lower-bounds its continuous-angle maximum. `locate_points.py`
selects numerical grid maxima and refines eight close cases by numerical
stationary-point locations. Those computations supply points only.

The interval script checks each supplied point's region membership and evaluates
its weighted power ratio afresh. Rational fractional-grid nodes include exact
region endpoints. Decimal root estimates must lie strictly within the certified
endpoint limits. A root estimate need not actually be a root: any valid point
is sufficient for a lower bound.

All 1,420 resulting lower endpoints exceed the certified incumbent upper.
The smallest separation is

`0.00000946132880931184555869385605184439217185689074`

in normalized weighted power. The full per-neighbor classifications, phase
changes, point locations and interval endpoints are in
`neighborhood-certificate.json`. Every neighbor is accounted for; no ambiguous
case was dropped. The original four sampled-descent variants and all 7,872
attempted scores are retained separately.

This certificate concerns nominal continuous-angle suppression under a gate
on the analytical efficiency bound. It supplies no error-box guarantee for
perturbed sidelobes, beamwidth or pointing, and no hardware claim. The source
audit is same-model AI mathematical research, not independent-person acceptance.
