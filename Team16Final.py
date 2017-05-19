from itertools import repeat
import json
import requests
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
import smtplib
from email.mime.text import MIMEText
import time

def check_response_code(rcode, expected):
  if rcode == expected:
    return True
  else:
    return False

# SEND SMTP
def smtp_send(subject, body):
  gmail_user =  'NutanixTS2017@gmail.com' # 'TechSummitTest@gmail.com'
  gmail_pwd =  'nutanix/4u' # 'TechSummitTest1'
  FROM =  'nutanixts2017@gmail.com' # 'TechSummitTest@gmail.com'
  TO = ['e2t2p0m5a0d2u2i3@nutanix.slack.com','9496777440@tmomail.net']
  SUBJECT = subject
  TEXT = body
  msg = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, TO, SUBJECT, TEXT)
  server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
  server.ehlo()
  server.login(gmail_user, gmail_pwd)
  server.sendmail(FROM, TO, msg)
  server.close()

# CHANGE CLUSTER IP
def change_cluster_ip():
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/cluster/"
  r = requests.get(uri, auth=('admin', 'nutanix/4u'), verify=False)
  r = json.loads(r.content)
#  print(json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')))
  cname = r['name']
  dsip = r['cluster_external_data_services_ipaddress']
  cip = raw_input("What is the Cluster IP: ")
  if cip <> "":
    data = {'name':cname, 'cluster_external_ipaddress': cip, 'cluster_external_data_services_ipaddress':dsip}
    r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
    if check_response_code(r.status_code, 200):
      print("\r\n*************************************\r\n* Successfully Processed Cluster IP *\r\n*************************************\r\n")
      smtp_send("Notification: Cluster " + cname + " IP Add/Change", "Cluster " + cname + " IP set to: " + cip)
      time.sleep(10)
    else:
      print("Status Code: %s - Response: %s" % (r.status_code,r.content))
  else:
    err("You must supply a Data Services IP!")

# CHANGE DATA SERVICES IP
def change_ds_ip():
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/cluster/"
  r = requests.get(uri, auth=('admin', 'nutanix/4u'), verify=False)
  r = json.loads(r.content)
#  print(json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')))
  cname = r['name']
  cip = r['cluster_external_ipaddress']
  dsip = raw_input("What is the Data Services IP: ")
  if dsip <> "":
    data = {'name':cname, 'cluster_external_ipaddress': cip, 'cluster_external_data_services_ipaddress':dsip}
    r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
    if check_response_code(r.status_code, 200):
      print("\r\n********************************\r\n* Successfully Processed DS IP *\r\n********************************\r\n")
      smtp_send("Notification: Cluster " + cname + " Data Services IP Add/Change", "Cluster " + cname + " Data Services IP set to: " + dsip)
      time.sleep(10)
    else:
      print("Status Code: %s - Response: %s" % (r.status_code,r.content))
  else:
    err("You must supply a Data Services IP!")    

# LIST VLAN
def vlan_list():
  i = 0
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/networks/"
  r = requests.get(uri, auth=('admin', 'nutanix/4u'), verify=False)
  r = json.loads(r.content)
  print("\r\n# - Name - ID - UUID")
  for e in r['entities']:
    i += 1
    print("%d - %s - %d - %s" % (i, e['name'], e['vlan_id'], e['uuid']))
  print("\r\n")
#  print(json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')))

