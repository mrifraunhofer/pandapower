"""
Test case from book "Power System State Estimation", p. 23ff.
@author: menke
"""
from pandapower.estimation.state_estimation import state_estimation, create_measurement
import pandapower as pp
import numpy as np
import pytest


def test_3bus():
    # S_ref = 1 MVA (PP standard)
    # V_ref = 1 kV
    # Z_ref = 1 Ohm

    # The example only had per unit values, but Pandapower expects kV, MVA, kW, kVar
    # Measurements should be in kW/kVar/A - Voltage in p.u.

    # 1. Create network
    net = pp.create_empty_network()
    pp.create_ext_grid(net, 0)
    pp.create_bus(net, name="bus1", vn_kv=1.)
    pp.create_bus(net, name="bus2", vn_kv=1.)
    pp.create_bus(net, name="bus3", vn_kv=1.)
    pp.create_bus(net, name="bus4", vn_kv=1., in_service=0)  # out-of-service bus test
    pp.create_line_from_parameters(net, 0, 1, 1, r_ohm_per_km=.01, x_ohm_per_km=.03, c_nf_per_km=0., imax_ka=1)
    pp.create_line_from_parameters(net, 0, 2, 1, r_ohm_per_km=.02, x_ohm_per_km=.05, c_nf_per_km=0., imax_ka=1)
    pp.create_line_from_parameters(net, 1, 2, 1, r_ohm_per_km=.03, x_ohm_per_km=.08, c_nf_per_km=0., imax_ka=1)

    create_measurement(net, "vbus_pu", 0, 1.006, .004)  # V at bus 1
    create_measurement(net, "vbus_pu", 1, .968, .004)   # V at bus 2

    create_measurement(net, "pbus_kw", 1, -501, 10)    # P at bus 2
    create_measurement(net, "qbus_kvar", 1, -286, 10)  # Q at bus 2

    create_measurement(net, "pline_kw", 0, 888, 8, line=0)    # Pline for line (bus 1 -> bus 2) at bus 1
    create_measurement(net, "pline_kw", 0, 1173, 8, line=1)   # Pline for line (bus 1 -> bus 3) at bus 1
    create_measurement(net, "qline_kvar", 0, 568, 8, line=0)  # Qline for line (bus 1 -> bus 2) at bus 1
    create_measurement(net, "qline_kvar", 0, 663, 8, line=1)  # Qline for line (bus 1 -> bus 3) at bus 1

    v_start = np.array([1.0, 1.0, 1.0, 0.])
    delta_start = np.array([0., 0., 0., 0.])

    # 2. Do state estimation
    wls = state_estimation()
    wls.set_grid(net)
    success = wls.estimate(v_start, delta_start)
    v_result = net.res_bus_est.vm_pu.values
    delta_result = net.res_bus_est.va_degree.values

    # 3. Print result
    print("Result:")
    print("V [p.u.]:")
    print(v_result)
    print(u"delta [°]:")
    print(delta_result)

    target_v = np.array([[0.9996, 0.9741, 0.9438, np.nan]])
    diff_v = target_v - v_result
    target_delta = np.array([[ 0., -1.2475, -2.7457, np.nan]])
    diff_delta = target_delta - delta_result

    assert success
    assert (np.nanmax(abs(diff_v)) < 1e-4)
    assert (np.nanmax(abs(diff_delta)) < 1e-4)

if __name__ == '__main__':
    pytest.main(['-xs', __file__])

