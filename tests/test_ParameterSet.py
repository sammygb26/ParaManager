import paramanager as pm


def test_required_parameter():
    proto_parameters = [pm.ProtoParameter("required", 0.0, required=True)]
    ps = pm.ParameterSet(proto_parameters)
    try:
        ps.check_unset_parameters()
        assert False
    except ValueError:
        assert True

    try:
        ps.read_argv(args=[])
        assert False
    except ValueError:
        assert True

    try:
        ps.read_argv(args=["-required", "0.1"])
        assert True
    except ValueError:
        assert False
