from eucadeploy.componentdeployer import ComponentDeployer


def test_constructor():
    component_deployer = ComponentDeployer('foobar', 'etc/environment.yml',
                                           'etc/environment.yml')