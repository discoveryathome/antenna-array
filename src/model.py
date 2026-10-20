"""Optimization-side model. All lengths in wavelengths; angles represented by u=sin(theta)."""
import numpy as np


def positions(n=16, spacing=0.5):
    return spacing * (np.arange(n) - (n - 1) / 2)


def steering(x, u0):
    return -2 * np.pi * np.asarray(x) * u0


def quantize(phi, bits=6):
    step = 2 * np.pi / (2**bits)
    return (np.floor(np.asarray(phi) / step + 0.5).astype(int) % (2**bits)) * step


def power(u, x, phi, amplitude=None):
    x, phi = np.asarray(x), np.asarray(phi)
    a = np.ones(len(x)) if amplitude is None else np.asarray(amplitude)
    f = np.exp(2j * np.pi * np.outer(np.atleast_1d(u), x)) @ (a * np.exp(1j * phi)) / len(x)
    return abs(f)**2


def regions(target, guard):
    u0 = np.sin(np.deg2rad(target['steer_deg']))
    side = [(-1., u0 - guard), (u0 + guard, 1.)]
    notch = [tuple(np.sin(np.deg2rad(v))) for v in target['notches_deg']]
    return float(u0), side, notch


class Objective:
    """Minimax weighted off-target power normalized to desired-direction power.

    For discrete search, penalize coherent gain loss.
    Continuous SLSQP uses an explicit gain constraint instead.
    Beamwidth and pointing are checked by the independent evaluator.
    """
    def __init__(self, cfg, target):
        self.cfg = cfg
        self.x = positions(cfg['element_count'], cfg['spacing_wavelengths'])
        self.u0, side, notch = regions(target, cfg['guard_u'])
        us, weights = [], []
        for segments, weight in [(side, 1.), (notch, cfg['notch_weight_power'])]:
            for a,b in segments:
                n = max(17, int(np.ceil((b-a) * (cfg['optimizer_grid_n']-1)/2))+1)
                us.extend(np.linspace(a,b,n)); weights.extend([weight]*n)
        self.u = np.array(us)
        self.weight = np.array(weights)
        self.A = np.exp(2j*np.pi*np.outer(self.u, self.x))/len(self.x)
        self.a0 = np.exp(2j*np.pi*self.u0*self.x)/len(self.x)
        self.calls = 0

    def values(self, phi, jac=False):
        self.calls += 1
        w = np.exp(1j*phi)
        z = self.A*w[None,:]
        f = z.sum(axis=1)
        z0 = self.a0*w
        f0 = z0.sum()
        p0 = float(abs(f0)**2)
        p = abs(f)**2
        if not jac:
            return p, p0
        dp = -2*np.imag(np.conj(f[:,None])*z)
        dp0 = -2*np.imag(np.conj(f0)*z0)
        return p,p0,dp,dp0

    def score(self, phi):
        p,p0 = self.values(phi)
        ratio = float(np.max(self.weight*p)/max(p0,1e-12))
        return ratio + 100*max(0,self.cfg['minimum_coherent_efficiency']-p0)

    def score_batch(self, phis):
        self.calls += len(phis)
        w = np.exp(1j*np.asarray(phis))
        f = w @ self.A.T
        p0 = abs(w @ self.a0)**2
        ratios = np.max(abs(f)**2*self.weight,axis=1)/np.maximum(p0,1e-12)
        return ratios + 100*np.maximum(0,self.cfg['minimum_coherent_efficiency']-p0)
