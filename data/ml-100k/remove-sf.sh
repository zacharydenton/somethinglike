#!/usr/bin/env bash
for user in $(grep '+b' /etc/vhosts | cut -d : -f 3 | sort | uniq)
do
    users_file="/usr/share/web/$user/users"
    if [ -f "$users_file" ]
    then
    for mail_account in $(grep -Eo "^\@\w+" $users_file | sed 's/\@//')
    do
        echo su "$user" -c vqsf-remove "$mail_account"
    done
    fi
done

