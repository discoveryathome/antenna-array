# Bounds audit — fresh-08-calibration-margin

Status: completed mathematical and primary-source research audit, within the requested 20-minute budget. Research began at 2026-10-22 19:43:20 UTC. This is a same-model, fresh-context AI review, not independent-person review or formal verification.

Task: `fresh-08-calibration-margin`; donation round 5; seed `239229a686e46247e5c96c3b6d7b0993`; repository `donation-20261022T173844Z/round-5/repo`; verified base/HEAD `d9db8b4f07222da18b89cd4a936cbcf5e915925f`.

The proposed mathematical route is valid, subject to the model and enclosure conditions below. A completed exact-integer interval computation can exclude every member of the specified finite neighborhood from improving the incumbent under a precisely stated calibration-bound gate. This report checks that argument and its mathematical sources; it does **not** certify the parent's implementation, completed neighborhood classifications, or continuous incumbent upper bound.

Concrete corrections and qualifications:

- The stored centered positions are `x_j=(2*j-15)/4`, for `j=0,...,15`: odd quarter-integers with half-wavelength spacing. Half-integer coordinates require an explicitly stated common origin shift. Such a shift preserves power, but coordinates and the curvature calculation must be consistent.
- The proposed required nominal efficiency is the calibration threshold **without** design slack. `trial/coherence.py:19` defaults to adding `0.005`. Excluding all neighbors that pass the weaker threshold is sufficient for exclusion under the stronger slack threshold too; it is not identical to the default design-floor test.
- Scoring weights are **1 for sidelobes and 16 for notches**, as in `docs/MODEL.md:19`; interpret “weight1/16” as those two weights, never a factor of `1/16`.
- The proposed common sine/cosine Taylor remainder is valid, including cosine's zero degree-55 coefficient. Its value is approximately `7.3028230261e-42`, so the `10^50` fixed-point scale is not a claim of 50-digit accuracy.
- The proposed curvature bound is valid. On the stored centered geometry it is `(149/2)*pi^2`; the repository's sharper pairwise bound is `(85/2)*pi^2`. Either may be used with outward enclosures.
- Exact scoring-region boundaries involve sines of decimal degree angles and `u0 +/- 3/20`. Cover these boundaries with outward enclosures or exact symbolic endpoint grids. An ordinary floating grid alone does not establish coverage.
- A competitor score lower bound divides a certified in-region point-power lower bound by that competitor's **desired-power upper bound**. The incumbent score upper divides the continuous peak upper by its **desired-power lower bound**, which must be positive.
- Failure of the sufficient calibration bound excludes a neighbor from the pinned bound gate; it does not establish failure of actual physical robust efficiency.

The details below distinguish primary-source statements from this audit's own algebraic specializations and numerical spot checks.

## 1. Exact model and provenance

The repository contract is a scalar, isotropic, equal-amplitude, 16-element array. Its six-bit phase set is exactly `phi_j=2*pi*q_j/64`, with integer `q_j` modulo 64. The stored centered positions are `x_j=(2*j-15)/4`, in wavelengths. These are exact rational inputs. See [the model contract](../../docs/MODEL.md), especially its physical scope and scoring definitions, and [the source geometry and masks](../../src/model.py).

The selected fresh target is in [the frozen readiness portfolio](../../research/readiness-20261021/portfolio.json), in task `fresh-08-calibration-margin` beginning at line 2223. Its exact decimal degree inputs are:

- Steering: `9.971020978907605`.
- Notch endpoints: `-15.88751027062795` and `-12.762826260560622`.

Thus `u0=sin(pi*9.971020978907605/180)`. The side region is `[-1,u0-3/20] union [u0+3/20,1]`, including the two mask boundaries. The notch endpoints are the sines of the exact decimal angles times `pi/180`. All these angles lie in the monotone branch from -90 to 90 degrees, and the notch is a subset of the side region. The target is marked `exposed-development`, not a fresh held-out result. `configs/frozen.json` is freeze metadata; the report should identify the actual portfolio target, not leave “the frozen JSON” ambiguous.

The canonical incumbent phase bins used in this audit's spot check are:

`[38,41,20,28,18,12,6,2,60,54,49,42,37,35,29,18]`.

