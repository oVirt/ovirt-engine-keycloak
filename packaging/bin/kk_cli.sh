#!/bin/sh

if [[ ! -z ${ADMIN_PASSWORD} ]]; then
  # handle kcadm config credentials
  ${KK_TOOL} $* --password $ADMIN_PASSWORD
elif [[ ! -z ${USER_NEW_PASSWORD} ]]; then
  # handle kcadm set-password for user
  ${KK_TOOL} $* --new-password $USER_NEW_PASSWORD
elif [[ !  -z ${CLIENT_SECRET} ]]; then
  # handle kcadm client create
  ${KK_TOOL} $* -s secret=$CLIENT_SECRET
else
  ${KK_TOOL} $*
fi

