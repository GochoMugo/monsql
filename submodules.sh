#!/bin/bash
# prepare submodules for use


prepare_sqlstr() {
  echo "from sqlstr import *" >> monsql/sqlstr/__init__.py
}


# starting work
prepare_sqlstr