These identify the intended six-bit design corresponding to the stored incumbent. The historical `phases_rad` decimals and NumPy/math angle calculations are rounded numerical representations. A certificate for canonical phases and exact decimal target angles is a certificate for the stated ideal model, not automatically a certificate for every intermediate float64 operation of the historical evaluator. Parse decimal inputs as exact decimal rationals before enclosure; converting a JSON number to binary float and then to a rational silently changes that convention.

A common position translation is harmless to power: replacing every `x_j` by `x_j+c` multiplies `F(u)` by `exp(i*2*pi*c*u)`, leaving `P(u)` unchanged. Half-integer coordinates are therefore permissible if explicitly identified as such a translation. Arbitrarily rounding each centered position is not permissible. The curvature proof must use a justified geometry, including any use of a centered representation.

## 2. Integer intervals: what must actually be outward rounded

Let `S=10^50`, with integer pair `[l,h]` denoting the closed real interval `[l/S,h/S]`. The following are sufficient elementary enclosure rules, derived directly from interval endpoint inequalities:

- Addition is exact endpoint addition. Negation reverses and negates the endpoints.
- For multiplication, take all four integer endpoint products, divide their minimum downward by `S`, and their maximum upward by `S`.
- For division by a strictly positive interval, enclose all endpoint quotients with the appropriate scale and outward division. For nonnegative numerator `[a,b]` and positive denominator `[c,d]`, the real lower and upper ratios are `a/d` and `b/c`.
- For signed integers and positive divisor `d`, floor division must mean mathematical floor, and ceiling can be implemented as `-floor(-n/d)`. Truncation toward zero is not downward rounding for negative numbers.
- Squaring an interval crossing zero has lower bound zero. Squaring its lower endpoint is not a valid lower bound in that case. The same care applies to absolute values.
- If `0<=l<=h`, a square-root enclosure has integer lower endpoint `isqrt(l*S)` and upper endpoint `ceil_sqrt(h*S)`. If `k=isqrt(h*S)`, use `k` when `k*k=h*S`, otherwise `k+1`. Python documents `isqrt` as an exact integer floor square root. [Python integer square-root documentation](https://docs.python.org/3.12/library/math.html#math.isqrt).

Use arbitrary-precision integers, exact factorials and integer powers. A fixed scale does not protect an operation that first converts to float. Every coefficient, division, grid endpoint, denominator and tail allowance must remain enclosed. Intersecting a power interval with `[0,1]` is legitimate here because `|F|<=1` has an independent proof for equal unit amplitudes; it must not be used to conceal an otherwise unjustified computation.

These rules provide a sound route to outward-rounded fixed-point interval arithmetic without a libm error assumption. Their correct implementation remains a separate obligation. The phrase “directed-rounding interval certificate” should be reserved for an implementation and output that actually satisfy them, with its runtime and integer-arithmetic trust assumptions stated.

## 3. Pi, range reduction and trigonometric tails

### Machin identity and branches

The identity `pi=16*atan(1/5)-4*atan(1/239)` is valid. It can be checked independently from the [DLMF tangent addition identity, 4.21.4](https://dlmf.nist.gov/4.21.E4): put `a=atan(1/5)` and `b=atan(1/239)`. Then

`tan(2a)=5/12`, `tan(4a)=120/119`, and `tan(4a-b)=1`.

For the branch: `0<a<pi/4`; because `tan(2a)=5/12<1`, `2a<pi/4`, hence `4a<pi/2`. Also `b<a`, so `0<4a-b<pi/2`. Consequently `4a-b=pi/4`, proving the claimed identity without assuming it from a floating approximation. This is this audit's algebraic derivation from the cited primary reference.

### Rational arctangent tails

For `0<x<1`, set `A_n(x)=sum(k=0,...,n-1) (-1)^k*x^(2k+1)/(2k+1)`. The series is given in [DLMF 4.24.3](https://dlmf.nist.gov/4.24.E3). The exact remainder identity

`atan(x)-A_n(x)=(-1)^n * integral_0^x t^(2n)/(1+t^2) dt`

follows by integrating a finite geometric identity, using the [DLMF arctangent integral](https://dlmf.nist.gov/4.23.E3). Its sign is `(-1)^n`, and its magnitude is at most `x^(2n+1)/(2n+1)`. Thus it supplies both the alternating-series enclosure and its correct orientation.

With **50 terms meaning k=0,...,49**, `atan(1/5)` lies between `A_50` and `A_50 + 1/(101*5^101)`. With **15 terms meaning k=0,...,14**, `atan(1/239)` lies between `A_15 - 1/(31*239^31)` and `A_15`. The subtraction in Machin's formula reverses which endpoint of the second interval is used. Before fixed-scale quantization, the resulting pi-interval width is bounded by

`16/(101*5^101) + 4/(31*239^31)`, approximately `4.01872e-72`.

Per-term outward rounding may widen that interval; this does not invalidate it. Discarding tails because they are smaller than one scale unit would invalidate an enclosure unless their possible effect is still covered.

### Arbitrary integer range reduction

For any **fixed integer** `m`, replacing a real argument `t` by `r=t-2*pi*m` preserves sine and cosine. An approximate value may choose `m`; its optimality is irrelevant. What matters is subsequently enclosing the exact subtraction and checking that **the entire reduced interval** is contained in `[-4,4]`. An approximate midpoint passing the check is insufficient. Ignoring correlations between repeated occurrences of pi can widen an interval but is safe when ordinary inclusion-preserving interval operations are used.

### Twenty-eight Taylor terms

Use `sum(k=0,...,27) (-1)^k*r^(2k+1)/(2k+1)!` for sine and `sum(k=0,...,27) (-1)^k*r^(2k)/(2k)!` for cosine. These are the series in [DLMF 4.19.1 and 4.19.2](https://dlmf.nist.gov/4.19).

Both are Taylor polynomials **through degree 55**: sine's highest term is degree 55; cosine's degree-55 coefficient is zero, so its last nonzero term is degree 54. By the [Taylor remainder, DLMF 1.4.35–36](https://dlmf.nist.gov/1.4.E36), their errors on the real interval `|r|<=4` are each at most `4^56/56!`, since every relevant sine/cosine derivative has magnitude at most one. The common bound is conservative and correct.

Independent exact-rational calculation gives `4^56/56!` approximately `7.30282302608437e-42`. At scale `10^50`, an outward allowance is **730282303 integer units on each side**, in addition to already-enclosed polynomial-evaluation errors. Thus “scale 10^50” describes representation, not 50 certified decimal digits. Interval polynomial evaluation must include argument uncertainty; evaluating only its endpoints is not generally an interval sine/cosine algorithm.

## 4. Calibration bound and its inversion

The proof in [trial/MATH.md](../../trial/MATH.md) is valid in the stated equal-amplitude model. For unit vectors with nominal desired overlap `r=sqrt(eta)`, orthogonal decomposition and Cauchy–Schwarz give, after a ray-angle perturbation of at most `epsilon`,

`|desired overlap after error| >= max(0, r*cos(epsilon)-sqrt(1-r^2)*sin(epsilon))`.

The phase and position errors at the **fixed desired direction** have per-element phase magnitude at most `d=pi/90 + 2*pi*abs(u0)/200`. Their normalized overlap has real part at least `cos(d)`. For positive amplitudes in `[a,b]=[0.97,1.03]`, writing `m=mean(amplitude)`, the elementary inequality `amplitude^2 <= (a+b)*amplitude-ab` gives

`m^2/mean(amplitude^2) >= 4ab/(a+b)^2 = 1-(3/100)^2`.

The minimum follows by minimizing `m^2/((a+b)m-ab)` on `[a,b]`. Hence amplitude errors add at most `asin(3/100)` to the ray angle. Applying the overlap inequality successively proves the stated coherent-efficiency bound with the **actual perturbed excitation-power denominator**, including correlated/adversarial errors within this box. It is not a theorem about sidelobes, beamwidth, pointing, mutual coupling, or RF radiation efficiency.

Let `delta=d+asin(3/100)` and `beta=acos(sqrt(17/20))`. If `0<=delta<=beta`, the condition that this sufficient lower bound reaches `17/20` is exactly

`eta >= T = cos(beta-delta)^2`

`T = (sqrt(17/20)*cos(delta) + sqrt(3/20)*sin(delta))^2`.

This follows because `acos(sqrt(eta))` is decreasing on `[0,1]`, and cosine squared is decreasing on `[0,pi/2]`. The angle condition is essential: if `delta>beta`, even perfect nominal coherence cannot reach the requested lower bound, whereas blindly evaluating the displayed squared expression would produce a misleading threshold below one.

No interval inverse-trigonometric implementation is needed to compute `T`. Set `c=sqrt(1-(3/100)^2)` and compute

`sin(delta)=sin(d)*c + cos(d)*(3/100)`,

`cos(delta)=cos(d)*c - sin(d)*(3/100)`.

The positive square root is required. These are direct uses of [DLMF sine/cosine addition formulas](https://dlmf.nist.gov/4.21.E2) and the principal branch `asin(3/100) in [0,pi/2]`. Angle validation can use a coarse exact bound `delta<1/10<pi/2`, together with `sin(delta)<sqrt(3/20)`; no floating acos/asin call is necessary. For example, `asin(a)<=a/sqrt(1-a^2)` follows by bounding the integrand in its defining integral.

The [source implementation](../../trial/coherence.py) adds default design slack `1/200=0.005`, capped at one. The current target is far from that cap. Therefore `T` is the no-slack sufficient-bound gate; `T+0.005` is the default design floor. Excluding improvements for all neighbors with `eta>=T` also excludes them under the stricter design floor. Do not label these gates identical or silently inherit historical floating tolerances.

For intervals `eta in [eta_L,eta_U]` and `T in [T_L,T_U]`:

- Prove gate failure only when `eta_U<T_L`.
- Prove gate passage when `eta_L>=T_U`.
- If they overlap, leave gate status ambiguous. A separate objective exclusion can still resolve the neighbor without deciding its gate status.

Failure here means failure of this **sufficient bound test**. It does not imply that an allowed physical perturbation actually violates efficiency, nor that the candidate is outside the full set of physically robust designs.

## 5. Continuous incumbent upper bound

For `F(u)=N^-1 sum exp(i*(2*pi*x_j*u+phi_j))`, equal amplitudes imply

`|F|<=1`, `|F'|<=2*pi*mean(abs(x))`, and `|F''|<=(2*pi)^2*mean(x^2)`.

Differentiating the power gives `P''=2*|F'|^2+2*Re(F''*conj(F))`. Triangle inequalities therefore prove the proposed global bound

`|P''| <= M = 2*((2*pi*mean(abs(x)))^2+(2*pi)^2*mean(x^2))`.

This is this audit's direct derivation. On the stored centered geometry, `mean(abs(x))=2` and `mean(x^2)=85/16`, hence `M=(149/2)*pi^2`, approximately `735.2855278811572`.

The pairwise expression already in [the evaluator](../../src/evaluator.py), `N^-2 sum_ij (2*pi*(x_i-x_j))^2`, is another valid bound. Here it is `(85/2)*pi^2`, approximately `419.4581870462977`. It is translation invariant and tighter. The proposed larger `M` remains correct; it may simply require a finer grid. Replacing the historical curvature constant by a larger one without refining the grid can widen the upper bound enough to lose a borderline comparison.

For a subinterval `[a,b]`, the linear interpolant is a convex combination of the endpoint powers. Its remainder has magnitude at most `M*(b-a)^2/8`. This is the specialization of the [DLMF Lagrange remainder](https://dlmf.nist.gov/3.3.E5), with the linear coefficient explicitly given by [DLMF 3.3.14–15](https://dlmf.nist.gov/3.3.E15). Thus, if each endpoint power is enclosed above by `U_k`,

`sup_region P <= max_k U_k + M_U*h_U^2/8`,

provided `M_U` is an upper bound for `M` and `h_U` bounds every actual cell width. Round the arithmetic of the added term upward. With `m+1` nodes there are `m` gaps, not `m+1` gaps. Nonuniform grids also work if the maximum gap or each individual gap is bounded.

Exact region endpoints are generally irrational. Two valid grid constructions are:

1. Define mathematical nodes `a+k*(b-a)/m` using exact endpoint expressions, enclose each node, enclose its power, and upper-bound the exact spacing.
2. Enclose the region in an outer rational interval `[a_L,b_U]`, use an exact rational grid covering that whole interval, and bound the supremum there. Covering a slightly larger region is conservative for an upper bound.

All closed side/notch endpoints must be included in the cover. Inward-rounded endpoints or nominally equal floating steps without a coverage argument are insufficient. Bounds for separate intervals are combined by maximum. Region overlap is harmless.

For positive certified incumbent desired power `P0_L`, the final score upper bound is

`J_inc_U = max(B_side_U, 16*B_notch_U)/P0_L`,

rounded upward. `P0_L` is the lower bound for the incumbent's power at the exact `u0`. Do not normalize by the main-beam maximum or by a nominal denominator from another candidate.

## 6. Competitor lower bounds and comparison logic

For any certified point `t` in a scoring region with weight `w` equal to 1 or 16,

`J_neighbor >= w*P_neighbor(t)/P_neighbor(u0)`.

Thus `w*P_point_L/P0_neighbor_U`, rounded downward, is a valid continuous-score lower bound, assuming the actual desired power is positive. Each neighbor needs its own denominator. Multiple certified points or regions may be combined by maximum, but one successful point suffices.

An existing sample argmax or floating stationary-root estimate may supply a point. Record its exact rational interpretation—either its exact binary rational value or the exact decimal string chosen for the witness—and recompute its power with enclosures. No claim that the point is stationary, locally maximal, or part of a complete root list is needed. A poor point weakens the lower bound; it does not invalidate the method.

Region membership must be certified under the exact target definition. For a rational point, sufficient tests include:

- Left side: `-1<=t<=u0_L-3/20`.
- Right side: `u0_U+3/20<=t<=1`.
- Notch with endpoint enclosures `[a_L,a_U]`, `[b_L,b_U]`: `a_U<=t<=b_L`.

A point exactly at a mathematical boundary may instead be defined by that exact boundary expression. An outward enclosure of a boundary must not itself be mistaken for an interval all of whose points are inside the region. A legacy floating endpoint can land just outside the exact region; using the symbolic endpoint or an interior witness fixes that issue.

For every neighbor, establish either gate exclusion or an objective lower bound `J_neighbor_L>=J_inc_U`. A strict inequality proves the neighbor is strictly worse; equality still excludes strict descent. Overlapping score intervals are unresolved. Failure to prove a lower bound above the incumbent is not evidence of an improvement.

## 7. Neighborhood coverage and the strength of the possible conclusion

For the fixed labeled phase vector:

- Every one-coordinate alternative gives `16*63=1008` distinct vectors.
- Choosing two distinct coordinates with `i<j` and independently choosing each increment from `{-2,-1,+1,+2}` gives `choose(16,2)*4^2=1920` distinct vectors modulo 64.

Every pair move changes exactly two coordinates, so the two sets are disjoint; the specified union contains exactly **2928** vectors. This is a combinatorial verification of the intended neighborhood size, not a verification that the parent's output enumerates it correctly. Store or hash the canonical tuples and account for every tuple once. If phases are quotiented by a common-phase gauge, explain how coverage is preserved; the simple count above uses labeled vectors without such quotienting.

The supplied search summary is consistent arithmetically: `1508+1419+1=2928`, with 1420 neighbors left after the reported gate exclusions. I did not independently verify those classifications or rerun the search. The quoted borderline lower `0.034743757` exceeds the quoted incumbent upper `0.034733984` by about `9.773e-6`, but these rounded float64 numbers alone are not an exact-real certificate. The exact-integer run must recompute every exclusion or score comparison; historical sampled values can choose witnesses, not substitute for proof endpoints.

If all comparisons close, the justified conclusion is: **within this exact target/array model and this finite union of all single-coordinate alternatives and the specified small two-coordinate moves, no neighbor satisfying the pinned sufficient calibration gate has a strictly smaller continuous weighted score than the incumbent.**

This does not cover all two-coordinate changes, three-or-more-coordinate changes, global discrete optimality, other targets, other geometries, amplitude optimization, or the broader set of genuinely robust designs that the sufficient gate might reject. Certifying the objective exclusions for all gate-eligible neighbors does not require certifying those neighbors' beamwidth or pointing. However, calling the incumbent a fully certified feasible local optimum would additionally require its own beamwidth and pointing constraints to be certified; the repository explicitly labels those checks numerical. [Model feasibility and enclosure limits](../../docs/MODEL.md).

## 8. Independent arithmetic spot checks

I executed newly written, standard-library-only scratch arithmetic for the constants, threshold and fixed incumbent nominal power. It used rational Machin sums, integer floor/ceiling intervals at `10^50`, `isqrt`, and the stated degree-55 Taylor enclosure. It imported or executed **no repository module**, evaluated no neighborhood search, and computed no continuous peak grid. The following displayed endpoints were widened outward to 16 decimal places:

- `u0 in [0.1731500600699268, 0.1731500600699269]`.
- `sin(delta) in [0.0702927404556192, 0.0702927404556193]`.
- `cos(delta) in [0.9975264059859462, 0.9975264059859463]`.
- `T in [0.8966161368603160, 0.8966161368603161]`.
- `T+0.005 in [0.9016161368603160, 0.9016161368603161]`.
- Canonical incumbent `eta in [0.9016630555784458, 0.9016630555784459]`.

These spot checks establish agreement of the proposed formulas with the intended calibration margin and show a clear nominal incumbent margin even above the default slack floor. They are author-written arithmetic evidence under ordinary interpreter correctness assumptions, not a machine-checked proof or a review of the parent's code. They do not validate the 1508/1419/1 partition, minimum neighbor separation, or any new `J_inc_U`.

## 9. Primary-source support and review limits

The main mathematical references inspected were NIST DLMF's exact equations and hypotheses:

- [4.21.4](https://dlmf.nist.gov/4.21.E4): tangent addition, used in the explicit branch-checked Machin proof above.
- [4.24.3](https://dlmf.nist.gov/4.24.E3) and [4.23.3](https://dlmf.nist.gov/4.23.E3): arctangent series and integral, supporting the signed rational remainder derivation.
- [4.19.1–2](https://dlmf.nist.gov/4.19): sine and cosine series.
- [1.4.35–36](https://dlmf.nist.gov/1.4.vi): Taylor theorem and Lagrange remainder for sufficiently differentiable real functions.
- [3.3.5](https://dlmf.nist.gov/3.3.E5), [3.3.14](https://dlmf.nist.gov/3.3.E14), and [3.3.15](https://dlmf.nist.gov/3.3.E15): interpolation remainder, linear interpolant and the exact `1/8` constant.
- [4.21.2–3](https://dlmf.nist.gov/4.21): sine/cosine angle addition.

These sources support the classical identities and error theorems. They do not attest to this application, its interval implementation, the chosen truncation counts, or a completed optimization certificate. The array curvature, calibration inversion and finite-neighborhood conclusion are the explicit derivations in this report.

A historical primary-source lead is William Jones, *Synopsis Palmariorum Matheseos* (1706), page 263, with the Machin series and attribution: [digitized volume](https://archive.org/details/SynopsisPalmariorumMatheseosOrANewIntroductionToTheMathematics/page/n283/) and [page-excerpt catalog](https://commons.wikimedia.org/wiki/File:Synopsis_Palmariorum_Matheseos_pi.jpg). The catalog was accessible, but this run could not inspect the original page pixels or retrieve its OCR successfully. That historical lead is **not relied upon** as verified mathematical evidence here; the direct proof using DLMF identities supplies that evidence.

This was a same-model, fresh-context AI research sub-agent task, following the research skill under the user's explicit no-spawn restriction. I read `AGENTS.md`, `DISCOVERY.md`, `docs/MODEL.md`, `trial/MATH.md`, `trial/coherence.py`, and relevant static model/evaluator definitions and frozen input records. I did not inspect the parent's interval implementation. The provided search summary was context, not independently established evidence. Fresh context and independent algebra do not constitute an independent human or external expert review.

No upstream/source program was executed; no experiment was resumed; no agent was spawned; no post or PR was created; no repository file or accepted record was changed by this audit. The only intentionally written artifact is this report. No persistent supporting download was necessary. There is no independently verified whole-neighborhood certificate or global-optimum claim in this report.

## 10. Audited source fingerprints

The following SHA-256 fingerprints were read during this review; paths are relative to `repo/`:

```text
AGENTS.md
  9ecd1db9555a7c41639f6050493251a38ca0de4f7180b7b9763f4f59c3035e1d
docs/MODEL.md
  f758c42ebabbc6aa9a1b813fa56ba2ee6a162efab3d6c8c1cba28286e5200657
trial/MATH.md
  bb88157ed31e2fd5362501f80d38dce74c9a5484353fc6d9c4d17ca094a4d2f8
trial/coherence.py
  44bb43c778da86c99383b2752cd5fbc11733871dd70d87128154907b4231ecef
configs/experiment.json
  f4f2b1d0ba59c9f3fa39612ac00bebfcbc887a873a210c7b8e3d80806d7381aa
research/readiness-20261021/portfolio.json
  6f649596ce80bf423a102aee79d6aa236b70f20286bfffe5e1726f58aec7743b
research/readiness-20261021/fresh-08-calibration-margin.json
  3c5820c2d9960eefadf8b69f86ce197d9396bd2e934e4aaa7da6fe917c323080
```

