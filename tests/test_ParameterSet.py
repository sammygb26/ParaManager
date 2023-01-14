import paramanager as pm
import pytest


def test_required_parameter():
    proto_parameters = [pm.ProtoParameter("required", 0.0, required=True)]
    ps = pm.ParameterSet(proto_parameters)

    with pytest.raises(ValueError):
        ps.check_unset_parameters()

    with pytest.raises(ValueError):
        ps.read_argv(args=[])

    with pytest.raises(ValueError):
        ps.read_argv(args=["-required", "is_not_float"])

    ps.read_argv(args=[], check_unset_parameters=False)
    ps.read_argv(args=["-required", "0.0"])