# CREATE VLAN
def vlan_create():
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/networks/"
  vname = raw_input("What is the VLAN name: ")
  vid = raw_input("What is the VLAN ID: ")
  if vname <> "" and vid <> "":
    data = {'name':vname, 'vlan_id':vid}
    r = requests.post(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
    if check_response_code(r.status_code, 201):
      print("\r\n******************************\r\n* Successfully Added Network *\r\n******************************\r\n")
      smtp_send("Notification: VLAN Name - " + vname + " : VLAN ID - " + vid + " created", "VLAN Name - " + vname + " : VLAN ID - " + vid + " created")
    else:
      print("Status Code: %s - Response: %s" % (r.status_code,r.content))
  else:
    err("You must supply a Data Services IP!")

# GET ALL VMS
def vm_list():
  i = j = 0
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v1/vms/"
  r = requests.get(uri, auth=('admin', 'nutanix/4u'), verify=False)
  r = json.loads(r.content)
#  print(json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')))
  print("\r\n# - Name - UUID - IP Addresses (if any)")
  for e in r['entities']:
    i += 1
    if len(e['ipAddresses']) == 0:
      print("%d - %s - %s - %s" % (i,e['vmName'],e['uuid'],'None'))
    else:
      for ipAddress in e['ipAddresses']:
        j += 1
      if j > 0:
        print("%d - %s - %s - %s" % (i,e['vmName'],e['uuid'],','.join(e['ipAddresses'])))
  print("\r\n")

# CREATE A VM
def vm_create():
  os = raw_input("Do you want to create a Windows (1) or a Linux (2) VM?: ")
  if os == "1":
    vm_create_windows()
  elif os == "2":
    vm_create_linux()
  else:
    err("You must specify a 1 or a 2 for Windows or Linux")

# CREATE A WINDOWS VM
def vm_create_windows():
  print("Create a Windows VM")
  name = raw_input("Please enter the name of the Windows VM: ")
  desc = raw_input("Please enter the description of the Windows VM (optional): ")
  if name <> "":
    data = {'description':desc, 'guest_os':'string', 'memory_mb':2048, 'name':name, 'num_cores_per_vcpu':2, 'num_vcpus':1, 'vm_disks':[{ 'disk_address':{ 'device_bus':'ide', 'device_index':0 }, 'is_cdrom':True, 'is_empty':False, 'vm_disk_clone':{ 'disk_address':{ 'vmdisk_uuid':'ce671e05-687b-41f2-ac3a-92d8309511d6' } } }, {'disk_address':{ 'device_bus':'scsi', 'device_index':0 }, 'vm_disk_create':{ 'storage_container_uuid':'260f636a-319e-4222-a194-0fba0f637ca1', 'size':10737418240 } }, { 'disk_address':{ 'device_bus':'ide', 'device_index':1 }, 'is_cdrom':True, 'is_empty':False, 'vm_disk_clone':{ 'disk_address':{ 'vmdisk_uuid':'a66802d3-a57f-407c-b37f-f85a188f039c' } } }],'vm_nics':[{'network_uuid':'bb5a6857-d1fa-43cd-a27f-794efa92ba52'}], 'hypervisor_type':'ACROPOLIS', 'affinity':None }
    uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/vms/"
    r = requests.post(uri, auth=('admin','nutanix/4u'), verify=False, data=json.dumps(data))
    if check_response_code(r.status_code, 201):
      print("\r\n***************************\r\n* Successfully created VM *\r\n***************************\r\n")
      time.sleep(5)
      smtp_send("Notification: Windoze VM " + name + " Created", "Windoze VM " + name + " Created")
    else:
      print("Status Code: %s - Response: %s" % (r.status_code,r.content))
  else:
    err("You must supply a VM name!")

# CREATE LINUX VMs
def vm_create_linux():
  print("Create Linux VM")
  numvm = int(raw_input("How many Linux VMs (1-10)?"))
  base_name = raw_input("Please enter the base name of the Linux VMs: ")
  desc = raw_input("Please enter the description of the Linux VM (optional): ")
  if base_name <> "" and numvm > 0 and numvm <= 10:
    for x in range(1,numvm+1):
      bname = base_name+"-"+str(x)
      
      dataold = {'description':desc, 'guest_os':'string', 'memory_mb':512, 'name':bname, 'num_cores_per_vcpu':1, 'num_vcpus':1, 'vm_disks':[{ 'disk_address':{ 'device_bus':'ide', 'device_index':0 }, 'is_cdrom':True, 'is_empty':True }, {'disk_address':{ 'device_bus':'scsi', 'device_index':0 }, 'vm_disk_clone':{ 'disk_address':{ 'vmdisk_uuid': 'a57d6de6-9775-4570-9915-9e8cdf1234c1' } } }],'vm_nics':[{'network_uuid':'bb5a6857-d1fa-43cd-a27f-794efa92ba52'}],'vm_customization_config':{'fresh_install':True,'userdata':'package_upgrade: true'},'hypervisor_type':'ACROPOLIS', 'affinity':None }
      
      datacirros = {'description':desc, 'guest_os':'string', 'memory_mb':512, 'name':bname, 'num_cores_per_vcpu':1, 'num_vcpus':1, 'vm_disks':[{ 'disk_address':{ 'device_bus':'ide', 'device_index':0 }, 'is_cdrom':True, 'is_empty':True }, {'disk_address':{ 'device_bus':'scsi', 'device_index':0 }, 'vm_disk_clone':{ 'disk_address':{ 'vmdisk_uuid': '2c5b6e94-ea24-40b7-b0fc-193708d612ad' } } }],'vm_nics':[{'network_uuid':'bb5a6857-d1fa-43cd-a27f-794efa92ba52'}],'vm_customization_config':{'fresh_install':True,'userdata':'package_upgrade: true'},'hypervisor_type':'ACROPOLIS', 'affinity':None }
      
      data_centos6 = { 'description':desc, 'guest_os':'string', 'memory_mb':512, 'name':bname, 'num_cores_per_vcpu':1, 'num_vcpus':1, 'vm_disks':[{'disk_address':{ 'device_bus':'scsi', 'device_index':0 }, 'vm_disk_clone':{ 'disk_address':{ 'vmdisk_uuid': '9c08a056-189b-4e91-9685-80a2c2dc5c50' } } }],'vm_nics':[{'network_uuid':'bb5a6857-d1fa-43cd-a27f-794efa92ba52'}],'vm_customization_config':{'fresh_install':True,'userdata':'package_upgrade: true'},'hypervisor_type':'ACROPOLIS', 'affinity':None }
      
      data_centos7_ks = { 'description':desc, 'guest_os':'string', 'memory_mb':512, 'name':bname, 'num_cores_per_vcpu':1, 'num_vcpus':1, 'vm_disks':[{ 'disk_address':{ 'device_bus':'ide', 'device_index':0 }, 'is_cdrom':True, 'is_empty':False, 'vm_disk_clone':{ 'disk_address':{ 'vmdisk_uuid':'b5d2689e-319a-4700-9dc6-5b5b5e7eea27' } } },{'disk_address':{ 'device_bus':'scsi', 'device_index':0 }, 'vm_disk_create':{ 'storage_container_uuid':'260f636a-319e-4222-a194-0fba0f637ca1', 'size':10737418240 } }],'vm_nics':[{'network_uuid':'bb5a6857-d1fa-43cd-a27f-794efa92ba52'}],'vm_customization_config':{'fresh_install':True,'userdata':'package_upgrade: true'},'hypervisor_type':'ACROPOLIS', 'affinity':None }
      
      uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/vms/"
      r = requests.post(uri, auth=('admin','nutanix/4u'), verify=False, data=json.dumps(data_centos7_ks))
      if check_response_code(r.status_code, 201):
        print("\r\n*********************************\r\n* Successfully created Linux VM *\r\n*********************************\r\n")
        time.sleep(5)
        smtp_send("Notification: Linux VM " + bname + " Created", "Linux VM " + bname + " Created")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
  else:
    err("You must supply a VM name!")    

# GET VMs AND PRESENT TO USER TO CHOOSE WHICH TO OPERATE ON AND WHICH OPERATION TO CARRY OUT
def vm_operations():
  i = 0
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/vms/"
  r = requests.get(uri, auth=('admin', 'nutanix/4u'), verify=False)
  r = json.loads(r.content)
  print("\r\n# - Name - UUID")
#  print(r['entities'])
  for e in r['entities']:
    i += 1
    print("%d - %s - %s" % (i,e['name'],e['uuid']))
  print("\r\n")
  answer = raw_input("Please enter the number of the VM you'd like to power on/off or delete: ")
  if answer <> "":
    answer = int(answer)
    if answer > i:
      err("Bad entry! There are only %d VMs" % (i))
      main()
    uuid = r['entities'][answer-1]['uuid']
    vname = r['entities'][answer-1]['name']
    print("Available operations: 1 (power on), 2 (power off), 3 (delete)")
    op = raw_input("Please enter the operation you'd like to perform on the VM: ")
    uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/vms/" + uuid
    if op == "1":
      uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/vms/" + uuid + "/set_power_state/"
      data = {'uuid':uuid,'transition':'ON'}
      r = requests.post(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 201):
        print("\r\n******************************\r\n* Successfully Powered ON VM *\r\n******************************\r\n")
        smtp_send("Notification: " + vname + " Powered On", vname + " Powered On")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
    elif op == "2":
      uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/vms/" + uuid + "/set_power_state/"
      data = {'uuid':uuid,'transition':'OFF'}
      r = requests.post(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 201):
        print("\r\n*******************************\r\n* Successfully Powered OFF VM *\r\n*******************************\r\n")
        smtp_send("Notification: " + vname + " Powered Off", vname + " Powered Off")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
    elif op == "3":
      data = {'uuid':uuid,'delete_snapshots':True}
      r = requests.delete(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 201):
        print("\r\n***************************\r\n* Successfully Deleted VM *\r\n***************************\r\n")
        smtp_send("Notification: " + vname + " Deleted", vname + " Deleted")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
  else:
    err("You have to enter a valid number associated with the VM")

# GET IMAGES
def images_list():
  i = 0
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/images/"
  r = requests.get(uri, auth=('admin', 'nutanix/4u'), verify=False)
  r = json.loads(r.content)
  print("\r\n# - Name - Type - State - UUID - Disk ID")
  for e in r['entities']:
    i += 1
    print("%d - %s - %s - %s - %s - %s" % (i, e['name'], e['image_type'], e['image_state'], e['uuid'], e['vm_disk_id']))
#  print(json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')))
  print("\r\n")

# GET STORAGE CONTAINERS
def container_list():
  i = 0
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/storage_containers/"
  r = requests.get(uri, auth=('admin', 'nutanix/4u'), verify=False)
  r = json.loads(r.content)
#  print(json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')))
  print("\r\n# - Name - UUID - Compression - Cache Dedup - Capacity Dedup - ECX")
  for e in r['entities']:
    i += 1
    print("%d - %s - %s - %s - %s - %s - %s" % (i, e['name'],e['storage_container_uuid'],e['compression_enabled'],e['finger_print_on_write'],e['on_disk_dedup'],e['erasure_code']))
  print("\r\n")

# MODIFY STORAGE CONTAINERS
def container_modify():
  i = 0
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/storage_containers/"
  r = requests.get(uri, auth=('admin', 'nutanix/4u'), verify=False)
  r = json.loads(r.content)
#  print(json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')))
  print("\r\n# - Name - UUID - Compression - Cache Dedup - Capacity Dedup - EC-X")
  for e in r['entities']:
    i += 1
    print("%d - %s - %s - %s - %s - %s" % (i,e['name'],e['storage_container_uuid'],e['compression_enabled'],e['finger_print_on_write'],e['on_disk_dedup']))
  print("\r\n")
  
  answer = raw_input("Please enter # of Container to modify: ")
  if answer <> "":
    answer = int(answer)
    if answer > i:
      err("Bad entry! There are only %d Containers" % (i))
      main()
    cname = r['entities'][answer-1]['name']
    print(cname)
    print("Available operations:\r\n 1. Enable Compression\r\n 2. Enable Cache Dedup\r\n 3. Enable Capacity Dedup\r\n 4. Enable Erasure Coding (EC-X)\r\n 5. Disable Compression\r\n 6. Disable Cache Dedup\r\n 7. Disable Capacity Dedup\r\n 8. Disable Erasure Coding (EC-X)")
    op = raw_input("Please enter the operation # you'd like to perform on the Container: ")
    if op == "1":
      data = {'storage_container_uuid':r['entities'][answer-1]['storage_container_uuid'],'name':r['entities'][answer-1]['name'],'compression_enabled':True,'finger_print_on_write':'off'}
      r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 200):
        print("\r\n************************************\r\n* Successfully Enabled Compression *\r\n************************************\r\n")
        smtp_send("Notification: Container " + cname + " Compression Enabled", "Container " + cname + " Compression Enabled")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
    elif op == "2":
      data = {'storage_container_uuid':r['entities'][answer-1]['storage_container_uuid'],'name':r['entities'][answer-1]['name'],'finger_print_on_write':'on'}
      r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 200):
        print("\r\n*************************************\r\n* Successfully Enabled Cache Dedup *\r\n*************************************\r\n")
        smtp_send("Notification: Container " + cname + " Cache Dedup Enabled", "Container " + cname + " Cache Dedup Enabled")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
    elif op == "3":
      data = {'storage_container_uuid':r['entities'][answer-1]['storage_container_uuid'],'name':r['entities'][answer-1]['name'],'on_disk_dedup':'POST_PROCESS','finger_print_on_write':'off'}
      r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 200):
        print("\r\n**************************************\r\n* Successfully Enabled Capacity Dedup *\r\n**************************************\r\n")
        smtp_send("Notification: Container " + cname + " Capacity Dedup Enabled", "Container " + cname + " Capacity Dedup Enabled")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
    elif op == "4":
      data = {'storage_container_uuid':r['entities'][answer-1]['storage_container_uuid'],'name':r['entities'][answer-1]['name'],'erasure_code':'on','finger_print_on_write':'off'}
      r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 200):
        print("\r\n***************************************\r\n* Successfully Enabled Erasure Coding *\r\n***************************************\r\n")
        smtp_send("Notification: Container " + cname + " Erasure Coding Enabled", "Container " + cname + " Erasure Coding Enabled")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
    if op == "5":
      data = {'storage_container_uuid':r['entities'][answer-1]['storage_container_uuid'],'name':r['entities'][answer-1]['name'],'compression_enabled':False,'finger_print_on_write':'off'}
      r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 200):
        print("\r\n*************************************\r\n* Successfully Disabled Compression *\r\n*************************************\r\n")
        smtp_send("Notification: Container " + cname + " Compression Disabled", "Container " + cname + " Compression Disabled")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
    elif op == "6":
      data = {'storage_container_uuid':r['entities'][answer-1]['storage_container_uuid'],'name':r['entities'][answer-1]['name'],'finger_print_on_write':'off'}
      r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 200):
        print("\r\n*************************************\r\n* Successfully Disabled Cache Dedup *\r\n*************************************\r\n")
        smtp_send("Notification: Container " + cname + " Cache Dedup Disabled", "Container " + cname + " Cache Dedup Disabled")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
    elif op == "7":
      data = {'storage_container_uuid':r['entities'][answer-1]['storage_container_uuid'],'name':r['entities'][answer-1]['name'],'on_disk_dedup':'NONE','finger_print_on_write':'off'}
      r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 200):
        print("\r\n****************************************\r\n* Successfully Disabled Capacity Dedup *\r\n****************************************\r\n")
        smtp_send("Notification: Container " + cname + " Capacity Dedup Disabled", "Container " + cname + " Capacity Dedup Disabled")
        
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
    elif op == "8":
      data = {'storage_container_uuid':r['entities'][answer-1]['storage_container_uuid'],'name':r['entities'][answer-1]['name'],'erasure_code':'off','finger_print_on_write':'off'}
      r = requests.put(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
      if check_response_code(r.status_code, 200):
        print("\r\n****************************************\r\n* Successfully Disabled Erasure Coding *\r\n****************************************\r\n")
        smtp_send("Notification: Container " + cname + " Erasure Coding Disabled", "Container " + cname + " Erasure Coding Disabled")
      else:
        print("Status Code: %s - Response: %s" % (r.status_code,r.content))
  else:
    err("You have to enter a valid number associated with the Storage Container")

# CREATE STORAGE CONTAINERS
def container_create():
  cname = raw_input("Please enter the container base name: ")
  if cname <> "":
    data = {'name':cname,'compression_enabled':False,'finger_print_on_write':'off','on_disk_dedup':'NONE','erasure_code':'off'}
    uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/storage_containers/"
    r = requests.post(uri, auth=('admin','nutanix/4u'), verify=False, data=json.dumps(data))
    if check_response_code(r.status_code, 201):
      print("\r\n**********************************\r\n* Successfully created Container *\r\n**********************************\r\n")
      smtp_send("Notification: Storage Container " + cname + " Created", "Storage Container " + cname + " Created")
    else:
      print("Status Code: %s - Response: %s" % (r.status_code,r.content))
  else:
    err("You must supply a Container name!")

# TASK INFO
def task_info():
  s = f = i = 0
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v2.0/tasks/list"
  data = {'cluster_uuid_list':None,'count':0,'cut_off_time_usecs':0,'entity_list': [{'entity_id':None,'entity_name':None,'entity_type':None}],'include_completed':True,'include_subtasks_info':True,'operation_type_list':None}
  r = requests.post(uri, auth=('admin', 'nutanix/4u'), verify=False, data=json.dumps(data))
  r = json.loads(r.content)
  for e in r['entities']:
    i += 1
    print('%d %s %s' % (i, e['operation_type'], e['progress_status']))
    if e['progress_status'] == "Succeeded":
      s += 1
    else:
      f += 1
  
  total_tasks = s + f
  print('\r\nTotal Tasks: %d' % total_tasks)
  print '--------------------'
  print("Successful Tasks: %d\r\nFailed Tasks: %d\r\n" % (s, f))
  #print(json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')))

# ALERT INFO
def alert_info():
  i = 0
  uri = "https://" + ip + ":" + port + "/PrismGateway/services/rest/v1/alerts/"
  r = requests.get(uri, auth=('admin', 'nutanix/4u'), verify=False)
  r = json.loads(r.content)
  print("\r\n")
  print("# - Message")
  for e in r['entities']:
    i += 1
    msg = str(e['message'])
    cvm_ip = str(e['contextValues'][0])
    smtp_ip = str(e['contextValues'][1])
    smtp_port = str(e['contextValues'][2])
    error = str(e['contextValues'][3])
    reboot_ts = str(e['contextValues'][0])
    msg = msg.replace("{ip_address}", cvm_ip).replace("{smtp_host}", smtp_ip).replace("{smtp_port}", smtp_port).replace("{reboot_timestamp_str}", reboot_ts).replace("{error}", error)
    print("%d - %s" % (i, msg))
  print("\r\n")

# PRETTY WRITE ERRORS
def err(msg):
  print("\r\n" + ''.join(list(repeat(' ',(len(msg)-1)/2))) + "ERROR" + ''.join(list(repeat(' ',(len(msg)-1)/2))))
  print(''.join(list(repeat('*',len(msg)+4))))
  print("* " + msg + " *")
  print(''.join(list(repeat('*',len(msg)+4))) + "\r\n")

# MAIN
def main():
  global ip
  global port
  ip = "10.68.69.102"
  port = "9440"
  init = raw_input("What do you want to do:\r\n 1. Change Cluster IP\r\n 2. Change Data Services IP\r\n 3. List Containers\r\n 4. Create Container\r\n 5. Modify a Container\r\n 6. List Images\r\n 7. List VMs\r\n 8. Create a VM\r\n 9. Power on/off or Delete a VM\r\n 10. List VLANs\r\n 11. Create a VLAN\r\n 12. Task Info\r\n 13. Alert Info\r\n 99. EXIT\r\n: ")

  if init == "1":
    change_cluster_ip()
  elif init == "2":
    change_ds_ip()
  elif init == "3":
    container_list()
  elif init == "4":
    container_create()
  elif init == "5":
    container_modify()
  elif init == "6":
    images_list()
  elif init == "7":
    vm_list()
  elif init == "8":
    vm_create()
  elif init == "9":
    vm_operations()
  elif init == "10":
    vlan_list()
  elif init == "11":
    vlan_create()
  elif init == "12":
    task_info()
  elif init == "13":
    alert_info()
  elif init == "99":
    exit(1)
  else:
    print("Try again - Only options are 1-13 or 99")
  main()

main()