import json
import gvar as gv
import lsqfit
import numpy as np
import matplotlib.pyplot as plt
import sys

OUT_TO_FILE = True
if OUT_TO_FILE:
    sys.stdout = open("out.dat", "w")

ORDER = ["K", "D"]
m_q = [93, 11720] #MeV # P.A. Zyla et al. (Particle Data Group), Prog. Theor. Exp. Phys. 2020, 083C01 (2020)

def main():
    with open("input.json", "r") as f:
        datas = json.loads(f.read())
    
    for k, v in datas.items():
        datas[k] = make_gvar(v, ["E0", "a0"])
    
    E0s = {}
    # E0s is a dictionary of len2 arrays of gvars
    for k, v in datas.items():
        E0s[k] = v["E0"]
    
    fs = {}
    for k, v in datas.items():
        fs[k] = (m_q+v['mlms']*m_q[0]) * v['a0'] * np.sqrt(2 / v['E0']**3)

    compute_fit(datas, E0s)
    #compute_fit(datas, fs)
    
def compute_fit(datas, ys):
    fit = lsqfit.nonlinear_fit(data = (datas, ys), prior=build_prior(), fcn=model)
    
    print("=========")
    print_dict(fit.p)
    print(f"chi2={fit.chi2} dof={fit.dof} Q={fit.Q}")
    compare(fit.p, datas, ys)
    extrapolated_ys = model({"Extrapolated": {"a":0, "mlms":0}}, fit.p)
    print()
    print_dict(extrapolated_ys)
    print()


def build_prior():
    prior={}
    prior['A'] = [gv.gvar(500, 100), gv.gvar(2000, 600)]
    prior['cdelta'] = [gv.gvar(0, 1), gv.gvar(0, 1)]
    prior['ca2'] = [gv.gvar(0, 0.5), gv.gvar(0, 0.5)]
    return prior


def compare(params, datas, E0s):
    datas_pred = model(datas, params)
    print()
    print("Predicted values")
    print_dict(datas_pred)
    print()
    print("Original values")
    print_dict(E0s)

def print_dict(d):
    for k, v in d.items():
        print(f"{k} = {v}")

def model(datas, p):
    # Given parameters p, compute "y" values (masses) at the points in "datas"
    A = p['A']
    cdelta = p['cdelta']
    ca2 = p['ca2']
    
    out={}
    for k, data in datas.items():
        # k is the name of a dataset, data is the params ("x") for that dataset
        x = data['a']
        z = data['mlms']
        out[k]=A*(1+cdelta*z)*(1+ca2*x**2) # out[k] should be an array of size 2

    return out

def make_gvar(data, keys):
    # data is a dict{ **params, **keys}, where each key gives a dict of strings that are to be converted to an array of gvar
    out = {}
    for k, v in data.items():
        if k in keys:
            out[k] = []
            for gk in ORDER:
                # out[k] is a list of gvars in the order given by ORDER
                out[k].append(gv.gvar(v[gk]))
            out[k] = np.asarray(out[k])
        else:
            out[k] = np.asarray(v)
    return out

if __name__ == "__main__":
    main()