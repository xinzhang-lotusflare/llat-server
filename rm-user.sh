#!/bin/bash

source env.sh
source ${UTIL_SH}

USER_EMAIL_ADDR=$1

rm() {
  echo $(log_date) - Removing WireGuard credential for user: $USER_EMAIL_ADDR
  USER_NAME=$(${PYTHON} ${GET_EMAIL_USERNAME_PY} ${USER_EMAIL_ADDR})

  mkdir -p ./${ACCOUNTS_STORAGE}/inactive

  if [[ -e ./${ACCOUNTS_STORAGE}/active/${USER_NAME}.csv ]]; then
    mv ./${ACCOUNTS_STORAGE}/active/${USER_NAME}.csv ./${ACCOUNTS_STORAGE}/inactive/${USER_NAME}_$(today).csv
  fi
}

rm
if [[ ! $? -eq 0 ]]; then
  echo $(log_date) - Fail to remove credential for user: ${USER_EMAIL_ADDR}
  exit 1
fi

echo $(log_date) - Removed
exit 0
