cat $1 | tr '\n' '\0' | xargs -0 -n1 ./publish_order.sh
