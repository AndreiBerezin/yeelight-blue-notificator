# yeelight-blue-notificator
yeelight blue notificator now in python for linux only

###for scan YeeLightBlue without root:
- 1) sudo apt-get install libcap2-bin
- 2) sudo setcap 'cap_net_raw,cap_net_admin+eip' \`which hcitool\`
- 3) sudo setcap 'cap_net_raw,cap_net_admin+eip' \`which hciconfig\`