#### Sentinel-Agent.py

import psutil
from collections import namedtuple
from os import system
import socket
from time import sleep
import datetime
import json

ram = namedtuple('ram','phys_total phys_free phys_percent swap_total swap_free swap_percent')
cpu = namedtuple('cpu','cpu_count cpu_percpu cpu_total')
disk = namedtuple('disk','disk_num disk_info')
data = {}


def get_cpu_percent():
	res = {}
	res_data = []
	agg = []
	agg_data = 0
	percpu = []
	cpup = 0
	cpu_count = len(psutil.cpu_percent(percpu=True))
	for i in range(cpu_count):
		res["cpu{0}".format(i)] = 0
	for i in range(5):
		percpu.append(psutil.cpu_percent(interval=0.5, percpu=True))
		agg.append(psutil.cpu_percent(interval=0.5))
	for i in range(5):
		for x in range(cpu_count):
			res["cpu{0}".format(x)] = res['cpu{0}'.format(x)] + percpu[i][x]
	for i in res:
		x = float(float(res[i])/5)
		res_data.append(str(round(x, 2)))
	for i in agg:
		agg_data = agg_data + i
	cpu_total = float(agg_data / 5)
	cpu_data = cpu(cpu_count, res_data, round(agg_data, 2))
	return cpu_data


def get_ram_usage():
	ramv = psutil.virtual_memory()
	rams = psutil.swap_memory()
	st = float((rams.total - ramv.total)/1073741824)
	sf = float((rams.free - ramv.available)/1073741824)
	sp = (st - sf) / st * 100
	pt = float(ramv.total/1073741824)
	pf = float(ramv.available/1073741824)
	usage = ram(round(pt,1), round(pf,2), ramv.percent, st, sf, round(sp, 2))
	return usage

def get_disk():
	usage = []
	disks = {}
	disk_num = 0
	drives = psutil.disk_partitions()
	num_disks = len(drives)
	for i in drives:
		dev = i.mountpoint
		d = psutil.disk_usage(dev)
		dt = float(d.total/1073741824)
		dt = round(dt, 2)
		df = float(d.free/1073741824)
		df = round(df, 2)
		du = float(d.used/1073741824)
		du = round(du, 2)
		dp = d.percent
		disks['disk{0}'.format(disk_num)] = {'dev': dev, 'disk_total':dt, 'disk_free':df, 'disk_used':du, 'disk_percent':dp}
		disk_num = disk_num + 1
	return disk(disk_num, disks)

def get_ip():
	ip = socket.gethostbyname(socket.gethostname())
	return ip

def write_data(cpu, ram, disk, ip):
	cpu_data = {}
	timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
	for i in range(cpu.cpu_count):
		cpu_data['cpu{0}'.format(i)] = cpu.cpu_percpu[i]

	data = {
	'ipaddr': ip,
	'timestamp': timestamp,
	'cpu': {
	'cpu_count': cpu.cpu_count,
	'cpu_total': cpu.cpu_total,
	'cpu_percpu': cpu_data
	},
	'ram': {
	'ram_phystotal': ram.phys_total,
	'ram_physfree': ram.phys_free,
	'ram_physpercent': ram.phys_percent,
	'ram_swaptotal': ram.swap_total,
	'ram_swapfree': ram.swap_free,
	'ram_swappercent': ram.swap_percent
	},
	'disk': {
	'disk_count': disk.disk_num,
	'disk_info': disk.disk_info
	}
	}
	r = open('data', 'w')
	json.dump(data, r)
	r.close()
	return 


if __name__ == '__main__':
	while True:
		c = get_cpu_percent()
		system('cls')
		print '# CPU/cores: ' + str(c.cpu_count)
		print 'CPU Load: ' + str(c.cpu_total) + "%"
		for i in range(c.cpu_count):
			print "cpu" + str(i) + ': ' + str(c.cpu_percpu[i]) + '%'
		print ' '
		r = get_ram_usage()
		pt = r.phys_total
		pf = r.phys_free
		pp = 100 - r.phys_percent
		print "RAM Total: " + str(round(pt,1)) + " GB"
		print "RAM Free: " + "%.2f" % pf  + " GB"
		print "RAM %: " + str(pp) + "%"
		print '----'
		print "SWAP Total: " + str(r.swap_total) + " GB"
		print "SWAP Free: " + str(r.swap_free) + " GB"
		print "SWAP %: " + str(r.swap_percent) + "%"
		print "----"
		d = get_disk()
		for i in range(d.disk_num):
			print 'Disk: ' + d.disk_info['disk{0}'.format(i)]['dev']
			print 'Disk Total: ' + str(d.disk_info['disk{0}'.format(i)]['disk_total']) + " GB"
			print 'Disk Used: ' + str(d.disk_info['disk{0}'.format(i)]['disk_used']) + " GB"
			print 'Disk Free: ' + str(d.disk_info['disk{0}'.format(i)]['disk_free']) + " GB"
			print "% Used: " + str(d.disk_info['disk{0}'.format(i)]['disk_percent']) + "%"
			print ' '
		print '----'
		ip = get_ip()
		print "IP Address: " + ip
		write_data(c, r, d, ip)
		sleep(5)
		