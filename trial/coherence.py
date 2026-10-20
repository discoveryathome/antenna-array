"""Analytical coherence-angle bound for bounded calibration errors.

Unit-amplitude nominal phase-only arrays only. This bounds coherent efficiency,
not sidelobe levels, beamwidth or pointing. Real-arithmetic proof in MATH.md;
float64 implementation is author-checked, not formally verified.
"""
import math


def error_angle(u0,phase_deg=2.,position_lambda=.005,amplitude_fraction=.03):
    return math.radians(phase_deg)+2*math.pi*abs(u0)*position_lambda+math.asin(amplitude_fraction)


def efficiency_lower(nominal_eta,u0,phase_deg=2.,position_lambda=.005,amplitude_fraction=.03):
    angle=math.acos(math.sqrt(min(1.,max(0.,nominal_eta))))+error_angle(u0,phase_deg,position_lambda,amplitude_fraction)
    return 0. if angle>=math.pi/2 else math.cos(angle)**2


def required_nominal_eta(u0,minimum=.85,slack=.005):
    angle=math.acos(math.sqrt(minimum))-error_angle(u0)
    if angle<0:raise ValueError('error budget cannot meet requested efficiency by this bound')
    return min(1.,math.cos(angle)**2+slack)
