#!/usr/bin/env bash

virsh net-define virbr1.xml
virsh net-autostart virbr1
virsh net-start virbr1
