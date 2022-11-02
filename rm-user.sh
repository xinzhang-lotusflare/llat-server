#!/bin/bash

source env.sh
source ${UTIL_SH}

USER_EMAIL_ADDR=$1

rm() {
  echo $(log_date) - Remove WireGuard credential for user: $USER_EMAIL_ADDR
  USER_NAME=$(${PYTHON} ${GET_EMAIL_USERNAME_PY} ${USER_EMAIL_ADDR})

  mkdir -p ./${ACCOUNTS_STORAGE}/inactive

  if [[ -e ./${ACCOUNTS_STORAGE}/active/${USER_NAME}.csv ]]; then
    mv ./${ACCOUNTS_STORAGE}/active/${USER_NAME}.csv ./${ACCOUNTS_STORAGE}/inactive/${USER_NAME}_$(today).csv
  fi

  # Remove WireGuard config
  echo $(log_date) - Removing
  CLIENT_NAME=$(${PYTHON} ${GET_CLIENT_NAME_PY} ${USER_EMAIL_ADDR})
  sudo ${PYTHON} ${WG_PY} rm -c ${CLIENT_NAME} -s ${WG_SH}
}

rm
if [[ ! $? -eq 0 ]]; then
  echo $(log_date) - Fail to remove credential for user: ${USER_EMAIL_ADDR}
  exit 1
fi

echo $(log_date) - Removed
exit 0
