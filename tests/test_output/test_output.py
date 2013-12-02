#!/usr/bin/env python

import os
from subprocess import Popen, STDOUT, PIPE, call
import filecmp
from nose_mpi import NoseMPI
import glob

pwd = os.path.dirname(__file__)

def setup(): 
    os.putenv('PWD', pwd)
    os.chdir(pwd)

def test_run():
    openmc_path = pwd + '/../../src/openmc'
    if int(NoseMPI.mpi_np) > 0:
        proc = Popen([NoseMPI.mpi_exec, '-np', NoseMPI.mpi_np, openmc_path],
               stderr=STDOUT, stdout=PIPE)
    else:
        proc = Popen([openmc_path], stderr=STDOUT, stdout=PIPE)
    print(proc.communicate()[0])
    returncode = proc.returncode
    assert returncode == 0

def test_summary_exists():
    summary = glob.glob(pwd + '/summary.*')
    assert len(summary) == 1
    assert summary[0].endswith('out') or summary[0].endswith('h5')

def test_cross_sections_exists():
    assert os.path.exists(pwd + '/cross_sections.out')

def test_statepoint_exists():
    statepoint = glob.glob(pwd + '/statepoint.10.*')
    assert len(statepoint) == 1
    assert statepoint[0].endswith('binary') or statepoint[0].endswith('h5')

def test_results():
    statepoint = glob.glob(pwd + '/statepoint.10.*')
    call(['python', 'results.py', statepoint[0]])
    compare = filecmp.cmp('results_test.dat', 'results_true.dat')
    if not compare:
      os.rename('results_test.dat', 'results_error.dat')
    assert compare

def teardown():
    output = glob.glob(pwd + '/statepoint.10.*') + glob.glob(pwd + '/summary.*')
    output.append(pwd + '/summary.out')
    output.append(pwd + '/cross_sections.out')
    output.append(pwd + '/results_test.dat')
    for f in output:
        if os.path.exists(f):
            os.remove(f)