from ip_utils import *

controller_raw = ['10.107.8.70']

ctrl = handler_raw_list(controller_raw)

computer_raw = [
#'10.107.8.80-10.107.8.170:10'
'10.107.8.80',
'10.107.8.90-10.107.8.170:10',
'10.107.9.10-10.107.9.30:10',
'10.107.9.50',
'10.107.9.70-10.107.9.80:10',
#'10.107.8.120',
]

cpu = handler_raw_list(computer_raw)

cinder_raw = [
'10.107.10.10-10.107.10.20:10',
]

cinder = handler_raw_list(cinder_raw)
