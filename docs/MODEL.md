# Model and verification contract

## Physical scope

At f = 3 GHz, lambda = 299792458/f = 0.0999308193 m. There are N = 16 identical scalar isotropic elements with field pattern E_n(u)=1, along x, at x_n/lambda = (n-7.5)/2. Adjacent spacing is 0.5 lambda = 49.9654 mm; aperture is 7.5 lambda = 0.749481 m. Positions are fixed in synthesis. The phase-only feasible hardware set has a_n=1 and phi_n in {2 pi q/64 : q=0,...,63}. No amplitude optimization or geometry movement is allowed in this class. Optimizers search residual phases in a stated subset, then polish on the full discrete grid.

With u = sin(theta), theta measured from broadside in a meridional plane,

F(u) = E(u) / N sum_n a_n exp(i [2 pi x_n u + phi_n]),   P(u) = |F(u)|^2,

where x_n is in wavelengths. The time/sign convention is arbitrary but steering phi_n=-2 pi x_n u0 must make all terms coherent at u0. Fields are scalar and co-polarized. For receive operation the conjugate beamforming convention gives the same magnitude pattern under reciprocal ideal elements; this is not a noise or sensitivity model.

The full sphere is represented by u in [-1,1] because the model is axisymmetric about the array axis. A linear array makes cones of equal response, not a unique 3D pencil beam. Both front and back copies are shown in full polar cuts. No ground plane, polarization loss, mutual coupling, mismatch, feed loss, finite range, amplifier compression, bandwidth, structural scattering, or embedded-element patterns are modeled. Radiation efficiency and hardware EIRP are **not** inferred. Far-field use is an assumption, not a measured operating range.

## Target and scoring

Each target supplies steering angle theta0 and one or two protected angular sectors (endpoints included). The main-beam exclusion interval is fixed to |u-u0|<0.15. The sidelobe metric is explicitly the maximum outside this interval, normalized to desired-direction power P0=P(u0). It is a **fixed-mask peak sidelobe** metric, not the maximum outside data-dependent first nulls. The latter would reward widening the main beam. Protected sectors are subsets of the sidelobe region.

Minimize J=max(max_side P/P0, 16 max_notch P/P0). The protected-sector power receives 12.0412 dB more weight. This objective seeks sector rejection while controlling other sidelobes; it is not unweighted global sidelobe minimization. Lower J is better, subject to:

* coherent efficiency eta=|sum a_n exp(i[2 pi x_n u0+phi_n])|^2/(N sum a_n^2) >= 0.85;
* half-power beamwidth <=0.14 in u;
* pointing error |u_peak-u0|<=0.015.

For phase-only candidates eta=P0. Continuous SLSQP imposes the efficiency inequality; discrete search uses a strong deficit penalty. The evaluator checks **all** constraints independently, so an optimizer penalty never establishes feasibility. Width and pointing are numerical root/peak measurements, not formally certified. Seeds which fail the checks remain in the record and must not enter the feasible frontier.

Half-power width is the distance between the nearest half-main-peak crossings enclosing the strongest peak in the main exclusion interval. We also report that width in degrees, coherent efficiency, target directivity D0=2P0/integral_-1^1 P du, and main-region power fraction integral_(u0-.15)^(u0+.15) P du / integral_-1^1 P du. The integrals use the analytic pairwise sinc formula. Coherent efficiency is an array combining/taper metric; it is not RF radiation efficiency. All methods use the same total excitation sum a_n^2=N. The Chebyshev reference uses continuously variable positive amplitudes and continuous steering phases; it is explicitly outside the phase-only hardware class.

## Peaks between samples

The optimizer uses independent uniform-u grids on each interval at nominal density 513 points across [-1,1], with at least 17 points per sector. The authoritative verifier uses density 10007 and always includes interval endpoints. It separately computes real cosine/sine sums rather than using the optimization matrix implementation.

For P(u)=N^-2 sum_ij a_i a_j cos(2 pi (x_i-x_j)u+phi_i-phi_j),

B2 = N^-2 sum_ij |a_i a_j| [2 pi (x_i-x_j)]^2 >= sup_u |P''(u)|.

On each adjacent sample interval of length h, linear interpolation differs from P by at most B2 h^2/8. Therefore

max_samples P <= max_continuous P <= max_samples P + B2 h^2/8.

We take the maximum of these bounds across each region. Each candidate reports lower and upper dB values; comparisons use upper bounds and an improvement is established only when candidate upper < baseline lower. This prevents a grid-missed peak from being called a gain. The curvature enclosure is mathematically valid in exact arithmetic; its implementation uses float64 and adds 1e-12 to the upper bound. The padding is not a proof of rounding error. These results are author-checked numerical simulation evidence, **not formal certificates or directed-rounding interval arithmetic**. Tests compare adversarial coarse sampling and a distinct much denser grid. Strengthening rounding control is a catalog task.

## Robustness scope

For the predetermined seed-1729 representative of each method, evaluate 64 common perturbation realizations for each of four scenarios: independent uniform phase errors +/-2 degrees; along-array position errors +/-0.005 lambda (about 0.50 mm); relative amplitude errors +/-3%; all three simultaneously. Errors are applied after phase quantization without recalibration. Each realization uses a density-2049 verification grid with the same curvature upper bound computed for perturbed positions/amplitudes. These are bounded-error stress scenarios, not measured fabrication statistics. Empirical 95th percentiles and feasible counts have no population confidence guarantee.

A separate worst-case bound covers **every** error vector in the stated box. Let delta=2 degrees + 2 pi*0.005, amax=0.03. For every u in [-1,1],

|F_perturbed-F_nominal| <= epsilon = (sum |a_n|/N) [amax+2 sin(delta/2)].

This follows by adding amplitude error and unit-phasor rotation error. Thus desired field is at least max(0,sqrt(P0)-epsilon), and any off-target peak field is at most sqrt(P_peak_upper)+epsilon. Their squared ratio bounds perturbed sidelobes and protected-sector peaks. This bound may be loose and makes no beamwidth or pointing guarantee. It does not model coupling or element-pattern errors.
