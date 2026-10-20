# Contributor reasoning: a useful robust gain margin

The starting pilot's nominal phase designs sometimes violate eta>=0.85 under small calibration errors. A generic bound on absolute field error is very loose for **coherent efficiency**, because it treats changes in amplitude and normalization independently. The appropriate quantity is the angle between normalized excitation vectors.

Let e be the desired-direction unit steering vector, z the normalized nominal excitation, and r=|e* z|=sqrt(eta). If normalized z' satisfies |z* z'| >= cos(epsilon), orthogonal decomposition and Cauchy–Schwarz give

|e* z'| >= max(0, r cos(epsilon) - sqrt(1-r^2) sin(epsilon)).

This is the cosine angle-addition formula. Apply it successively to phase/position perturbation and amplitude perturbation:

1. At desired u0, the combined per-element phase error is bounded by delta = 2 degrees + 2 pi |u0| (0.005). The inner product between the normalized original and phase-perturbed vectors has real part at least cos(delta), so the angle between their complex rays is at most delta.
2. Amplitudes a_i lie in [a,b]=[0.97,1.03]. Between equal-amplitude and amplitude-perturbed phase vectors, the inner product magnitude is mean(a)/sqrt(mean(a^2)). Since a_i^2 <= (a+b)a_i-ab, minimizing the resulting ratio over mean(a) in [a,b] gives mean(a)^2/mean(a^2) >= 4ab/(a+b)^2. Thus this second angle is at most asin((b-a)/(a+b))=asin(0.03).

Therefore every allowed error vector obeys

eta_perturbed >= cos^2( acos(sqrt(eta_nominal)) + delta + asin(0.03) )

when the total angle is below pi/2; otherwise use zero. This covers correlated/adversarial errors as well as independent random errors. It uses the original error box and actual perturbed excitation power in the efficiency denominator. It assumes the nominal unit-amplitude array-factor model, without coupling or embedded-element changes. It is not a sidelobe, beamwidth, pointing or hardware guarantee.

Invert this expression to choose the nominal gain constraint; add 0.005 absolute efficiency slack against numerical/quantization drift. This is an engineering bound assembled from elementary inequalities, not a claimed new theorem. Its implementation is float64, not formal interval arithmetic. Tests compare 24,000 random perturbations, numerical adversarial minimizations, the zero-error identity and the margin inversion.

# A second reasoning opportunity: quantization has a gauge

Adding a common phase alpha to every excitation leaves the continuous array power unchanged. Rounding phases to 6 bits breaks that invariance until alpha is itself a whole phase bin. Over one bin, each element crosses one rounding threshold. Checking the midpoint of each interval between thresholds enumerates at most N+1 rounding patterns; it costs O(N) evaluations rather than an arbitrary fine grid. The frozen implementation samples the open intervals; it does not separately enumerate isolated exact half-bin ties under NumPy’s round-to-even convention. Thus “exact” refers to enumerating these constant open-interval patterns, not a global optimum over all possible rounding conventions or arbitrary discrete phase assignments. This can recover performance otherwise lost when a continuous optimizer fixes one global phase and rounds only once. The contribution is using this established symmetry correctly, not claiming the symmetry is new.

# Coupled moves

For paired element positions +/-x, equal residual phases combine as 2 exp(i phi) cos(2 pi x (u-u0)). The power is symmetric about u0 before absolute phase quantization and domain clipping. Joint changes of mirrored elements can thus move both symmetric quiet sectors together; single-element moves may worsen one while helping the other. The trial tests equal and opposite pair steps in addition to single-element moves. These moves are a heuristic, not a theorem that the optimum must be symmetric.
