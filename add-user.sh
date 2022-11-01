#!/bin/bash

source env.sh
source ${LOG_DATE_SH}

USER_EMAIL_ADDR=$1

create() {
  CLIENT_NAME=$(${PYTHON} ${GET_CLIENT_NAME_PY} ${USER_EMAIL_ADDR})
  echo $(log_date) - Creating WireGuard credential for client: $CLIENT_NAME

  if [[ ! -x ${WG_SH} ]]; then
    chmod u+x ${WG_SH}
  fi
  sudo ${PYTHON} ${WG_PY} add -c ${CLIENT_NAME} -s ${WG_SH}

  if [[ ! -e ${CLIENT_NAME}.conf ]]; then
    echo $(log_date) - WireGuard conf file is missing for user: ${USER_EMAIL_ADDR}
    exit 1
  fi

  echo ${CLIENT_NAME}.conf | grep "Address" >> ${CLIENT_NAME}.llat.conf
  echo ${CLIENT_NAME}.conf | grep "PrivateKey" >> ${CLIENT_NAME}.llat.conf
  echo ${CLIENT_NAME}.conf | grep "PublicKey" >> ${CLIENT_NAME}.llat.conf
  echo ${CLIENT_NAME}.conf | grep "PresharedKey" >> ${CLIENT_NAME}.llat.conf

  CLIENT_PEER_ADDR=$(echo ${CLIENT_NAME}.conf | grep "Address" | cut -d'=' f2)
  # TODO:
  ${PYTHON} ${PERSIST_PY} --operation create-new --user-email-addr ${USER_EMAIL_ADDR} --client-name ${CLIENT_NAME} --peer-addr ${CLIENT_PEER_ADDR}

  # TODO: send email to ${USER_EMAIL_ADDR} with attachment ${CLIENT_NAME}.llat.conf
}

create
if [[ ! $? -eq 0 ]]; then
  echo $(log_date) - Fail to create credential for user: ${USER_EMAIL_ADDR}
  exit 1
fi

exit 0
