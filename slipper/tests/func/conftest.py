# coding=utf-8

import pytest

import os
import signal
import subprocess
import shlex
import copy

import logging


def getstatusoutput(cmd, env=None):
    """Return (status, output) of executing cmd in a shell.
       This new implementation should work on all platforms."""

    if env is not None:
        osenv = copy.deepcopy(os.environ)
        osenv.update({k: str(env[k]) for k in env})
        env = osenv

    pipe = subprocess.Popen(cmd,
                            env=env,
                            stdout=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True,
                            preexec_fn=os.setsid)
    sts = pipe.returncode
    output = "".join(pipe.stdout.readlines())
    if sts is None:
        sts = 0
    return pipe, sts, output


def _app_fixture(request, cmd, env=None):
    pipe, status, output = getstatusoutput('%s 1>&2 &' % cmd, env)
    if status:
        pytest.fail(output)

    def fin():
        os.killpg(pipe.pid, signal.SIGTERM)

    request.addfinalizer(fin)


@pytest.mark.tryfirst
@pytest.fixture(scope='session')
def slipper_instances(request):
    cmd = 'slipper-serve'


    _app_fixture(request, cmd, env={
        'SLIPPER_HTTP_PORT': 9001
    })

    # print request.config.getoption('--slipper-instances')
    # return request.config.getoption('--slipper-instances')
