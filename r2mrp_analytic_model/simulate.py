#!/bin/env python3
"""Vectorized reimplementation of the R2MRP analytic recursion in main.py.

Only the 'log' radio model is implemented. The recursion, initial conditions,
sink handling and beta normalization are kept identical to main.py so results
match; numpy is used purely for speed.
"""
import argparse
import math
import numpy as np
import matplotlib.pyplot as plt


def build_coords(x, y, node, dist):
    coords = np.zeros((node, 2))
    for i in range(x):
        for j in range(y):
            idx = i * y + j
            if idx < node:
                coords[idx] = (i * dist, j * dist)
    return coords


def pairwise_dist(coords):
    diff = coords[:, None, :] - coords[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=2))


def pd_log(D, a, d0):
    z = a * (D - d0)
    z = np.clip(z, -700, 700)
    return 1.0 / (1.0 + np.exp(z))


def qos_pass(P, nt, tau):
    kmin = math.ceil(tau * nt)
    q = np.zeros_like(P)
    for k in range(kmin, nt + 1):
        q += math.comb(nt, k) * (P ** k) * ((1 - P) ** (nt - k))
    return q


def calc_alpha(coords, a, d0, nt, tau, iters, epsilon):
    n = coords.shape[0]
    D = pairwise_dist(coords)
    Pm = pd_log(D, a, d0)            # p(d_uv)  (== r)
    Bm = qos_pass(Pm, nt, tau) * Pm  # q(d_uv) * r(d_uv)

    p_sink = Pm[0, :].copy()         # p(d_vs)
    b_sink = Bm[0, :].copy()         # b_u = q(d_us) r(d_us)

    # k = 1 initial condition: alpha_{u,u} = b_u
    alpha_prev = np.zeros((n, n))
    for i in range(1, n):
        alpha_prev[i, i] = b_sink[i]
    beta = alpha_prev.copy()

    o_cumsum = np.zeros(n)
    o_cumsum[1:] = p_sink[1:]        # o_v^(1) = p(d_vs)

    for _k in range(2, iters):
        S = beta.sum(axis=1)         # sum_p beta[u,p]
        alpha_new = alpha_prev.copy()
        o_k = np.zeros(n)
        for v in range(1, n):
            # a_v^(k): at least one RINV received
            Mu = 1.0 - S * Pm[:, v]
            Mu[0] = 1.0
            Mu[v] = 1.0
            a_v = 1.0 - np.prod(Mu)
            o_v = (1.0 - o_cumsum[v]) * a_v
            o_k[v] = o_v
            # alpha update over all paths p
            G = 1.0 - beta * Bm[:, v][:, None]
            G[0, :] = 1.0
            G[v, :] = 1.0
            prodp = np.prod(G, axis=0)
            alpha_new[v, :] = (alpha_prev[v, :]
                               + o_v * (1.0 - alpha_prev[v, :]) * (1.0 - prodp))
        delta = alpha_new - alpha_prev
        m = delta.sum(axis=1, keepdims=True)
        beta = delta / (m + epsilon)
        alpha_prev = alpha_new
        o_cumsum = o_cumsum + o_k

    return alpha_prev, b_sink


def calc_lambda(alpha, b_sink):
    n = alpha.shape[0]
    lam = np.zeros(n)
    for v in range(1, n):
        lam[v] = float(np.dot(b_sink[1:], alpha[v, 1:]))
    return lam


def print_alpha_matrix(matrix):
    n = matrix.shape[0]
    row_hdr_w = len('Node {}'.format(n)) + 2
    col_w = max(len('Path {}'.format(n)), len('0.0000')) + 2
    header = ' ' * row_hdr_w + ''.join('Path {}'.format(p).rjust(col_w) for p in range(n))
    print(header)
    for v in range(n):
        row = 'Node {}'.format(v).ljust(row_hdr_w)
        row += ''.join('{:.4f}'.format(matrix[v, p]).rjust(col_w) for p in range(n))
        print(row)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--data', choices=['alpha', 'spof'], default='spof')
    ap.add_argument('-n', '--node', type=int, default=100)
    ap.add_argument('-x', type=int, default=10)
    ap.add_argument('-y', type=int, default=10)
    ap.add_argument('-gd', '--grid-distance', type=float, nargs='+', default=[20])
    ap.add_argument('-q', '--qos', type=float, default=0.6)
    ap.add_argument('-nt', type=int, default=10)
    ap.add_argument('-a', '--alpha', type=float, default=0.12)
    ap.add_argument('-rd', '--d0', type=float, default=45.0)
    ap.add_argument('-i', '--iter', type=int, default=30)
    ap.add_argument('-e', '--epsilon', type=float, default=1e-5)
    ap.add_argument('-o', '--out', default='spof_log.png')
    args = ap.parse_args()

    if args.data == 'alpha':
        coords = build_coords(args.x, args.y, args.node, args.grid_distance[0])
        alpha, _ = calc_alpha(coords, args.alpha, args.d0, args.nt, args.qos,
                              args.iter, args.epsilon)
        print_alpha_matrix(alpha)
    else:
        p_c0, p_c1, p_c2, e_c = [], [], [], []
        for gd in args.grid_distance:
            coords = build_coords(args.x, args.y, args.node, gd)
            alpha, b_sink = calc_alpha(coords, args.alpha, args.d0, args.nt,
                                       args.qos, args.iter, args.epsilon)
            lam = calc_lambda(alpha, b_sink)[1:]
            p_c0.append(np.mean(np.exp(-lam)))
            p_c1.append(np.mean(lam * np.exp(-lam)))
            p_c2.append(np.mean(1 - np.exp(-lam) * (1 + lam)))
            e_c.append(np.mean(lam))
            print(f'gd={gd:5.1f}  E[C]={e_c[-1]:.4f}  '
                  f'P(C=0)={p_c0[-1]:.4f}  P(C=1)={p_c1[-1]:.4f}  '
                  f'P(C>=2)={p_c2[-1]:.4f}')

        plt.figure(figsize=(8, 5))
        plt.plot(args.grid_distance, p_c0, marker='o', label='P(C=0)  outage')
        plt.plot(args.grid_distance, p_c1, marker='o', label='P(C=1)  SPOF')
        plt.plot(args.grid_distance, p_c2, marker='o', label='P(C>=2)  multipath')
        plt.xlabel('Grid distance [m]')
        plt.ylabel('Probability')
        plt.title(f'log radio  (a={args.alpha}, d50={args.d0}, tau={args.qos}, '
                  f'n={args.node}, K={args.iter})')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(args.out, dpi=120)
        print('saved', args.out)
