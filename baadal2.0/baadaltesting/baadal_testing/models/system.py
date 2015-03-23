# coding: utf8
import os
import thread
import paramiko
import logging
import datetime
import logging.config
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import TimeoutException
from helper import *
from function import *
#from common import op_list
import libvirt
import commands
import MySQLdb as mdb
from selenium.webdriver.common.keys import Keys
import sys
import time
import random
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 600))
display.start()


#creating a logger for logging the records
logger = logging.getLogger("web2py.app.baadal")

#list of operation to be performed     
op_list={'revert_to_snapshot':0,'delete_snapshot':1,'snapshot':'Snapshot VM','pause_machine':'Suspend VM','Delete':'Delete VM','shutdown_machine':'Stop VM','destroy_machine':'Destroy VM','start_machine':'Start VM','user_details':'Add User','attach_extra_disk':"Attach Disk",'clone_vm':'Clone VM ','delete_user_vm':'Delete User','adjrunlevel':'Adjust Run Level','edit_vm_config':'Edit VM Config','resume_machine':'Resume VM','migrate_vm':'Migrate VM Between Hosts'}

usrnm_list={"badalUF":"BadalUF UF","badalUA":"Badal UA","badalUO":"Badal UO","badalUFA":"Badal UFA","badalUFO":"Badal UFO","badalUOA":"Badal UOA","badalUFOA":"BadalUFOA UFOA","badalU":"BadalU U"}

########################### DB connection ############################
def db_connection(host_ip,my_logger):
    Config = ConfigParser.ConfigParser()
    Config.read(os.path.join(get_context_path(),'static/db.conf'))
    database_user_name=Config.get("db_info","database_user_name")
    database_name=Config.get("db_info","database_name")
    password=Config.get("db_info","password")
    db=mdb.connect(ip_host,database_user_name,password,database_name)
    logger.debug(db)
    return db

#################################################################################################################
#                                       The main test function  for unit testing                                            #
#################################################################################################################
vm_status=2
def sys_test_script(test_case_no,host_ip,my_logger):
    baadal_path="https://"+str(host_ip)+"/baadal"
    my_logger.debug("Testing has been started and test case no is : "+ str(test_case_no))
    #creating connection to remote database
    baadal_db=db_connection(host_ip,my_logger) 
    logger.debug(baadal_db)
    root = xml_connect_sys()
    num=int(test_case_no)
    logger.debug("num is : "+str(num))
    vm_status=2
    public_ip =""
    logger.debug(root[num-1].get("id"))
    if root[num-1].get("id")==str(test_case_no):       
        i=num-1
        vm_name=""  
        for j in xrange(0,len(root[i])):
            temp_value=1
            logger.debug("inside for loop")       	
            driver = webdriver.Firefox()#connect to selenium server
            driver.implicitly_wait(10)
            page_present=driver.get(baadal_path) #url of the page to be hit 
            if page_present!="None":
            	driver.find_element_by_link_text(root.get("href")).click()
            	image=0
            	for k in xrange(0,len(root[i][j])):
                    if vm_status:
                        field_type=root[i][j][k].get("type")
                        xml_parent=root[i]
                        xml_child=root[i][j]
                        xml_sub_child=root[i][j][k]
                        logger.debug("task type is : " + str(field_type))
                    	if field_type=="input": #checking for text fields
                        	vm_name1=isInput(driver,xml_sub_child,my_logger)

                        elif field_type=="select":
                        	temp=isSelect(driver,xml_sub_child,temp_value,my_logger)# selecting from dropdown menu

                    	elif field_type=="submit": #checking for submit button
                        	time.sleep(3)
                                isSubmit(driver, xml_parent,xml_child,xml_sub_child,my_logger)

                        elif field_type=="create file":
				public_ip=create_file(driver,xml_child,xml_sub_child,xml_parent,vm_name,baadal_db,my_logger)

                        elif field_type=="shutdown_vm":
				shutdown_vm_test(driver,xml_child,xml_sub_child,xml_parent,baadal_db,my_logger)

                    	elif field_type=="scroll":#scrolling the page up/down
                        	isScroll(driver,xml_sub_child,my_logger)
                        	
                        elif field_type=="href":
                            isHref(driver,xml_sub_child,xml_child,my_logger)#clicking on the hyper link

                        elif field_type=="check_data":
                        	isCheckdata(driver,xml_parent,xml_child,xml_sub_child,vm_name,baadal_db,my_logger)#checking for data in table

                        elif field_type=="task_table":
                         	operation_name=xml_sub_child.text
                                logger.debug("operation name is : " + str(operation_name))
                         	vm_status=check_data_in_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,my_logger)
			elif field_type=="wait":
                        	isWait(driver,xml_parent,xml_child,xml_sub_child,my_logger)#checking for data in table

                        elif field_type=="wol":#checking for Wake on Lan
                        	table_path=xml_sub_child.get("path")
                        	wake_on_lan(driver,xml_child,xml_sub_child,table_path,my_logger)
                    
			elif field_type=="vnc":
                            print "calling vnc"
                            vnc_access(driver,xml_sub_child,xml_child,vm_name,baadal_db,my_logger)

                        elif field_type=="verify_sorting":
                            verify_sorting(driver,xml_sub_child,xml_child,my_logger)
                 
                    	elif field_type=="attach_disk":#checking for attached disk
                        	attach_disk(driver,xml_child,xml_sub_child,xml_parent,vm_name,baadal_db,my_logger)

                        elif field_type=="live_attach_disk":#checking for attached disk
                        	live_attach_disk(driver,xml_child,xml_sub_child,baadal_db,vm_name,my_logger)

                        elif field_type=="clone_vm":#checking for clone vm
                        	clone_vm(driver,xml_child,xml_sub_child,xml_parent,vm_name,baadal_db,my_logger)

                        elif field_type=="check_shutdown":#checking for baadal shutdown 
                        	check_baadal_shutdown(driver,xml_child,xml_sub_child,my_logger)

                        elif field_type=="shutdown_test":
                        	shutdown_test(driver,xml_child,xml_sub_child,my_logger)

                        elif field_type=="host_checking":#sanity check
                            check_host_state(driver,xml_child,xml_sub_child,my_logger)

                        elif field_type=="create_vm":#create lot of vm in a Host then put it into maintenance mode then sanity check
                            main_host_check(driver,xml_child,xml_sub_child,my_logger)

                        elif field_type=="edit_vm": 
                             edit_vm_conf(driver,xml_sub_child,xml_child,xml_parent,vm_name,my_logger) 

			elif field_type=="vm_snapshot":#checking for VM Snapshot
		             data=vm_list_my_vm(driver,xml_child,xml_sub_child,my_logger) 
                             vm_id=data[0][3:]
                             print vm_id	
                             take_vm_snapshot(driver,xml_child,xml_sub_child,data,my_logger)

                        elif field_type=="create_vm_for_image":# create VM for image
                             create_vm_for_image_testing(driver,xml_child,xml_sub_child,xml_parent,host_ip,my_logger)

                        elif field_type=="create_template_from_vm_image":# create template from vm image
                             create_vm_for_image_testing(driver,xml_child,xml_sub_child,xml_parent,host_ip,my_logger)

                    	else:
                        	logging.debug("report problem") #logging the report
                    	if k==5:
                        	vm_name=vm_name1
            	driver.close()#disconnect from server        
                if vm_status==0:
                
                    my_logger.debug("Your VM has not created.Please Check it!!!Its in pending task table!!!Either Scheduler is not working or Host is down!!!")
                if vm_status==1:
                	my_logger.debug("Your VM has not created.Please Check it!!!Its in failed task table!!!")
                	
            else:
                my_logger.debug("Cannot connect to controller.Please check controller")


###################################################################################################################
#performing   operation on vm        
def other_operation_on_vms(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):

    logger.debug("inside other op")
    op_name=xml_sub_child.get("op")
    logger.debug("op_name"+str(op_name))
    operation_name=op_list[op_name]
    my_logger.debug("Performing " +str(operation_name)+" operation on "+str(vm_name)+"...")
    logger.debug("op"+str(operation_name))    
    xpath=task_path_vm(xml_sub_child,op_name,my_logger)   
    path="//*[@title='" + str(xpath) + "']"    
    logger.debug(path)
    if isElementPresent(driver,xml_child,path,my_logger):
        logger.debug("inside is element checking")
	driver.find_element_by_partial_link_text("All VMs").click()
        logger.debug("@@@@@@ after click All VMS @@@@@@@")
	'''vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
        logger.debug("return to total user")
        logger.debug(vm_user_list)
	total=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list,my_logger)
        logger.debug("total"+str(total))
	driver.find_element_by_partial_link_text("All VMs").click()'''
	click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger) 
        logger.debug(path)
        driver.find_element_by_xpath(path).click()
        '''field_text=message_flash( driver,xml_sub_child,xml_child,my_logger)	
	if total==[]:
            logger.debug("inside total")
            logger.debug(xml_sub_child)
            result=message_in_db(xml_sub_child,my_logger)
	    limit=1
	else:
	    result="Your request already in the queue"
	    limit=0
        print_result(field_text,result,xml_child,my_logger)'''       
    else:
        logger.debug(xml_child.get("value") + ":Table does not exists") 
	limit=0	
    my_logger.debug("Performed " +str(operation_name)+" operation on "+str(vm_name)+"...")
    return 

#selecting operation to be perform   
def click_on_operations(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,op_name,baadal_db,my_logger):   
    logger.debug("inside click on operation")
    logger.debug("click on op op_name is " + str(op_name))  
    if op_name=="Delete":
        limit=delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    elif op_name=="attach_extra_disk":
	limit=operation_on_attach_disk(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger)
    elif op_name in {"revert_to_snapshot","delete_snapshot","snapshot"}:         
        limit=op_snap_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    elif op_name=="delete_user_vm": 
        limit=operation_on_del_user_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,baadal_db,my_logger)
    elif op_name=="edit_vm_config":
        operation_on_edit_vm_conf(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    elif op_name=="migrate_vm":
        limit=operation_on_migrate_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)  
    elif op_name=="clone_vm":
	limit=op_clone_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger)
    elif op_name=="start_machine":
	print "start vm"
        logger.debug("vm_name is : " + str(vm_name))
	limit=op_start_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger)
        logger.debug("return back after performing start vm")
    else:
	logger.debug("other opn")
        limit=other_operation_on_vms(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
        logger.debug("return back to click on operation")
    return limit
####################################################################################################################


def isSelect2(driver, xml_sub_child,path,my_logger):
	list=[]
	if xml_sub_child.get("select_name")=="configuration":	    
	    path=xml_sub_child.text +str(temp)+ "']/option"	  
	field=driver.find_elements_by_xpath(path)
	count=0
	for data in field:
	    value=data.get_attribute("value")
	    print value
	    list.insert(count,value)
	    count+=1	
	option_value=random.choice(list)
	print option_value
	driver.find_element_by_xpath(path + "[@value='" + option_value + "']").click()
        
	if xml_sub_child.get("select_name")=="configuration":
	    option_value=1
	return option_value




def create_template_from_vm_image(driver,xml_child,xml_sub_child,xml_parent,my_logger):
    data =vm_list_my_vm(driver,xml_child,xml_sub_child,my_logger) #get public ip of vm
    logger.debug(data)
    if data!=['','','','']:
        vm_id=data[0][3:]
        vm_name=data[1][0:]
        public_ip=data[2][0:]
        public_ip=str(public_ip)
    data1=vm_all_info(driver,xml_child,xml_sub_child,data,my_logger)
    logger.debug("after vm_all_info")
    data.append(data1[0][0:])
    data.append(data1[2][0:])
    logger.debug("After appending data from vm_all_info to main data list : "+str(data)) 
    if xml_sub_child.get("create_template_status")=="1":
        op_stop_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger)
        driver.find_element_by_title( 'Save as Template' ) .click()
        wait(60)
    data1=list_details_my_template(driver,xml_child,xml_sub_child,data,my_logger)
    request_vm(driver,xml_child,xml_sub_child,data1,my_logger)#request vm with that template which we created 

    
#requesting vm with same template which we created in create_template_from_vm_image
#when create_template_flag_status is 1 then function will check the entry only in template id and it return back to create_template_from_vm_image funtion
def request_vm(driver,xml_child,xml_sub_child,data1,my_logger):
    if data1!=['','','','','','','']:
        template_space=str(data[6][0])+str(data[6][1])+str(data[6][3])+str(data[6][4])
        logger.debug("Disk space of  VM is :"+str(disk_space))
        template_name = str(data[2][0:]) +" "+str(data[3][0:])+ " "+str(data[4][0:])+" "+str(data[5][0:])+" "+template_space+"("+str(data[0][0:])+")"
        logger.debug("template_name :"+str(template_name))
    driver.find_element_by_link_text('Request VM').click()
    driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='template_id']/option[text()="+template_name+"]").click()
    if xml_sub_child.get("create_template_status")=="1":
        my_logger.debug("Template created  successfully and having same values which was in vm image ")
        return 
    driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='configuration_1']/random.choice(option)").click()
    if xml_sub_child.get("extra_disk_flag")==1:
        extra_disk_space=xml_sub_child("extra_disk")
        driver.find_element_by_xpath("//table/tbody/tr/td/input[@id='request_queue_extra_HDD']").send_keys(extra_disk_space)
    if xml_sub_child.get("security_domain_flag")==1:
        driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='template_id']/random.choice(option)").click()
    if xml_sub_child.get("public_ip_flag")==1:
        driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='public_ip']").click()
    driver.find_element_by_xpath("//input[@type='submit']").click()        
     
         

            
# list_details_my_template function returns all value from the my template table    
#  returned values are the value who belongs to that particular vm from which   
# this template was made
def list_details_my_template(driver,xml_child,xml_sub_child,vm_name,my_logger):
    logger.debug("inside list_details_my_template")
    data1=[]
    driver.find_element_by_link_text('My Templates').click()
    path_col="//table[@id='mytemp']/tbody/tr/td"
    path_row="//table[@id='mytemp']/tbody/tr"
    path_header="//table[@id='mytemp']/tbody/tr/th"
    countc=0
    if isTablePresent(driver,xml_child,path_col,my_logger):
        c_count=0
        r_count=0
        select_row=0
        select=0
        select_status=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            logger.debug( "in for loop")
            if hdata.text=="Name of Template":
                template_name_no=count
            if hdata.text=="Operating System":
                os_no=count
            if hdata.text=="OS Name":
                os_name_no=count
            if hdata.text=="OS Version":
                os_version_no=count
            if hdata.text=="OS Type":
                os_type_no=count
            if hdata.text=="Architecture":
                architecture_no=count
            if hdata.text=="Harddisk(GB)":
                hard_disk_no=count
            count+=1
        col_count=count
        logger.debug( "after checking header count in list_details my templates")
        field=driver.find_elements_by_xpath(path_col)
        logger.debug(field)
        os_details=data[5][0:].split(' ')
        for data in field:
            if c_count%col_count==template_name_no:
                logger.debug("vm_name :"+str(vm_name)+"_template")
                if data[1][0:]+"_template"==template_name:
                    template_name=data.text
                else :
                    continue
            if c_count%col_count==os_no:
                operating_system=data.text
            if c_count%col_count==os_name_no:
                logger.debug("os_name :"+str(os_details[0][0:]))
                if data.text==data[0][0:]:
                    os_name=data.text
                else :
                    continue
            if c_count%col_count==os_version_no:
                logger.debug("os_version :"+str(os_details[1][0:]))
                if data.text== os_details[1][0:]:
                    os_version=data.text
                else:
                    continue
                                               
            if c_count%col_count==os_type_no:
                logger.debug("os_type :"+str(os_details[2][0:]))
                if data.text==os_details[2][0:]:
                    os_type=data.text
                else :
                    continue
            if c_count%col_count==architecture_no:
                logger.debug("architecture :"+str(os_details[3][0:]))
                if data.text==os_details[3][0:]:
                    architecture=data.text
                else :
                    continue
            if c_count%col_count==hard_disk_no:
                if data.text==data[4][0:]:
                    hard_disk=data.text
                else :
                    continue
            c_count+=1
    if c_count==0:
        logger.debug("No template is found with the  vm_name")
        return None
    data1.insert(0,template_name)
    data1.insert(1,operating_system)
    data1.insert(2,os_name)
    data1.insert(3,os_version)
    data1.insert(4,os_type)
    data1.insert(5,architecture)
    data1.insert(6,hard_disk)
    return data1
#create vm for image testing
def create_vm_for_image_testing(driver,xml_child,xml_sub_child,xml_parent,ssh_ip,my_logger):
    data =vm_list_my_vm(driver,xml_child,xml_sub_child,my_logger) #get public ip of vm
    logger.debug(data)
    logger.debug("u r in  create_vm_for_image_testing")
    if data!=['','','','']:
        vm_id=data[0][3:]
        vm_name=data[1][0:]
        public_ip=data[2][0:]
        public_ip=str(public_ip)
    logger.debug("vm id is : " + str(vm_id))
    logger.debug("data values :"+str(data))
    driver.refresh()
    logger.debug("u r in my function")
    data1=vm_all_info(driver,xml_child,xml_sub_child,data,my_logger)
    logger.debug("after vm_all_info")
    for val in data1:
        data.append(val)
	logger.debug("After appending data from vm_all_info to main data list : "+str(data))
    limit = op_stop_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger)
    if limit != 1 :
       driver.find_element_by_link_text("All VMs").click()
       data2= find_vm_id(driver,xml_child,xml_sub_child,vm_name,my_logger)
       logger.debug("data returned from find_vm_id :"+str(data2))
       data.append(data2[2][0:])
       data.append(data2[3][0:])
       data.append(data2[4][0:])
       logger.debug("After appending data from vm_all_info to main data list : "+str(data))
       create_vm_for_image(driver,xml_child,xml_sub_child,data,ssh_ip,my_logger)
       # time.sleep(60)
       data3= find_vm_id(driver,xml_child,xml_sub_child,vm_name1,my_logger)
       if data3[5][0:]== "Running":
          my_logger.debug("Create vm from vm image task is successfull")
       else:
          my_logger.debug("Create vm from vm image  task is not successfull ")
    return     
#function returns all the necessary information after clicking setting button
#return values are different from the return value of vm_list_my_vm function
def vm_all_info(driver,xml_child,xml_sub_child,data,my_logger):
    logger.debug("Inside vm_all_info function  ")
    vm_id=data[0][3:]
    logger.debug("vm_id" + str(vm_id))
    vm_name=data[1][0:]
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    data2=[]
    path_col="//table[@id='configuration']/tbody/tr/td"
    path_row="//table[@id='configuration']/tbody/tr"
    path_header="//table[@id='configuration']/tbody/tr/th"
    countc=0
    if isTablePresent(driver,xml_child,path_col,my_logger):
        logger.debug("return back to vm_all_info after checking table present")
        c_count=0
        r_count=0
        select_row=0
        select=0
        select_status=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            logger.debug( "in for loop")
            if hdata.text=="Private IP":
                private_ip_no=count
            if hdata.text=="VCPUs":
                cpu_no=count
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="HDD":
                hdd_name_no=count
            if hdata.text=="RAM":
                ram_no=count
            if hdata.text=="Operating System":
                operating_system_no=count
            if hdata.text=="Security Domain":
                security_domain_no=count
            count+=1
        col_count=count
        logger.debug( "after checking header count")

        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==private_ip_no:
                private_ip=data.text
            if c_count%col_count==cpu_no:
                total_no_cpu=data.text
            if c_count%col_count==hdd_name_no:
                hdd_name=data.text
            if c_count%col_count==ram_no:
                ram_capacity=data.text
            if c_count%col_count==operating_system_no:
                operating_system_name=data.text
            if c_count%col_count==security_domain_no:
                security_domain_name=data.text
            c_count+=1
    logger.debug( "security domain:"+str(security_domain_name))
    data2.insert(0,hdd_name)
    data2.insert(1,ram_capacity)
    data2.insert(2,operating_system_name)
    data2.insert(3,security_domain_name)
    data2.insert(4,private_ip)
    data2.insert(5,total_no_cpu)
    op_name=xml_sub_child.get("op1")
    
    return data2


#
#function will create vm from image by providing  necessery details in launch vm image page
#
def create_vm_for_image(driver,xml_child,xml_sub_child,data,ssh_ip,my_logger):
    logger.debug("inside create_vm_for_image ")
    if data!=['', '','','','','','','','','','','','']:
        print data
        vm_id=data[0][3:]
        vm_name=str(data[1])
        logger.debug("vm_name is :"+str(vm_name))
        if xml_sub_child.get("public_ip_flag") == "1":
            public_ip=data[2][0:]
        else:
            public_ip=""
        logger.debug("Public IP assigned to vm is :"+str(public_ip))
        if xml_sub_child.get("private_ip_flag") == "1":
            private_ip=data[8][0:]
        else:
            private_ip=""
        logger.debug("Private IP assigned to vm is :"+str(private_ip))
        cpuinfo=str(data[9][0:]).replace(" CPU","")
        logger.debug("Total no of cpu in VM :"+str(cpuinfo))
        host_ip=data[10][0:]
        logger.debug("Host IP of the VM is :"+str(host_ip))
        if '+' in data[4][0:]:
            add_extra_drive =1    
        disk_space=str(data[4][0])+str(data[4][1])+str(data[4][3])+str(data[4][4])
        logger.debug("Disk space of  VM is :"+str(disk_space))
        ram=str(data[5][0:]).replace(" MB","")
        logger.debug("RAM for vm is :"+str(ram))
        operating_sys_name=str(data[6][0:])
        logger.debug("VM operating system name :"+str(operating_sys_name))
        security_domain=str(data[7][0:])
        organisation=str(data[11][0:])
        owner=str(data[12][0:])
        vm_owner=xml_sub_child.get("owner")
        vm_image_name=organisation+"_badalUFA_"+vm_name
        logger.debug("VM image name :"+str(vm_image_name))
        vm_requester=xml_sub_child.get("requester")
        #vm_requester="badalUFA"
        template_id=operating_sys_name+" "+disk_space
        datastore="filer"
        add="'"
        public_ip=add + public_ip + add
        private_ip=add + private_ip + add
        template_id= add + template_id + add
        logger.debug("Template id :"+str(template_id))
        security_domain=add + security_domain + add
        logger.debug("security domain for vm :"+str(security_domain))
        logger.debug("attaching extra disk")
        if xml_sub_child.get("disk_status")== "1" and add_extra_drive== 1:
            attach_disk_name=vm_image_name
        elif xml_sub_child.get("disk_status")== "1":
            logger.debug("no extra disk is attached Please add extra disk to vm and try again ")
        else:
            attach_disk_name=""
            logger.debug("attaching extra disk when empty")
    logger.debug("after attaching extra disk")    
	#vm_requester="badalUFA"
    undefine_vm(driver,xml_child,xml_sub_child,ssh_ip,host_ip,vm_image_name,my_logger)
    click_on_sanity_check_operation(driver,xml_child,xml_sub_child,vm_name,my_logger)
    logger.debug("before scroll")
    isScroll(driver, xml_sub_child,my_logger)
    logger.debug("after scroll")
    path =driver.find_element_by_id('configure').click()
    path = driver.find_element_by_xpath("//a[@href='/baadal/admin/launch_vm_image']").click()
    field = driver.find_element_by_xpath("//table/tbody/tr/td/input[@id='vm_data_vm_name']").send_keys(vm_name)
    field = driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='RAM']/option[text()="+ram+"]").click()
    field = driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='vCPU']/option[text()="+cpuinfo+"]").click()
    #field = driver.find_element_by_xpath("//table/tbody/tr/td/input[@id='vm_data_template_id']").send_keys(template_id)
    #field = driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='vm_data_template_id']/option[text()="+ template_id+"]").click()
    driver.find_element_by_xpath("//table/tbody/tr/td/select[@id='vm_data_template_id']/option[@value='1']").click()
    #field = driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='vm_data_datastore_id']/option[text()="+datastore+"]").click()
    driver.find_element_by_xpath("//table/tbody/tr/td/select[@id='vm_data_datastore_id']/option[@value='1']").click()
    field = driver.find_element_by_xpath("//table/tbody/tr/td/input[@id='vm_data_vm_identity']").send_keys(vm_image_name)
    field = driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='security_domain']/option[text()="+security_domain+"]").click()
    logger.debug("//table/tbody/tr/td/input[@name='private_ip']/option[text()="+private_ip+"]")
    field = driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='private_ip']/option[text()="+private_ip+"]").click
    #field = driver.find_element_by_xpath("//table/tbody/tr/td/input[@id='vm_data_public_ip']").clear()
    field = driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='public_ip']/option[text()="+public_ip+"]").click
    if attach_disk_name!="" :
        field = driver.find_element_by_xpath("//table/tbody/tr/td/input[@id='attach_disks']").send_keys(attach_disk_name)
    else :
        field = driver.find_element_by_xpath("//table/tbody/tr/td/input[@id='attach_disks']").send_keys(attach_disk_name)
    field = driver.find_element_by_xpath("//table/tbody/tr/td/input[@id='requester_user']").send_keys(vm_requester)
    field = driver.find_element_by_xpath("//table/tbody/tr/td/input[@id='owner_user']").send_keys(vm_owner)

    driver.find_element_by_xpath("//input[@type='submit']").click()

#function undefine vm from the host
#ssh_ip is controller ip , host_ip is host on wich vm is running ,vm_image_name is vm name which we want to undefine
def undefine_vm(driver,xml_child,xml_sub_child,ssh_ip,host_ip,vm_image_name,my_logger):
    logger.debug("inside undefine vm")
    logger.debug("ssh ip is : " + str(ssh_ip))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_ip,username="root", password="baadal")
    logger.debug("Connect to server....")
    host_ip=str(host_ip)
    print type(host_ip)
    print host_ip
    #stdin, stdout,stderr=ssh.exec_command("sshpass -p host_baadal ssh "+host_ip+" -l root -o StrictHostKeyChecking=no grep MemTotal /proc/meminfo")
    stdin, stdout,stderr=ssh.exec_command("sshpass -p host_baadal ssh "+host_ip+" -l root -o StrictHostKeyChecking=no virsh undefine "+vm_image_name)
    var1=stdout.readlines()
    logger.debug("output :"+str(var1))

    #stdin,stdout,stderr=ssh.exec_command("ssh -X root@"+host_ip+" virsh undefine "+vm_image_name)

#click on sanity check operation

def click_on_sanity_check_operation(driver,xml_child,xml_sub_child,vm_name,my_logger):
    logger.debug("inside click on sanity check operation")
    isScroll(driver, xml_sub_child,my_logger)
    path=driver.find_element_by_xpath("//a[@href='/baadal/admin/sanity_check']").click()
    driver.find_element_by_xpath("//div/form/select/option[@value='0']").click()
    driver.find_element_by_xpath("//div/form/a/span[@class='icon-refresh']").click()
    path_table="//table[@id='sanity_check_table']/tbody"
    path_col="//div[@id='sanity_check_table']/table/tbody/tr/td"
    path_row="//div[@id='sanity_check_table']/table/tbody/tr"
    path_header="//div[@id='sanity_check_table']/table/tbody/tr/th"
    logger.debug("_________________________")
    if isTablePresent(driver,xml_child,path_col,my_logger):
        print "host_list table present"
        countc=0
        c_count=0
        row_count=1
        select=0
        select_vm=0
        click_flag=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Host":
                host_name_no=count
            if hdata.text=="Message":
                msg_no=count
            if hdata.text=="VM Name":
                vm_name_no=count
            if hdata.text=="Status":
                status_no=count
            if hdata.text=="Operations":
                operation_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        logger.debug("before data in  datafield")
        for data in field:
            if c_count%col_count==msg_no:
                msg=data.text
            if c_count%col_count==vm_name_no:
                vm_name1=data.text
                if vm_name in vm_name1:
                    select_vm=1
            if c_count%col_count==operation_no:
                operation=data.text
            if c_count%col_count==status_no:
                status=data.text
                if "Undefined"== status:
                    click_flag=1
            if (c_count%col_count==col_count-1):
                row_count+=1
		if select_vm and click_flag:
                	if msg in "VM not found":

                    		if operation in "Delete VM Info":
                                        print str(row_count)
                         		path="//div[@id='sanity_check_table']/table/tbody/tr["+str(row_count)+"]/td/a"
                         		driver.find_element_by_xpath(path).click()

            c_count+=1
        logger.debug("end of the click on sanity ")
	
#performing  edit vm configuration
def operation_on_edit_vm_conf(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    op_name=xml_sub_child.get("op1")
    operation_name=op_list[op_name]
    my_logger.debug("Performing " +str(operation_name)+" operation on "+str(vm_name)+"...")
    driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"']").click()
    path="//select[@id='request_queue_RAM']/option"
    isSelect2(driver, xml_sub_child,path,my_logger)
    path='//select[@id="request_queue_vCPU"]/option'
    isSelect2(driver, xml_sub_child,path,my_logger)
    #path='//input[@id="request_queue_public_ip"]'
    #isSelect1(driver,xml_child,path)
    driver.find_element_by_xpath("//input[@type='submit']").click()
    my_logger.debug("Performed " +str(operation_name)+" operation on "+str(vm_name)+"...")
    return

#performing delete operation on vm
def delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):   
    limit=0    
    op_name=xml_sub_child.get("op")  
    operation_name=op_list[op_name]
    my_logger.debug("Performing " +str(operation_name)+" operation on "+str(vm_name)+"...")
    path=xml_sub_child.get("title")  
    if isTablePresent(driver,xml_child,path,my_logger):         
    	driver.find_element_by_xpath(path).click()
    	click_on_dialogbox(driver)
    	click_on_dialogbox(driver)
    	field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
    else:
	my_logger.debug("No element exist")       
    my_logger.debug("Performed " +str(operation_name)+" operation on "+str(vm_name)+"...")   

    return limit

#performing  delete add_user operation on vm
def operation_on_del_user_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,baadal_db,my_logger):
    limit=0
    op_name=xml_sub_child.get("op") 
    operation_name=op_list[op_name]
    my_logger.debug("Performing " +str(operation_name)+" operation on "+str(vm_name)+"...")
    path=xml_sub_child.get("xpath_user")
    if isElementPresent(driver,xml_child,path,my_logger):  
        user_id=get_user_id(driver,xml_sub_child,xml_child,vm_name,baadal_db,my_logger) 
        driver.find_element_by_xpath("//*[@href='/baadal/admin/"+ str(op_name) +"/"+ str(vm_id) +"/"+ str(user_id) + "']").click()
        result="User access is eradicated."
        field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
        print_result(field_text,result,xml_child,my_logger)   
        if xml_sub_child.get("name") in vm_mode_type:
            check_deleted_user(driver,user_id,op_name,xml_child,xml_sub_child,my_logger)
    else:
    	my_logger.debug(xml_child.get("value") + ":Table does not exists") 
    my_logger.debug("Performed " +str(operation_name)+" operation on "+str(vm_name)+"...")   
    return limit


#performing attach disk operation on vm
'''def operation_on_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    my_logger.debug("inside operation_on_attach_disk")  
    op_name=xml_sub_child.get("op1") 
    logger.debug(op_name)  
    path="//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"']" 
    print path
    driver.find_element_by_xpath(path).click()
    print "shutdown"
    time.sleep(60)
    driver.refresh()
    print "reboot"
    op_name=xml_sub_child.get("op")   
    path="//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"']" 
    print path
    if isElementPresent(driver,xml_child,path,my_logger):
    	driver.find_element_by_xpath(path).click()
    	add_value(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
        check_attach_disk(driver,xml_sub_child,xml_child,vm_name,my_logger)
    else:
	my_logger.debug("No element exist")'''

def operation_on_attach_disk(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger):
    logger.debug("inside operation_on_attach_disk")  
    op_stop_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger)
    time.sleep(60)
    driver.refresh()
    op_name=xml_sub_child.get("op")
    logger.debug("op_name : "+ str(op_name))
    operation_name=op_list[op_name]
    my_logger.debug("Performing " +str(operation_name)+" operation on "+str(vm_name)+"...")
    driver.find_element_by_link_text("My VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)  
    xpath=task_path_vm(xml_sub_child,op_name,my_logger)    
    logger.debug("xpath is : " + str(xpath))
    path="//*[@title='" + str(xpath) + "']" 
    logger.debug("path is : " + str(path))
    if isElementPresent(driver,xml_child,path,my_logger):
    	driver.find_element_by_xpath(path).click()
    	add_value(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
        check_attach_disk(driver,xml_sub_child,xml_child,vm_name,my_logger)
    else:
	my_logger.debug("No element exist")
    limit=1
    my_logger.debug("Performed " +str(operation_name)+" operation on "+str(vm_name)+"...")
    return limit


def op_clone_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger):
    logger.debug("inside op_clone_vm")  
    op_stop_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger)
    driver.refresh()
    print "reboot"
    op_name=xml_sub_child.get("op")
    logger.debug("op_name"+str(op_name))
    operation_name=op_list[op_name]
    my_logger.debug("Performing " +str(operation_name)+" operation on "+str(vm_name)+"...")
    driver.find_element_by_link_text("My VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)     
    xpath=task_path_vm(xml_sub_child,op_name,my_logger)
    path="//*[@title='" + str(xpath) + "']" 
    logger.debug("path is : " + str(path))
    if isElementPresent(driver,xml_child,path,my_logger):
    	driver.find_element_by_xpath(path).click()
    	add_value(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
        check_clone_vm(driver,xml_sub_child,xml_child,vm_name,my_logger)
    else:
	logger.debug("No element exist")
    limit=1
    my_logger.debug("Performed " +str(operation_name)+" operation on "+str(vm_name)+"...")
    return 

def op_stop_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger):
    logger.debug("inside stop vm")
    op_name=xml_sub_child.get("op1")
    logger.debug("in stop vm op_name : "+ str(op_name))
    operation_name=op_list[op_name]
    my_logger.debug("Performing " +str(operation_name)+" operation on "+str(vm_name)+"...") 
    xpath=task_path_vm(xml_sub_child,op_name,my_logger) 
    logger.debug("xpath is : " + str(xpath))
    path="//*[@title='" + str(xpath) + "']"
    task_value=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    driver.find_element_by_partial_link_text("My VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    my_logger.debug("xpath is : " + str(path))
    if isElementPresent(driver,xml_child,path,my_logger):
    	driver.find_element_by_xpath(path).click()
        time.sleep(60)
	my_logger.debug("vm stop")
	driver.refresh()
    
    else:
	my_logger.debug("No element exist")
    driver.find_element_by_link_text("Tasks").click()
    task_n_value=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    logger.debug("Before operations:"+str(task_value))
    logger.debug("After operations:"+str(task_n_value))
    flag = compare_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,task_value,task_n_value,my_logger)
    my_logger.debug("Performed " +str(operation_name)+" operation on "+str(vm_name)+"...") 
    return

def op_start_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger):
    op_name=xml_sub_child.get("op2")
    logger.debug("op_name"+str(op_name))
    operation_name=op_list[op_name]
    my_logger.debug("Performing " +str(operation_name)+" operation on "+str(vm_name)+"...") 
    xpath=task_path_vm(xml_sub_child,op_name,my_logger)
    path="//*[@title='" + str(xpath) + "']" 
    logger.debug("path is : " + str(path))
    task_value=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    driver.find_element_by_partial_link_text("My VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    if isElementPresent(driver,xml_child,path,my_logger):
    	driver.find_element_by_xpath(path).click()
        #time.sleep(60)
	my_logger.debug("vm start")
	driver.refresh()
   
    else:
	my_logger.debug("No element exist")
    driver.find_element_by_link_text("Tasks").click()
    logger.debug("operation name is : " + str(operation_name))
    task_n_value=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    logger.debug("Before operations:"+str(task_value))
    logger.debug("After operations:"+str(task_n_value))
    compare_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,task_value,task_n_value,my_logger)
    my_logger.debug("Performed " +str(operation_name)+" operation on "+str(vm_name)+"...") 
    return

#performing migrate operation on vm
def operation_on_migrate_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    logger.debug("inside operation_on_migrate_vm")
    op_name=xml_sub_child.get("op")
    limit=0
    op_name=xml_sub_child.get("op")
    operation_name=op_list[op_name]
    my_logger.debug("Performing " +str(operation_name)+" operation on "+str(vm_name)+"...") 
    path="//a[@title='Migrate this virtual machine']"
    if isElementPresent(driver,xml_child,path,my_logger):
	my_logger.debug("vm exist")
	driver.find_element_by_partial_link_text("All VMs").click()
        #vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
	#total=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list,my_logger)
        #driver.find_element_by_partial_link_text("All VMs").click()
	my_logger.debug("again clicked all vms")
	click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger) 
	status=check_status_of_vm(driver,xml_sub_child,xml_child,my_logger)
	my_logger.debug(status+" status")
	driver.find_element_by_xpath("//a[@title='Migrate this virtual machine']").click()
	if xml_sub_child.get("live")=="yes":
	   my_logger.debug("live migration")
           message=message_flash(driver,xml_sub_child,xml_child,my_logger)
           print message
           message=str(message)
           if message=="No host available right now":
                sys.exit()
           else:
           	driver.find_element_by_xpath("//input[@name='live_migration']").click()
	   	driver.find_element_by_xpath("//input[@value='Migrate']").click()       
	'''if total:
	    result="Your request already in the queue"
	    field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
            print_result(field_text,result,xml_child,my_logger)
	else:
           result="Your task has been queued. please check your task list for status. "
           field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
           print field_text
           print_result(field_text,result,xml_child,my_logger)
           print print_result
           limit=1
	print "migration done"'''
    else:
	print "Migrate operation could not performed because no host is available.Please do host up then again try this operation"
        my_logger.debug("Migrate operation could not performed because no host is available.Please do host up then again try this operation")
    limit=1
    my_logger.debug("Performed " +str(operation_name)+" operation on "+str(vm_name)+"...") 
    return limit 
            
#checking whether user access removed for a vm or not                        
def check_deleted_user(driver,user_id,op_name,xml_child,xml_sub_child,my_logger):
    operation_name=op_list[op_name]

    path=xml_sub_child.get("xpath_user")
    user_absent=1
    if isTablePresent(driver,xml_child,path,my_logger):
        user_table=driver.find_elements_by_xpath("//table[@id='vm_users']/tbody/tr/td")
	for user in user_table:
            if user.get_attribute("id")==user_id:
                my_logger.error(xml_child.get("value")  + "User has not been deleted")
	        user_absent=0
        if user_absent:
            my_logger.debug(xml_child.get("value")  + "User access is eradicated")
    else:
        my_logger.debug("User access is eradicated")
    return


def delete_vm_from_allvms(driver,xml_sub_child,xml_child,my_logger):
    vm_exist=0
    driver.find_element_by_partial_link_text("All VMs").click()
    path="//table[@id='listallvm']/tbody/tr/td"
    counth=0
    user_vm=0
    select_row=0 
    col_count=0
    user_present=0
    if isElementPresent(driver,xml_child,path,my_logger):
        field=driver.find_elements_by_xpath("//table[@id='listallvm']/thead/tr/th")  
        for data in field:
            if data.text=="Owner":
		requester_col_no=counth
		
            counth+=1
        
        total_col=counth
	
        field=driver.find_elements_by_xpath("//table[@id='listallvm']/tbody/tr/td[2]")  
        for data in field:
	         for username in username_list:
		         if username==data.text:
		             
   		             user_present+=1
        for x in range(0,user_present):
	    
            driver.refresh()
	    
            field_data=driver.find_elements_by_xpath("//table[@id='listallvm']/tbody/tr/td")
	   
            for user in field_data:
                
                if (col_count%total_col==requester_col_no):
                    for username in username_list:
                        if username==user.text:
                            user_name=user.text
                            select_row=1   
			   
                if col_count%total_col==(total_col-1) :
                    if select_row:
                        vm_id=user.get_attribute("id")
         	        
                        path="//*[@href='/user/settings/"+ str(vm_id[3:]) +"']"
    	
			time.sleep(30)
    	    		if isElementPresent(driver,xml_child,path,my_logger):
	       		    q=driver.find_element_by_xpath(path).click()
	       		    path="//a[@title='Delete this virtual machine']"
		
	       		    if isElementPresent(driver,xml_child,path,my_logger): 
		   		driver.find_element_by_xpath(path).click() 
		   		click_on_dialogbox(driver,my_logger)
		   		click_on_dialogbox(driver,my_logger)
		   		my_logger.debug(str(user_name) + " VM (" + str(vm_id[3:]) + ") has been deleted from All VMs table") 
                    		select_row=0
				col_count=0
				vm_exist=1
				driver.find_element_by_partial_link_text("All VMs").click()
				driver.refresh()
				time.sleep(10)
				break
		   
                col_count+=1
	if vm_exist==0:
	    my_logger.debug("No VM exists to perform Delete Pending request!!!")
    return

 
def check_vm_in_pending_request_table(driver,xml_sub_child,xml_child,vm_name,old_field,my_logger):
    logger.debug("check_vm_in_pending_request_table")  
    path=str(old_field)+'/tbody/tr/td'
    #path="//table[@id='sortTable3']/tbody/tr/td"
    #path="//table[@id='sortTable3']/tbody/tr/td"
    counth=0
    user_vm=0
    select_row=0 
    col_count=0
    s_row=0
    ref=0
    if isElementPresent(driver,xml_child,path,my_logger):
        new_field=str(old_field)+'/thead/tr/th'
	new_field=str(new_field)
        my_logger.debug(new_field)
        field=driver.find_elements_by_xpath(new_field)  
        for data in field:
            if data.text=="Requested By":
               user_no=counth
	    if data.text=="VM Name":
		       vm_no=counth	    
            counth+=1        
        total_col=counth
        field1=driver.find_elements_by_xpath(path)
        for data in field1:            
            if col_count%total_col==vm_no:		
                if vm_name in data.text:
                    logger.debug("vm_name" + str(data.text))
                    s_row=1	      
            if col_count%total_col==user_no:
                logger.debug(xml_child[0].text)
                usernm=usrnm_list[xml_child[0].text]        
                if str(data.text)==usernm:
                    logger.debug(data.text)
                    select_row=1   		   
            if col_count%total_col==(total_col-1) :
                logger.debug("value of select_row : " + str(select_row))
                logger.debug("value of s_row : " + str(s_row))
                if select_row :
                    if s_row:
			data1=data.find_element_by_tag_name("a")
                        value=data1.get_attribute("id")
                        logger.debug("id" + str(value))				
                        vm_id=value[7:]
                        logger.debug("vm_id"+str(vm_id))
                        break
            col_count+=1    
    return vm_id

#checking data in attach_disk table
def check_attach_disk(driver,xml_sub_child,xml_child,vm_name,my_logger):
    driver.find_element_by_partial_link_text("All Pending Requests").click()
    driver.find_element_by_partial_link_text("Attach Disk").click()
    old_field="//table[@id='sortTable3']"
    vm_id=check_vm_in_pending_request_table(driver,xml_sub_child,xml_child,vm_name,old_field,my_logger)
    if xml_sub_child.get("action")=="approve_request": 
	    logger.debug("approve rqst")   
            driver.find_element_by_xpath("//*[@href='/baadal/admin/approve_request/"+ str(vm_id) +"']").click()  
            time.sleep(60)
	    logger.debug("approve attach disk rqst")      
    else:
        
        driver.find_element_by_xpath("//*a[@href='/baadal/admin/reject_request/"+ str(vm_id) +"']").click()
       
    return

def check_create_vm(driver,xml_sub_child,xml_child,vm_name,my_logger):
    driver.find_element_by_partial_link_text("All Pending Requests").click()
    driver.find_element_by_partial_link_text("Install VM").click()
    #field=driver.find_elements_by_xpath("//table[@id='sortTable2']/tbody/tr")
    old_field="//table[@id='sortTable1']"
    logger.debug(old_field)
    vm_id=check_vm_in_pending_request_table(driver,xml_sub_child,xml_child,vm_name,old_field,my_logger)
    if xml_sub_child.get("action")=="approve_request": 
	    logger.debug("approve rqst")   
            driver.find_element_by_xpath("//*[@href='/baadal/admin/approve_request/"+ str(vm_id) +"']").click()  
            time.sleep(60)
	    logger.debug("approve  rqst")      
    else:
        
        driver.find_element_by_xpath("//*a[@href='/baadal/admin/reject_request/"+ str(vm_id) +"']").click()
       
    return

def check_clone_vm(driver,xml_sub_child,xml_child,vm_name,my_logger):
    print "inside check_clone_vm"
    driver.find_element_by_partial_link_text("All Pending Requests").click()
    driver.find_element_by_partial_link_text("Clone VM").click()
    field=driver.find_elements_by_xpath("//table[@id='sortTable2']/tbody/tr")
    old_field="//table[@id='sortTable2']"
    vm_id=check_vm_in_pending_request_table(driver,xml_sub_child,xml_child,vm_name,old_field,my_logger)
    print vm_id
    if xml_sub_child.get("action")=="approve_request":   
	    logger.debug("approve_request") 
            print "//*[@href='/baadal/admin/approve_request/"+ str(vm_id) +"']"
            driver.find_element_by_xpath("//*[@href='/baadal/admin/approve_request/"+ str(vm_id) +"']").click() 
            time.sleep(120)
            logger.debug("approve_clone_request")      
    else:
        
        driver.find_element_by_xpath("//*a[@href='/baadal/admin/reject_request/"+ str(vm_id) +"']").click()
       
    return  


def vm_mode_operation(xml_child,xml_sub_child,xml_parent,driver,vm_name,vm_id,baadal_db,my_logger):
    logger.debug("inside vm_mode_operation")
    op_name=xml_sub_child.get("op") 
    logger.debug("vm _mode op_name is : " + str(op_name))   
    operation_name=op_list[op_name]
    logger.debug("vm _mode operation_name is : " + str(operation_name)) 
    #task_value=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    task_value=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    driver.find_element_by_partial_link_text("All VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    logger.debug("return back to vm_mode_operation")
    limit=click_on_operations(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,op_name,baadal_db,my_logger)	
    if limit:
        driver.find_element_by_link_text("Tasks").click()
        task_n_value=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
	logger.debug("Before operations:"+str(task_value))
    	logger.debug("After operations:"+str(task_n_value))
	compare_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,task_value,task_n_value,my_logger)
    else:
        logger.debug(xml_sub_child.get("print_mode"))
    return
   	   

def vm_list_my_vm(driver,xml_child,xml_sub_child,my_logger):
    logger.debug("inside vm_list_my_vm")
    data2=[]
    path_col="//table[@id='myvms']/tbody/tr/td"
    path_row="//table[@id='myvms']/tbody/tr"
    path_header="//table[@id='myvms']/thead/tr/th"
    #path=driver.find_element_by_id("menu_user").click()
    #path=driver.find_element_by_link_text("My VMs").click()
    #driver.find_element_by_partial_link_text("My VMs").click()
    countc=0
    if isTablePresent(driver,xml_child,path_col,my_logger):
        logger.debug("return back after checking table exist!!")
        c_count=0
        r_count=0
        select_row=0
	select=0
	select_status=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="Owner":
                user_name_no=count
            if hdata.text=="Status":
                status_no=count
	    if hdata.text=="Public IP":
		public_ip_no=count
            count+=1
        col_count=count
        logger.debug("col_count is : " + str(col_count))
        logger.debug("vm_no is : " + str(vm_name_no))
        logger.debug("user no : " + str(user_name_no))
        logger.debug("status is : " + str(status_no))
        logger.debug("public ip is : " + str(public_ip_no))
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            logger.debug("c_count is : " + str(c_count))
            if c_count%col_count==vm_name_no:
                vm_name=data.text
            if c_count%col_count==user_name_no:
                for username in username_list:
                    logger.debug(username)
                    logger.debug(data.text)
		    if username==data.text:
                       logger.debug("inside if user")
                       user_name=data.text
                       select_row=1
                       break
                logger.debug("select row is : " + str(select_row))
            if c_count%col_count==status_no:
                logger.debug("inside status c_count is : " + str(c_count))
                status=data.text
		if status=="Running":
                   select_status=1
	    if c_count%col_count==public_ip_no:
                logger.debug("inside public ip c_count is " + str(c_count))
                public_ip=data.text
		if public_ip == "Not Assigned":
                   select=0
		else:
	           select=1
            logger.debug("value is : " + str(c_count%col_count))
            logger.debug("value of col_count-1 is : " + str(col_count-1))
            if (c_count%col_count == col_count-1 ):
                logger.debug("select row : " + str(select_row) + "select : " + str(select) + "select_status : " + str(select_status))
	        if select_row and select and select_status:
                    logger.debug("inside if for select id")
                    logger.debug(type(status))	
                    logger.debug(xml_sub_child.get("status"))    
                    if (str(status)==xml_sub_child.get("status")):
                        logger.debug("inside if for status")
                        field_data=driver.find_elements_by_xpath(path_row)
                        data1=data.find_element_by_tag_name("a")
			vm_id=data1.get_attribute("id")
              		countc+=1
                        break   
                            
            c_count+=1           
    if countc==0:
        my_logger.debug("No user of testing User.Please Create a VM!!!!")
        vm_name=""
        vm_id=""
	public_ip=""
        status=""
    data2.insert(0,vm_id)
    data2.insert(1,vm_name)
    data2.insert(2,public_ip)
    data2.insert(3,status)
    logger.debug(data2)
    return data2

def mapping(public_ip):
    print "inside mapping function"
    if public_ip in "172.16.0.221":
       public_ip="10.237.20.252"
    else:
       public_ip=public_ip
    return public_ip
        
		   
####################### Migration of VM ############################                          
def create_file(driver,xml_child,xml_sub_child,xml_parent,vm_name,baadal_db,my_logger):
    '''data = vm_list_my_vm(driver,xml_child,xml_sub_child,my_logger)
    logger.debug("return back to create file")    
    logger.debug(data)
    if data!=['', '','','']:
        vm_id=data[0][3:]
        vm_name=data[1][0:]
        public_ip=data[2][0:]
    public_ip=mapping(public_ip)
    public_ip=str(public_ip)
    logger.debug(public_ip)'''
    logger.debug("inside create file function")
    logger.debug("vm_name : " + str(vm_name))
    vm_info=get_vm_info_frm_mylist(xml_child,xml_sub_child,driver,vm_name,my_logger) #get public ip of vm
    public_ip=vm_info['public_ip']
    vm_id=vm_info['vm_id']
    vm_name=vm_name
    public_ip=mapping(public_ip)
    public_ip=str(public_ip)
    logger.debug("public_ip : " + str(public_ip))
    logger.debug("vm_id : " + str(vm_id))
    logger.debug("vm_name : " + str(vm_name))
    change_vm_paswd(public_ip)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(public_ip,username="root", password="baadal123")
    logger.debug("Connect to server....")
    stdin, stdout,stderr=ssh.exec_command("mkdir /home/testmig")
    stdin, stdout,stderr=ssh.exec_command("touch /home/testmig/test.txt")
    localstring = xml_sub_child.text
    stdin, stdout,stderr=ssh.exec_command("echo " + localstring + " > /home/testmig/test.txt")
    stdin, stdout,stderr=ssh.exec_command("vi /home/testmig/test.txt")
    isHref(driver,xml_sub_child,xml_child,my_logger)
    vm_mode_operation(xml_child,xml_sub_child,xml_parent,driver,vm_name,vm_id,baadal_db,my_logger)
    check_file(driver,xml_sub_child,ssh,my_logger)
    stdin.flush()
    return public_ip

def check_file(driver,xml_sub_child,ssh,my_logger):
    chan = ssh.get_transport().open_session()
    chan.exec_command("find /home/testmig/test.txt")
    return_status = chan.recv_exit_status()
    if return_status==0:
        chan = ssh.get_transport().open_session() 
        chan.exec_command("ls -a /home/testmig/.test.txt.swp")
        return_status = chan.recv_exit_status()
        stdin, stdout,stderr=ssh.exec_command("cat /home/testmig/test.txt")
        localstring=stdout.read()
        if (return_status==0):
            my_logger.debug( "Vm migrated with file open")
            my_logger.debug("vm migrated correctly")
        else:
            my_logger.debug("Swp file does not exist")
            my_logger.debug("error occur in VM migration")

######################shutdown VM,Paused VM,Delete VM #######################################   
def shutdown_vm_test(driver,xml_child,xml_sub_child,xml_parent,baadal_db,my_logger):
    data = vm_list_my_vm(driver,xml_child,xml_sub_child,my_logger) #get public ip of vm
    logger.debug("return back to shutdown")
    logger.debug(data)
    if data!=['', '','','']:
        vm_id=data[0][3:]
        vm_name=data[1][0:]
        public_ip=data[2][0:]
        public_ip=mapping(public_ip)
        public_ip=str(public_ip)
        logger.debug(public_ip)
        vm_mode_operation(xml_child,xml_sub_child,xml_parent,driver,vm_name,vm_id,baadal_db,my_logger) #click seeting button and shutdown vm
        logger.debug("return back after vm_mode_operation")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        check=pingf(driver,xml_child,xml_sub_child,vm_name,public_ip,my_logger)
        if check:
           my_logger.debug("VM is either shutdown/Paused/Delete ")
        else:
           my_logger.debug(" Some Error occur in shutdown/Paused/Delete")
    else :
            my_logger.debug("no vm exist")
            return 0  

############################################# Attach Disk #############################################

def attach_disk(driver,xml_child,xml_sub_child,xml_parent,vm_name,baadal_db,my_logger):
    logger.debug("inside attach disk function")
    logger.debug("vm_name : " + str(vm_name))
    vm_info=get_vm_info_frm_mylist(xml_child,xml_sub_child,driver,vm_name,my_logger) #get public ip of vm
    public_ip=vm_info['public_ip']
    vm_id=vm_info['vm_id']
    vm_name=vm_name
    logger.debug("vm id is : " + str(vm_id))
    public_ip=mapping(public_ip)
    public_ip=str(public_ip)
    logger.debug("public_ip : " + str(public_ip))
    logger.debug("vm_id : " + str(vm_id))
    logger.debug("vm_name : " + str(vm_name))
    change_vm_paswd(public_ip)
    check=execute_remote_cmd(public_ip,"root","fdisk -l | egrep 'Disk.*bytes' | awk '{ sum +=$3;} END {print sum}'", "baadal123",my_logger, ret_list = False)
    logger.debug("before attach request disk size is : " + str(check))
    vm_mode_operation(xml_child,xml_sub_child,xml_parent,driver,vm_name,vm_id,baadal_db,my_logger)
    driver.find_element_by_partial_link_text("All VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    op_name=xml_sub_child.get("op2")
    logger.debug(op_name)
    limit=click_on_operations(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,op_name,baadal_db,my_logger)
    time.sleep(60)
    check1=execute_remote_cmd(public_ip,"root","fdisk -l | egrep 'Disk.*bytes' | awk '{ sum +=$3;} END {print sum}'", "baadal123",my_logger, ret_list = False)
    if check == check1:
	   my_logger.error("error occur in attach disk operation please check logs ")
           my_logger.debug("before attach request disk size is : " + str(check))
	   my_logger.debug("after attach request disk size is : " +str(check1))
    else:
           my_logger.debug("attached sucessfully:")
           my_logger.debug("before attach request disk size is : " + str(check))
	   my_logger.debug("after attach request disk size is : " +str(check1))
    delete_specific_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)


def live_attach_disk(driver,xml_child,xml_sub_child,baadal_db,vm_name,my_logger):
    logger.debug("vm name is : " + str(vm_name))
    logger.debug("inside live attach disk function")
    data = vm_list_my_vm(driver,xml_child,xml_sub_child,my_logger) #get public ip of vm
    if data!=['', '','','']:
        vm_id=data[0][3:]
        vm_name=data[1][0:]
        public_ip=data[2][0:]
    public_ip=mapping(public_ip)
    public_ip=str(public_ip)
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    vm_info=get_vm_info_frm_setting(xml_child,xml_sub_child,driver,vm_name,my_logger)
    privous_HDD=vm_info['hdd']
    logger.debug("privous_HDD is : " + str(privous_HDD))
    logger.debug("public ip is : " + public_ip)
    change_vm_paswd(public_ip)
    check=execute_remote_cmd(public_ip,"root","fdisk -l | egrep 'Disk.*bytes' | awk '{ sum +=$3;} END {print sum}'", "baadal123",my_logger, ret_list = False)
    logger.debug("before attach request disk size is : " + str(check))
    if check in "10.7":
       my_logger.debug("error in attached disk")
    else:
       my_logger.debug("successfully attached")
       my_logger.debug("New disk size is " + str(check))
     
################################ Clone VM ###########################################
def clone_vm_list(driver,xml_child,xml_sub_child,vm_name,my_logger):
    logger.debug("inside clone vm list")
    data2=[]
    path_col="//table[@id='myvms']/tbody/tr/td"
    path_row="//table[@id='myvms']/tbody/tr"
    path_header="//table[@id='myvms']/thead/tr/th"
    #path=driver.find_element_by_id("menu_user").click()
    path=driver.find_element_by_link_text("My VMs").click()
    new_vmname=vm_name+"_clone"
    if isTablePresent(driver,xml_child,path_col,my_logger):
        logger.debug("inside table checking")
        countc=0
        c_count=0
        r_count=0
        select_row=0
	select=0
	select_vm=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="Owner":
                user_name_no=count
            if hdata.text=="Status":
                status_no=count
	    if hdata.text=="Private IP":
		private_ip_no=count
            count+=1
        col_count=count
        logger.debug("vm name no is : " + str(vm_name_no))
        logger.debug("user_name_no is : " + str(user_name_no))
        logger.debug("status_no is : " + str(status_no))
        logger.debug("private_ip_no is : " + str(private_ip_no))
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==vm_name_no:
                vm_name1=data.text
                logger.debug("vm name is : " + str(vm_name1))
                logger.debug("new vm name is : " + str(new_vmname))
		if new_vmname in vm_name1:
			select_vm+=1
            if c_count%col_count==user_name_no:
                for username in username_list:
		    if username==data.text:
                        user_name=data.text
                        select_row=1
                        break
            if c_count%col_count==status_no:
                status=data.text
	    if c_count%col_count==private_ip_no:
                private_ip=data.text
            if (c_count%col_count==col_count-1):
                logger.debug("select_vm : " + str(select_vm))
                logger.debug("select_row : " + str(select_row))
	        if select_vm and select_row:
                    field_data=driver.find_elements_by_xpath(path_row)
                    #data1=data.find_element_by_tag_name("a")
		    vm_id=data.get_attribute("id")
                    logger.debug("vm_id "+str(vm_id))
              	    countc+=1
                    break         
            c_count+=1         
    if countc==0:
        my_logger.debug("No user of testing User.Please Create a VM!!!!")
        vm_name=""
        vm_id=""
	private_ip=""
    data2.insert(0,vm_id)
    data2.insert(1,vm_name1)
    data2.insert(2,private_ip)
    logger.debug(data2)
    return data2

def clone_vm(driver,xml_child,xml_sub_child,xml_parent,vm_name,baadal_db,my_logger):
    logger.debug("inside clone vm")
    logger.debug("vm_name : " + str(vm_name))
    vm_info=get_vm_info_frm_mylist(xml_child,xml_sub_child,driver,vm_name,my_logger) #get public ip of vm
    public_ip=vm_info['public_ip']
    vm_id=vm_info['vm_id']
    public_ip=mapping(public_ip)
    public_ip=str(public_ip)
    logger.debug("public_ip : " + str(public_ip))
    logger.debug("vm_id : " + str(vm_id))
    change_vm_paswd(public_ip)
    check=execute_remote_cmd(public_ip,"root","fdisk -l | egrep 'Disk.*bytes' | awk '{ sum +=$3;} END {print sum}'", "baadal123",my_logger, ret_list = False)
    logger.debug("check value is : " + str(check))
    chk=execute_remote_cmd(public_ip,"root","grep MemTotal /proc/meminfo", "baadal123",my_logger, ret_list = False)    
    logger.debug("chk value is : " + str(chk))
    vm_mode_operation(xml_child,xml_sub_child,xml_parent,driver,vm_name,vm_id,baadal_db,my_logger) 
    driver.find_element_by_partial_link_text("All VMs").click() 
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    op_name=xml_sub_child.get("op2")
    logger.debug("op_name is : " + str(op_name))
    limit=click_on_operations(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,op_name,baadal_db,my_logger)
    logger.debug("return back to clone vm")
    time.sleep(20) 
    op_name=xml_sub_child.get("op2")
    logger.debug("vm name is : " + str(vm_name))
    data1=clone_vm_list(driver,xml_child,xml_sub_child,vm_name,my_logger)
    logger.debug(data1)
    if data1!=['', '','']:
        vm_id2=data1[0]
        vm_name2=data1[1][0:]
	private_ip=data1[2][0:]
    private_ip=str(private_ip)
    logger.debug("vm_id is : " + str(vm_id2))
    logger.debug("vm_name2 is : " + str(vm_name2))
    logger.debug("private ip is : " + str(private_ip))
    #driver.find_element_by_partial_link_text("My VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name2,vm_id2,my_logger)
    logger.debug("return back click on setting")
    limit=click_on_operations(driver,xml_sub_child,xml_child,xml_parent,vm_name2,vm_id2,op_name,baadal_db,my_logger)
    time.sleep(120)
    logger.debug("return back to cloning vm") 
    '''command="ssh -X root@"+private_ip+" grep MemTotal /proc/meminfo"
    logger.debug(command)
    new_chk=execute_remote_cmd(public_ip,"root",command, "baadal123",my_logger, ret_list = False)
    cmnd="ssh -X root@"+private_ip+" fdisk -l | egrep 'Disk.*bytes'| awk '{ sum +=$3;} END {print sum}'"
    logger.debug(cmnd)
    new_check=execute_remote_cmd(public_ip,"root",cmnd, "baadal123",my_logger, ret_list = False)'''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(public_ip,username="root", password="baadal123")
    logger.debug("Connect to server....")
    stdin, stdout,stderr=ssh.exec_command("sshpass -p baadal123 ssh "+private_ip+" -l root -o StrictHostKeyChecking=no grep MemTotal /proc/meminfo")
    new_chk=stdout.readline()
    logger.debug("new chk is : " + str(new_chk))
    stdin, stdout,stderr=ssh.exec_command("sshpass -p baadal123 ssh "+private_ip+" -l root -o StrictHostKeyChecking=no fdisk -l | egrep 'Disk.*bytes'| awk '{ sum +=$3;} END {print sum}'")
    new_check=stdout.readline()
    logger.debug("new check is : " + str(new_check))
    if new_chk in chk:
	if new_check in check:
       		my_logger.debug("vm and clone vm have same configuration")
    else:
	my_logger.error("vm and clone vm have not same configuration")
        send_mail("vm and clone vm have not same configuration")
    delete_specific_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    delete_specific_vm(driver,xml_sub_child,xml_child,vm_name2,vm_id2,my_logger)
    
#################################### shutdown baadal ################################################

def copy_data(public_ip,my_logger):
    public_ip=mapping(public_ip)
    public_ip=str(public_ip)
    execute_remote_cmd(public_ip,"root","mkdir /home/test", "baadal",my_logger, ret_list = False)
    execute_remote_cmd(public_ip,"root","touch /home/test/test.txt", "baadal",my_logger, ret_list = False)
    stdin.flush()

def shutdown(driver,my_logger):
        logger.debug("inside shutdown function")
	driver.find_element_by_partial_link_text("Shutdown Baadal").click()   
	driver.find_element_by_id("start_shutbown_button").click()
        click_on_dialogbox(driver)
        time.sleep(6)
	driver.refresh()
        time.sleep(6)
	driver.find_element_by_xpath("//input[@type='button']").click()
	driver.refresh()
	path=driver.find_element_by_xpath("//a[@href='/baadal/admin/sanity_check']").click()

def check(public_ip,my_logger):
    public_ip=mapping(public_ip)
    public_ip=str(public_ip)
    check=execute_remote_cmd(public_ip,"root","find /home/test/test.txt", "baadal",my_logger, ret_list = False)
    if check!=0:
		my_logger.debug("file exist on vm")
    else:
		my_logger.debug("file does not exist")

def check_baadal_shutdown(driver,xml_child,xml_sub_child,my_logger):
    data = vm_list_my_vm(driver,xml_child,xml_sub_child,my_logger)
    if data!=['','','','']:
        vm_id=data[0][3:]
        vm_name=data[1][0:]
	public_ip=data[2][0:]
    public_ip=str(public_ip)
    copy_data(public_ip)
    shutdown(driver)
    check(public_ip)


def shutdown_baadal(driver,my_logger):
	driver.find_element_by_partial_link_text("Shutdown Baadal").click()   
	driver.find_element_by_id("start_shutbown_button").click()
        click_on_dialogbox(driver)
	driver.refresh()
        
def check_baadal_shutdown1(public_ip,driver,my_logger):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
         check=ssh.connect(public_ip,username="root", password="baadal123")    
         return 1
    except:
	    my_logger.debug("error in connection") 
	    driver.find_element_by_xpath("//input[@type='button']").click()
	    driver.refresh()
	    path=driver.find_element_by_xpath("//a[@href='/baadal/admin/sanity_check']").click()
	    return 0 

def shutdown_test(driver,xml_child,xml_sub_child,my_logger):
    data = vm_list_my_vm(driver,xml_child,xml_sub_child,my_logger) #get public ip of vm
    if data!=['', '','','']:
        vm_id=data[0][3:]
        vm_name=data[1][0:]
	public_ip=data[2][0:]
    public_ip=mapping(public_ip)
    public_ip=str(public_ip)
    shutdown_baadal(driver,my_logger)
    check_baadal_shutdown1(public_ip,driver,my_logger)

######################################################################## sanity check ############################################################################################   
def list_host(xml_child,xml_sub_child,driver,host_ip,my_logger):
    path_col="//table[@id='hostdetails']/tbody/tr/td"
    path_row="//table[@id='hostdetails']/tbody/tr"
    path_header="//table[@id='hostdetails']/tbody/tr/th"
    if isTablePresent(driver,xml_child,path_col,my_logger):
        countc=0
        c_count=0
        row_count=1
        select=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Name":
                host_name_no=count
            if hdata.text=="IP":
                host_ip_no=count
	    if hdata.text=="Status":
                status_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==host_name_no:
                host_name=data.text  
            if c_count%col_count==host_ip_no:
            	if data.text== host_ip:
                   select+=1
            if c_count%col_count==status_no:
                status=data.text              
            if (c_count%col_count==col_count-1):
                  row_count+=1	  
                  if select:
                     path="//table[@id='hostdetails']/tbody/tr["+str(row_count)+"]/td/a"
              	     driver.find_element_by_xpath(path).click()
                     if click_on_dialogbox(driver):
                         time.sleep(10)
                         driver.refresh()
                     break
            c_count+=1

def list_my_vm(driver,xml_child,xml_sub_child,vm_name,my_logger):
    data2=[]
    path_col="//table[@id='myvms']/tbody/tr/td"
    path_row="//table[@id='myvms']/tbody/tr"
    path_header="//table[@id='myvms']/thead/tr/th"
    path=driver.find_element_by_xpath("//a[@href='/baadal/user/list_my_vm']").click()
    if isTablePresent(driver,xml_child,path_col,my_logger):
        c_count=0
        select=0
        select_row=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="Owner":
                user_name_no=count
            if hdata.text=="Host":
                host_no=count
            if hdata.text=="Private IP":
                private_no=count
            if hdata.text=="Public IP":
                public_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==vm_name_no:
                vm_name1=data.text
                if vm_name1 in vm_name:
                    select=1
            if c_count%col_count==user_name_no:
                for username in username_list:
                    if username==data.text:
                          user_name=data.text
                          select_row=1
                          break
            if c_count%col_count==host_no:
                host=data.text
            if c_count%col_count==public_no:
                public_ip=data.text
            if c_count%col_count==private_no:
                private_ip=data.text
            if (c_count%col_count==col_count-1):
                if select_row and select :
                    break          
            c_count+=1
    if select_row and select :
        data2.insert(0,private_ip)
        data2.insert(1,host)
        data2.insert(2,public_ip)
    else:
        data2.insert(0,'')
        data2.insert(1,'')
        data2.insert(2,'')
    return data2

            
def check_sanity_table(xml_child,xml_sub_child,driver,host_ip,vm_name,my_logger):  	
    print host_ip
    host_no=host_ip[7:]
    path_col="//div[@id='sanity_check_table']/table/tbody/tr/td"
    path_row="//div[@id='sanity_check_table']/table/tbody/tr"
    path_header="//div[@id='sanity_check_table']/table/tbody/tr/th"
    if isTablePresent(driver,xml_child,path_col,my_logger):
        print "host_list table present"
        countc=0
        c_count=0
        row_count=1
        select=0
        select_vm=0
        select_host=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Host":
                host_name_no=count
            if hdata.text=="Message":
                msg_no=count
            if hdata.text=="VM Name":
                vm_name_no=count
            if hdata.text=="Status":
                status_no=count
            if hdata.text=="Operations":
                operation_no=count			
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==msg_no:
                msg=data.text   
            if c_count%col_count==vm_name_no:
                vm_name1=data.text
                if vm_name in vm_name1:
                    select_vm=1
            if c_count%col_count==operation_no:
                operation=data.text
            if c_count%col_count==status_no:
                status=data.text 
                host_status=xml_sub_child.get("status")
                if host_status in status:
                    select_host=1                 
            if (c_count%col_count==col_count-1):
                row_count+=1
                if select_vm:
                        logger.debug("VM Name:" + vm_name1 + "  Status:" + status)
                        if msg in "VM not found":
                            if operation in "Delete VM Info":
                                path="//div[@id='sanity_check_table']/table/tbody/tr["+str(row_count)+"]/td/a"  
                                driver.find_element_by_xpath(path).click()
                                #driver.find_element_by_link_text("Sanity Check").click()
                                #check_sanity_table(xml_child,xml_sub_child,driver,host,my_logger)
                                break
                        if "VM is on expected host" in msg :
                            data=list_my_vm(driver,xml_child,xml_sub_child,vm_name,my_logger)
                            if data!=['', '','','']:
                                private_ip=data[0][0:]
                                host_ip=data[1][0:]
                                public_ip=data[2][0:]
                            host_ip=str(host_ip)
                            public_ip=mapping(public_ip)
                            public_ip=str(public_ip)
                            if public_ip!='Not Assigned':
                                ssh = paramiko.SSHClient()
                                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                if ssh.connect(public_ip,username="root", password="baadal123"):
                                   logger.debug("SSH True " + vm_name)
                                else:
                                   logger.debug("SSH False " + vm_name)
                                ssh.close()
                            break
                        if msg in "Orphan, VM is not in database":
                            if operation in "Add Orphan VM":
                                  path="//div[@id='sanity_check_table']/table/tbody/tr["+str(row_count)+"]/td/a"
                                  print path
                                  driver.find_element_by_xpath(path).click()
                                  break
            c_count+=1
    
def click_sanity(driver,xml_sub_child,my_logger):
    logger.debug("Inside click_sanity")
    isScroll(driver, xml_sub_child,my_logger)
    driver.find_element_by_link_text("Sanity Check").click()
    driver.find_element_by_xpath("//div/form/select/option[@value='0']").click()
    driver.find_element_by_xpath("//div/form/a/span[@class='icon-refresh']").click()

def check_host_state(driver,xml_child,xml_sub_child,my_logger):
    logger.debug("inside check_host_state***--")
    logger.debug("check_host_state")
    data=vm_list_all_vm(xml_child,xml_sub_child,driver,my_logger) 
    if data!=['', '','','']:
        vm_name=data[1][0:]
        host=data[2][0:]
    logger.debug("After vm_list_all_vm")
    isScroll(driver, xml_sub_child,my_logger)
    driver.find_element_by_link_text("Configure System").click()
    isScroll(driver, xml_sub_child,my_logger)
    driver.find_element_by_xpath("//a[@href='/baadal/admin/host_details']").click()
    logger.debug("After clicking host_details")
    list_host(xml_child,xml_sub_child,driver,host,my_logger)
    logger.debug("Entering checkPendingTask")
    checkPendingTask(driver)
    logger.debug("Back to check host state")
    click_sanity(driver,xml_sub_child,my_logger)
    time.sleep(6)
    logger.debug("After Putting Host Down")
    check_sanity_table(xml_child,xml_sub_child,driver,host,vm_name,my_logger)
    driver.find_element_by_xpath("//a[@href='/baadal/admin/host_details']").click()
    time.sleep(6)
    list_host(xml_child,xml_sub_child,driver,host,my_logger)


# Function to create many VM's in a particular host then put the host to maintainance mode for sanity check
def main_host_check(driver,xml_child,xml_sub_child,my_logger):
    create_many_vm(driver,xml_child,xml_sub_child,my_logger)
    host_ip_given=str(xml_sub_child.text)
    click_sanity(driver,xml_sub_child,my_logger)
    logger.debug("Before Putting Host Down")
    data_list=get_from_sanity(driver,xml_child,host_ip_given,my_logger)
    isScroll(driver, xml_sub_child,my_logger)
    driver.find_element_by_link_text("Configure System").click()
    put_a_host_down(driver,xml_child,xml_sub_child,my_logger)
    checkPendingTask(driver)
    #check sanity
    print "All VM's have completed migration or failed"
    logger.debug("After Putting Host Down")
    for data in data_list:
        print "VM vame : "+data
        xpath="//a[@href='/baadal/user/list_my_vm']"
        if(isPresent(driver,xpath)):
            driver.find_element_by_xpath(xpath).click()
            time.sleep(3)
            click_sanity(driver,xml_sub_child,my_logger)
            time.sleep(5)
            check_sanity_table(xml_child,xml_sub_child,driver,host_ip_given,data,my_logger)
    put_a_host_down(driver,xml_child,xml_sub_child,my_logger)

# Function to find vm names that are present in the host with given host_ip
def get_from_sanity(driver,xml_child,host_ip_given,my_logger):
    host_given="host"+str(host_ip_given[7:])
    print "host_given: "+host_given
    path_col="//div[@id='sanity_check_table']/table/tbody/tr/td"
    path_header="//div[@id='sanity_check_table']/table/tbody/tr/th"
    data1=[]
    if isTablePresent(driver,xml_child,path_col,my_logger):
        c_count=0
        select_host=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Host":
                host_name_no=count
            if hdata.text=="VM Name":
                vm_name_no=count
            if hdata.text=="Status":
                status_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==host_name_no:
                host_name=data.text
                if host_name==host_given:
                    select_host=1
            if c_count%col_count==vm_name_no:
                vm_name=data.text
            if c_count%col_count==status_no:
                status=data.text
            if (c_count%col_count==col_count-1):
                if select_host:
                    logger.debug("VM Name:" + vm_name + "  Status:" + status)
                    data1.append(vm_name)
                select_host=0
            c_count+=1
    return data1

# put host whose IP=host_ip_given to maintainence mode
def put_a_host_down(driver,xml_child,xml_sub_child,my_logger):
    logger.debug("Inside put_a_host_down")
    host_ip_given=str(xml_sub_child.text)
    isScroll(driver, xml_sub_child,my_logger)
    driver.find_element_by_xpath("//a[@href='/baadal/admin/host_details']").click()
    time.sleep(5)
    list_host(xml_child,xml_sub_child,driver,host_ip_given,my_logger)

# Function to create many Vm's on a host
# xml_subchild contains the host ip where a particular vm is to be created
def create_many_vm(driver,xml_child,xml_sub_child,my_logger):
    logger.debug("Inside Create many vm")
    host_ip_given=str(xml_sub_child.text)
    logger.debug(host_ip_given)
    createflag=0
    migrateflag=0
    start=time.time()
    end=start+5400
    while start<end:
        driver.find_element_by_link_text('Request VM').click()
        vm_name=create_new_vm(driver,xml_sub_child,xml_child,my_logger)
        print "Name of newly created VM:" + str(vm_name)
        checkPendingTask(driver)
        print "Task is Either completed or failed"
        data=list_my_vm(driver,xml_child,xml_sub_child,vm_name,my_logger)
        host_ip=data[1][0:]
        logger.debug("Host IP of newly created VM :" + host_ip)
        if host_ip=='':
            createflag=createflag+1
            logger.debug("VM creation unsucessful")
            if createflag==3:
                logger.debug("There is some problem in VM creation!Aborting VM creation")
                break
        elif host_ip_given!=host_ip:
            createflag=0
            #Migrate vm to the destination vm
            logger.debug("Migration Required")
            migrateVmTo(driver,xml_child,xml_sub_child,vm_name,my_logger)
            time.sleep(3)
            data1=list_my_vm(driver,xml_child,xml_sub_child,vm_name,my_logger)
            new_host_ip=data[1][0:]
            if host_ip_given!=new_host_ip:
                migrateflag=migrateflag+1
            else:
                migrateflag=0
            if migrateflag==2:
                logger.debug("New VM's are unable to migrate to the destined host.Aborting VM creation")
                break
        else:
            logger.debug("VM is created in the destined host")
            createflag=0
        start=time.time()

################################ Function for creating a new VM. User is OrgAdmin ######################################
def create_new_vm(driver,xml_sub_child,xml_child,my_logger):
    #Request new VM
    vm_id=requestNewVm(driver,xml_sub_child,xml_child)
    #Approve the new VM
    approveNewVm(driver,xml_sub_child,xml_child,vm_id,my_logger)
    return vm_id

################################# Function for requesting a new VM with name as current date and time.######################

def requestNewVm(driver,xml_sub_child,xml_child):
    current_time=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    field = driver.find_element_by_id('request_queue_vm_name')
    field.send_keys(str(current_time))
    driver.find_element_by_xpath("//input[@type='submit']").click()
    return current_time

###############################Function for requesting a new VM with name as current date and time.#########################

def approveNewVm(driver,xml_sub_child,xml_child,vm_name,my_logger):
    driver.find_element_by_partial_link_text('All Pending Requests').click()
    old_field="//table[@id='sortTable1']"
    vm_id=check_vm_in_pending_request_table(driver,xml_sub_child,xml_child,vm_name,old_field,my_logger)
    time.sleep(3)
    driver.find_element_by_xpath("//*[@href='/baadal/admin/approve_request/"+ str(vm_id) +"']").click()
    time.sleep(3)

# Function to migrate a VM with given VM name and Destination HOST
def migrateVmTo(driver,xml_child,xml_sub_child,vm_name,my_logger):
    logger.debug("Inside migrateVmTo function")
    host_ip_given=str(xml_sub_child.text)
    driver.find_element_by_partial_link_text("All VMs").click()
    data1=find_vm_id(driver,xml_child,xml_sub_child,vm_name,my_logger)
    vm_id=data1[0][3:]
    print "VM ID of newly created VM :" + vm_id
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    time.sleep(10)
    #click on migrate vm element
    driver.find_element_by_xpath("//a[@title='Migrate this virtual machine']").click()
    #set the destination host with the given host ip
    el = driver.find_element_by_xpath("//select[@name='selected_host']")
    for option in el.find_elements_by_tag_name('option'):
        if option.text==host_ip_given:
            logger.debug("Option.text= " + option.text)
            option.click()
            time.sleep(5)
            xpath="//input[@name='live_migration']"
            if isPresent(driver,xpath):
                print "Live Migration needed"
                driver.find_element_by_xpath(xpath).click()
                time.sleep(5)
            driver.find_element_by_xpath("//input[@value='Migrate']").click()
            print "Migration request added to queue"
            if checkPendingTask(driver):
                print "VM migration either completed or failed"
            break

############################################# Edit VM Configuration ##########################################################

def pingf(driver,xml_child,xml_sub_child,vm_name,public_ip,my_logger):
	flag=0
        if public_ip=="Not Assigned":
	  logger.debug("VM is not pingable")
	else:
          logger.debug("Trial for VM pingable")
	mine = []
	check=os.system("ping -c4 "+public_ip)
	print check
	if check==0:
	   logger.debug("exist")
	   flag=1
	else:
	   logger.debug("not exist")
	for i in range(1, 2):
	    z =public_ip
            result = os.system("ping -c 1 "+ str(z))
            os.system("clear")
            if result == 0:
	       mine.append(z)
	for j in mine:
            print "host ", j ," is up"
        return flag

def check_vm_configuration(driver,xml_child,xml_sub_child,vm_name,public_ip,my_logger):
    data2=[]
    logger.debug("inside check_vm_configuration")
    logger.debug(public_ip)
    memory_vm=execute_remote_cmd(public_ip,"root","grep MemTotal /proc/meminfo", "baadal123",my_logger, ret_list = False)
    no_of_cpu=execute_remote_cmd(public_ip,"root","grep MemTotal /proc/meminfo", "baadal123",my_logger, ret_list = False)    
    logger.debug("memory_vm : " + str(memory_vm))
    logger.debug("no of cpu : " + str(no_of_cpu))
    data2.insert(0,no_of_cpu)
    data2.insert(1,memory_vm)	
    logger.debug(data2)
    return data2

def check_vm_in_pending_request_tablee(driver,xml_sub_child,xml_child,vm_name,my_logger):
    logger.debug("inside check_vm_in_pending_request_tablee")
    path="//table[@id='sortTable4']/tbody/tr/td"
    counth=0
    user_vm=0
    select_row=0 
    col_count=0
    s_row=0
    ref=0
    user_no=1	
    if isElementPresent(driver,xml_child,path,my_logger):
        field=driver.find_elements_by_xpath("//table[@id='sortTable4']/thead/tr/th")  
        for data in field:
	    if data.text=="VM Name":
		vm_no=counth
	    if data.text=="Requested By":
		user_no=counth
            counth+=1
        total_col=counth
        edit_vm_info=list();
        field=driver.find_elements_by_xpath(path)
        for data in field:
            if col_count%total_col==vm_no:
                if str(data.text)==str(vm_name):
                    print "vm_name" + str(data.text)
                    s_row=1
            if col_count%total_col==user_no:
                usernm=usrnm_list[xml_child[0].text]
                if str(data.text)==usernm:
                    print data.text
                    select_row=1 
	    select_row=1 	   
            if col_count%total_col==(total_col-1) :
                if select_row :
                    if s_row:
                        data1=data.find_element_by_tag_name("a")
                        value=data1.get_attribute("id")
                        vm_id=value[7:]
                        #field=driver.find_element_by_xpath("//table/tbody/tr/td/a[@id='accept_"+str(vm_id)+"']").click()
                        break
            col_count+=1
    
    return vm_id


def approval_reject_request(driver,xml_sub_child,xml_child,vm_name,my_logger):
        logger.debug("inside approval_reject_request ")
	driver.find_element_by_partial_link_text("All Pending Requests").click()
	driver.find_element_by_partial_link_text("Edit Configuration").click()
	field=driver.find_elements_by_xpath("//table[@id='sortTable4']/tbody/tr")
        old_field="//table[@id='sortTable4']"
    	vm_id=check_vm_in_pending_request_tablee(driver,xml_sub_child,xml_child,vm_name,my_logger)
        logger.debug("" + str(vm_id))
	driver.find_element_by_xpath("//*[@href='/baadal/admin/approve_request/"+ str(vm_id) +"']").click()

def edit_vm_conf(driver,xml_sub_child,xml_child,xml_parent,vm_name,my_logger):
    logger.debug("inside edit_vm_conf")
    logger.debug("vm_name : " + str(vm_name))
    vm_info=get_vm_info_frm_mylist(xml_child,xml_sub_child,driver,vm_name,my_logger) #get public ip of vm
    public_ip=vm_info['public_ip']
    vm_id=vm_info['vm_id']
    public_ip=mapping(public_ip)
    public_ip=str(public_ip)
    logger.debug("public_ip : " + str(public_ip))
    logger.debug("vm_id : " + str(vm_id))
    public_ip=mapping(public_ip)
    change_vm_paswd(public_ip)
    data=check_vm_configuration(driver,xml_child,xml_sub_child,vm_name,public_ip,my_logger)
    logger.debug(data) 
    if data!=['','']:
       no_of_cpu=data[0]
       memory_vm_GB=data[1]
    op_name=xml_sub_child.get("op1")
    logger.debug("op_name : " + str(op_name))		
    operation_name=xml_sub_child.text
    flag=pingf(driver,xml_child,xml_sub_child,vm_name,public_ip,my_logger)  
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    other_operation_on_vms(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    time.sleep(60)	
    driver.find_element_by_partial_link_text("My VMs").click() 	
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    operation_on_edit_vm_conf(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    approval_reject_request(driver,xml_sub_child,xml_child,vm_name,my_logger)  
    op_name=xml_sub_child.get("op2")
    logger.debug("op_name : " + str(op_name))
    time.sleep(30) 
    driver.find_element_by_partial_link_text("My VMs").click() 	
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    op_start_vm(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id,my_logger)
    time.sleep(30) 
    data1=check_vm_configuration(driver,xml_child,xml_sub_child,vm_name,public_ip,my_logger)
    if data1!=['','']:
       no_of_cpu1=data1[0]
       memory_vm_GB1=data1[1]
    if no_of_cpu == no_of_cpu1:
       if memory_vm_GB in memory_vm_GB1:
          my_logger.error("Edit VM Configuration failed check logs")
       		
    else:
       my_logger.debug("Edit VM Configuration Done Successfully")
    limit=1
    delete_specific_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    return 


# Edit VM Config End
#getting snapshot id of a VM or #performing snapshot operation on vm Start

def take_vm_snapshot(driver,xml_child,xml_sub_child,data,my_logger):
        vm_id=data[0][3:]
        vm_name=data[1][0:]
        public_ip=data[2][0:]
        status=data[3][0:]
        public_ip=mapping(public_ip)
        op_name=xml_sub_child.get("op")	
        if(status=="Running"):
		takesanapshot(driver,xml_sub_child,xml_child,op_name,vm_name,vm_id,my_logger)
        	time.sleep(300)
        else:
		my_logger.debug("VM is already shutdown operation of file is not performed and snapshot can not be taken")
        time.sleep(300) 
        create_file1(driver,xml_child,xml_sub_child,public_ip,my_logger)
	if(status=="Running"):
		takesanapshot(driver,xml_sub_child,xml_child,op_name,vm_name,vm_id,my_logger)
		time.sleep(300)        
        else:
		my_logger.debug("VM is already shutdown operation of file is not performed and snapshot can not be taken") 
	snap_id=get_vm_snapshot_id(driver,xml_sub_child,xml_child,vm_name,my_logger)
	op_name="revert_to_snapshot"
        click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
        driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"/"+ str(snap_id) +"']").click()	
	flag=check_file1(driver,xml_sub_child,ssh,public_ip,my_logger)
        if flag==1:
		my_logger.debug("VM Snapshot revert is success full")
	else:
		my_logger.debug("VM Snapshot revert is Not success full")
	  #     takesanapshot(driver,xml_sub_child,xml_child,op_name,data)	 +"/"+ str(snap_id)



def takesanapshot(driver,xml_sub_child,xml_child,op_name,vm_name,vm_id,my_logger):	
     click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
     driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"']").click()	

               
def get_vm_snapshot_id(driver,xml_sub_child,xml_child,vm_name,my_logger):
    snap_data=driver.find_elements_by_xpath("//table[@id='vm_snaps']/tbody/tr")
    select_row=0
    snap_id=0
    total_count=3
    for row in snap_data:
	row_data=row.text.split()
        if "User"==row_data[0]:
	    snap_id=row.get_attribute("id")
	    
    return snap_id


def op_snap_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    limit=0
    snap=1
    op_name=xml_sub_child.get("op") 
    if op_name=="snapshot": 
        path="//a[@title='Take VM snapshot']"
    else:
        path=xml_sub_child.get("xpath_snap")
    if isElementPresent(driver,xml_child,path,my_logger): 
	result=snap_result(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name,my_logger)
	
        if op_name=="snapshot":
            driver.find_element_by_xpath(path).click()
        else:
            snapshot_id=get_vm_snapshot_id(driver,xml_sub_child,xml_child,vm_name,my_logger) 
	    if snapshot_id:
                 driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"/"+ str(snapshot_id) + "']").click()
            else:
		my_logger.debug("No snapshot present")
		snap=0
	
        if  (result=="Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot.") | (result=="Snapshot request already in queue.") | (result=="") | (snap==0):
            my_logger.debug(result )
	    limit=0
        else:
            limit=1
    else:
    	my_logger.debug(xml_child.get("value") + ":This functioality is Disabled")  

      
    return limit
def create_file1(driver,xml_child,xml_sub_child,public_ip,my_logger):
    public_ip=mapping(public_ip)
    execute_remote_cmd(public_ip,"root","mkdir /home/testing", "baadal",my_logger, ret_list = False)
    execute_remote_cmd(public_ip,"root","touch /home/testmig/test.txt", "baadal",my_logger, ret_list = False)
    localstring = xml_sub_child.text
    execute_remote_cmd(public_ip,"root","echo " + localstring + " > /home/testmig/test.txt", "baadal",my_logger, ret_list = False)
    execute_remote_cmd(public_ip,"root","vi /home/testmig/test.txt", "baadal",my_logger, ret_list = False)
    return public_ip

def check_file1(driver,xml_sub_child,ssh,public_ip,my_logger):
    print "inside check_file"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())     	 
    ssh.connect(public_ip,username="root", password="baadal123")
    chan = ssh.get_transport().open_session()
    print "fhjshfhjsf"
    chan.exec_command("find /home/testmig/test.txt")
    return_status = chan.recv_exit_status()
    print  "status of find command"
    if return_status==0:
	print "exist"
        
	chan = ssh.get_transport().open_session()
	#Execute the command
	chan.exec_command("ls -a /home/testmig/.test.txt.swp")
	return_status = chan.recv_exit_status() # This will print its return code
        stdin, stdout,stderr=ssh.exec_command("cat /home/testmig/test.txt")
	localstring=stdout.read()
	print localstring
	if (return_status==0):		
	    logger.debug("vm Snapshot taken correctly")
	return 0
    else:
	logger.debug("not exist")
        return 1



def total_snap(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name,my_logger):
    total_user_snap=0
    total_snap=0
    snap_data=driver.find_elements_by_xpath("//table[@id='vm_snaps']/tbody/tr")
    for row in snap_data:
        s_row=row.text.split()
        user=s_row[0]
        if "User"==user:
            total_user_snap+=1
	total_snap+=1
    
    if op_name=="158Migrate VM":
	total=total_snap
    else:
	total=total_user_snap
    return total

#checking snapshot
def snap_result(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name,my_logger):
    op_name=xml_sub_child.get("op")   
    operation_name=op_list[op_name]

    vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    l_snap=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list,my_logger)
 
    length_snap=len(l_snap)
    
    driver.find_element_by_link_text("All VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)    
    total_user_snap=total_snap(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name,my_logger)
    result=snap_db_result(xml_sub_child,op_name,length_snap, total_user_snap,my_logger)
    field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
    print_result(field_text,result,xml_child,my_logger)
    return result



############################################ Grant VNC#################################################

def op_grant_vnc(driver,xml_sub_child,xml_child,vm_name,vm_id,baadal_db,my_logger):
   # baadal_db=db_connection_root()
    msg_string="VNC access already granted. Please check your mail for further details."
    path="//a[@title='Grant VNC Access']"
    if isElementPresent(driver,xml_child,path,my_logger):
	driver.find_element_by_partial_link_text("All VMs").click()
	click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger) 	
	driver.find_element_by_xpath(path).click()
	ele = driver.find_element_by_id("flash_message")
	logger.debug(ele.text)
	if ele.text==msg_string:
		logger.debug(ele.text)
		logger.debug("removing grant permission from vm_id "+vm_id)
		id1=execute_query(baadal_db,'select id from vnc_access where vm_id='+vm_id+' order by id desc limit 1').fetchone()
		id1 = id1[0]
		print id1
		execute_query(baadal_db,my_logger,"update vnc_access set status=%s where id=%s",('inactive',id1))
		baadal_db.commit()
		driver.refresh()
		driver.find_element_by_xpath(path).click() 
	ip,port=get_vnc_ip_and_port(driver,my_logger)
	if ip=="" or port=="":
		my_logger.debug("vnc grant unsuccessful")
		sys.exit("vnc grant unsuccessful")
			
	return

def vnc_access(driver,xml_sub_child,xml_child,vm_name,baadal_db,my_logger):
	op=xml_sub_child.get("op")
        logger.debug("op name is : " + str(op))
	if op=="check_vnc_session":
		check_vnc_access_time(driver,xml_sub_child,xml_child,baadal_db,my_logger)
	elif op=="count_vnc_session":
		count_vnc_session(driver,xml_sub_child,xml_child,vm_name,baadal_db,my_logger)
	return
	
def check_vnc_access_time(driver,xml_sub_child,xml_child,baadal_db,my_logger):
    #USE EXISTING VM HERE
    xpath1="//p/strong"
    data = vm_list_all_vm(xml_child,xml_sub_child,driver,my_logger) #get public ip of vm
    if data!=['', '','','']:
       	vm_id=data[0]
        vm_name=data[1][0:]
        click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
        op_grant_vnc(driver,xml_sub_child,xml_child,vm_name,vm_id,baadal_db,my_logger)
        ele = driver.find_element_by_id("flash_message")
        msg_string="VNC access granted. Please check your mail for further details."
        if ele.text==msg_string:
            logger.debug(ele.text)
            ip,port=get_vnc_ip_and_port(driver,my_logger)
            if ip!="" and port!="":
                temp1 =0
                temp = 0
                time.sleep(900)
                driver.refresh()
                #wait = WebDriverWait(driver,1800)
                listpath1 = driver.find_elements_by_xpath(xpath1)
                for listp1 in listpath1:
                    if "VNC IP" in listp1.text:
                        my_logger.debug("session continues after 900 secs")
                        temp1 =1
                        break
                if temp1!=1:
                    my_logger.debug("session got over before 30 mins")
                    sys.exit()
                my_logger.debug("again sleep for 900secs")	
                time.sleep(900)
                driver.refresh()
                my_logger.debug("extra time for task to complete")
                time.sleep(360)
                driver.refresh()
                listpath1 = driver.find_elements_by_xpath(xpath1)
                for listp1 in listpath1:
                    if "VNC IP" in listp1.text:
                        logger.debug( listp1.text)
                        my_logger.debug("session didnot over in 30 mins extra")
                        temp = 1
                        break
                if temp == 1:
                    my_logger.debug("session didnot over in 30 mins")
                    sys.exit()
                else:
                    my_logger.debug("session got over in 30 mins")
    else:
        my_logger.debug("no vm available for testing")
        sys.exit()
	return

	

def count_vnc_session(driver,xml_sub_child,xml_child,vm_name,baadal_db,my_logger):
	count = 0
	path="//a[@title='Grant VNC Access']"
	data = vm_list_all_vm(xml_child,xml_sub_child,driver) #get public ip of vm
    	if data!=['', '','','']:
        	vm_id=data[0]
        	vm_name=data[1][0:]
	click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
	op_grant_vnc(driver,xml_sub_child,xml_child,vm_name,vm_id,baadal_db,my_logger)
	ele = driver.find_element_by_id("flash_message")
	msg_string1="VNC access granted. Please check your mail for further details."
	msg_string2="VNC access already granted. Please check your mail for further details."
	msg_string3=""
	if ele.text==msg_string1:
		count = 1
		my_logger.debug(ele.text)
		while count<11:
			print "This is "+str(count)+" session"
			ip,port=get_vnc_ip_and_port(driver)
			if ip!="" and port!="":
				my_logger.debug("removing grant permission from vm_id "+vm_id)
				id1=execute_query(baadal_db,'select id from vnc_access where vm_id='+vm_id+' order by id desc limit 1').fetchone()
				id1 = id1[0]
				execute_query(baadal_db,"update vnc_access set status=%s where id=%s",('inactive',id1))
				baadal_db.commit()
				driver.refresh()
				ip,port=get_vnc_ip_and_port(driver)
				if ip=="" and port=="":
					driver.find_element_by_xpath(path).click()
					count =count+1
				else:
					sys.exit("session is still on")
			else:
				sys.exit("session not created"+str(count))
		ele = driver.find_element_by_id("flash_message")
		if count==11 and (ele.text==msg_string1):
			sys.exit("session granted more then 10 times")
					
	else:
		my_logger.debug(ele.text)
	return

def find_vmid_by_vmname_username(driver,xml_sub_child,xml_child,vm_name,my_logger):
	path_col="//table[@id='listallvm']/tbody/tr/td"
    	path_row="//table[@id='listallvm']/tbody/tr"
    	path_header="//table[@id='listallvm']/thead/tr/th"
	if isTablePresent(driver,xml_child,path_col,my_logger):
        	countc=0
        	c_count=0
        	r_count=0
        	select_row=0
        	header_field=driver.find_elements_by_xpath(path_header)
        	count=0
        	for hdata in header_field:
            		if hdata.text=="Name":
                		vm_name_no=count
            		if hdata.text=="Owner":
               			user_name_no=count
            		if hdata.text=="Status":
                		status_no=count
            		count+=1
        	col_count=count
        	field=driver.find_elements_by_xpath(path_col)        
       		for data in field:
            		if c_count%col_count==vm_name_no:
				if data.text==vm_name:
					select_row1=1
            		if c_count%col_count==user_name_no:
                		if data.text in username_list:
                    			user_name=data.text
                    			select_row2=1                   
            		if c_count%col_count==status_no:
               	 		status=data.text                            
            		if (c_count%col_count==col_count-1):
                
	        		if select_row1 and select_row2:
		
                    			if (str(status)==xml_sub_child.get("status")):
                        			field_data=driver.find_elements_by_xpath(path_row)

                        			vm_id=data.get_attribute("id")
                        
                       				countc+=1
                        			break                                          
            		c_count+=1          
	if countc==0:
        	my_logger.debug("No user of testing User.Please Create a VM!!!!")
        	vm_name=""
        	vm_id=""
    	data1.insert(0,vm_id)
    	data1.insert(1,vm_name)
   
    	return data1

def get_vnc_ip_and_port(driver,my_logger):
	xpath1 = "//p"
	listpath = driver.find_elements_by_xpath(xpath1)
	ip=""
	port=""
	temp = 0
	for listp in listpath:
		if "VNC IP:" in listp.text:
			ip = listp.text.split()
			ip = ip[2]
			port = ip[5]
	return ip,port

def verify_sorting(driver,xml_sub_child,xml_child,my_logger):
	table_dict = {'My VMs': '//table[@id="myvms"]', 'All VMs': '//table[@id="listallvm"]', 'VM Utilization': '//table[@id="sortTable1"]'};
	table_page = xml_sub_child.get("page")
	if table_page!="":
		driver.find_element_by_partial_link_text(table_page).click()
		xpath = table_dict[table_page]
		check_column_sorting(xpath,driver,xml_child,my_logger)
	else:
		for key in table_dict:
			driver.find_element_by_partial_link_text(key).click()
			xpath=table_dict[key]
			check_column_sorting(xpath,driver,xml_child,my_logger)
	return

def check_column_sorting(xpath,driver,xml_child,my_logger):
	driver.find_element_by_xpath(xpath)
	path_col=xpath+"/tbody/tr/td"
    	path_row=xpath+"/tbody/tr"
    	path_header=xpath+"/thead/tr/th"
	header_field=driver.find_elements_by_xpath(path_header)
	count =0
	for hdata in header_field:
            	count+=1
        col_count=count
	col_ele_list_sorted = []
	for column in range(1,col_count+1):
		list_of_column_elements = driver.find_elements_by_xpath(path_col+"["+str(column)+"]")
		for col_ele in list_of_column_elements:
			my_logger.debug("adding elements")
			col_ele_list_sorted.append(col_ele.text)
		col_ele_list_sorted.sort()
		sort_and_compare(driver,xml_child,col_ele_list_sorted,path_header,path_col,column,1,my_logger)
		col_ele_list_sorted.sort(reverse=True)
		sort_and_compare(driver,xml_child,col_ele_list_sorted,path_header,path_col,column,2,my_logger)
		
		col_ele_list_sorted = []
				
	return

def sort_and_compare(driver,xml_child,col_ele_list_sorted,path_header,path_col,column,num,my_logger):
	driver.find_element_by_xpath(path_header+"["+str(column)+"]").click()
	sorted_list_of_column_elements = driver.find_elements_by_xpath(path_col+"["+str(column)+"]")
	print col_ele_list_sorted
	for ele in range(len(sorted_list_of_column_elements)):
		if sorted_list_of_column_elements[ele].text!=col_ele_list_sorted[ele]:
			my_logger.debug("Sorting not done poperly"+str(num))
			my_logger.debug(xml_child.get("value")+": Sorting not done poperly")
			sys.exit()
	my_logger.debug("correct sorting"+str(num)+" time")
	my_logger.debug(xml_child.get("value")+": Correct sorting"+str(num)+" time")

display.stop()

################################# Wake on LAN Testing ###########################

def wake_on_lan(driver,xml_child,xml_sub_child,table_path,my_logger):
      logger.debug("inside wake on lan")
      if isElementPresent(driver,xml_child,table_path,my_logger):
         logger.debug("return back to checking table : ")
         data=vm_list_host_detail(xml_child,xml_sub_child,driver,my_logger)
         logger.debug(data)
         if data!=['','','','']:
               vm_id=data[0][3:]
               vm_name=data[1][0:]
               owner_name=data[2][0:]
               host_name=data[3][0:]
               logger.debug("host name is : " + str(host_name))
               logger.debug("host name is : " + str(vm_id))
               op_name=xml_sub_child.get("op")    
               operation_name=op_list[op_name]
               logger.debug("operation_name is "+ str(operation_name))
               if vm_id !="":
                   click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
                   operation_on_wol(driver,xml_sub_child,xml_child,vm_name,vm_id,host_name,my_logger)
         else:       
               logger.debug(xml_sub_child.get("print_mode")) 
	       test_script(48)
      else:
    	my_logger.debug(xml_child.get("value") + ":No VM exists.So,to perform this operation please create a VM.")
      return 


#performing wake on lan operation on vm
def operation_on_wol(driver,xml_sub_child,xml_child,vm_name,vm_id,host_first,my_logger):
    logger.debug("inside operation_on_migrate_vm")
    host_second=migrate_to_host(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    if host_second=="":
        return 0
    logger.debug("second_host_name : " +str(host_second))
    op_name=xml_sub_child.get("op")
    op_name=xml_sub_child.get("op")
    operation_name=op_list[op_name]
    logger.debug("Operation_name : " +str(operation_name))
    flag=check_task_task_report(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    logger.debug("task in complted_task table:" + str(flag))
    if flag:
            flag=wol_host_op(driver,xml_sub_child,xml_child,vm_name,vm_id,host_first,host_second,operation_name,my_logger)
            logger.debug("what next")
            driver.find_element_by_partial_link_text("All VMs").click()
            if check_migration_result(driver,xml_sub_child,xml_child,vm_name,vm_id,host_first,host_second,my_logger):
               logger.debug("task in pogress")
               limit= migrate_on_specific_host(driver,xml_sub_child,xml_child,vm_name,vm_id,host_first,my_logger)
               driver.find_element_by_partial_link_text("All VMs").click()
               if check_task_task_report(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger):
                   driver.find_element_by_partial_link_text("All VMs").click()
                   if check_migration_result(driver,xml_sub_child,xml_child,vm_name,vm_id,host_second,host_first,my_logger):
                       my_logger.debug(" Success: Wake on Lan successfully tested " )
                   else:
                       my_logger.debug(" Wake on Lan test is unsuccessfull, vm is not migrated to it's original host" )     
    else:
        my_logger.debug("Migration operation unsuccessfull:  wake on lan testing can't be performed")
    return 0

def wol_host_op(driver,xml_sub_child,xml_child,vm_name,vm_id,host_first,host_second,operation_name, my_logger):
    driver.find_element_by_partial_link_text("All VMs").click()
    i=5
    while i :
         if check_migration_result(driver,xml_sub_child,xml_child,vm_name,vm_id,host_first,host_second,my_logger):
            logger.debug("shutting down the host")
            flag=shut_down_host(driver,xml_sub_child,xml_child,host_first,vm_name,operation_name,my_logger)
            logger.debug("restarting the host")
            return True
         i-=1
         time.sleep(30)
         driver.refresh()
    return True


def shut_down_host(driver,xml_sub_child,xml_child,host_first,vm_name,operation_name,my_logger):
    driver.find_element_by_partial_link_text("Configure System").click()
    driver.find_element_by_partial_link_text("Configure Host").click()
    path_row="//table[@id='hostdetails']/tbody/tr"
    path_col="//table[@id='hostdetails']/tbody/tr/td"
    path_header="//table[@id='hostdetails']/tbody/tr/th"
    if isTablePresent(driver,xml_child,path_col,my_logger):
        row_count=0
        count=0
        c_count=0
        host=""
        host_cm=0
        host_status=""
        header_field=driver.find_elements_by_xpath(path_header)
        for hdata in header_field: 
            if hdata.text=="IP":
                host_num=count
            if hdata.text=="Commands":
                host_cmd=count
            if hdata.text=="Status":
                host_status_no=count
            count+=1
        logger.debug("host_num is : " + str(host_num))
        logger.debug("host_cmd is : " + str(host_cmd))
        logger.debug("host_status is : " + str(host_status_no))
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==host_num:
                host=data.text   
            if c_count%col_count==host_cmd:
                host_cm=data.get_attribute("id")
                logger.debug("host cm is : " + str(host_cm))
            if c_count%col_count==host_status_no:
                host_status=data.text
                logger.debug("host status is : " + str(host_status))           
            if (c_count%col_count==col_count-1):
                  logger.debug("host is : " + str(host))
                  logger.debug("host first is : " + str(host_first))
                  row_count+=1
                  logger.debug("row_count is : " + str(row_count))
                  if (host in host_first) & (host_status=="Up"):
                     logger.debug("inside host checking if block  " + str(host_cm))
                     driver.find_element_by_xpath('//table/tbody/tr/td[@id="%s"]/a'%host_cm).click()
                     logger.debug("sleep for 60 seconds")
                     time.sleep(30)
                     logger.debug("shutting down the host")
                     click_on_dialogbox(driver)
                     flag=check_task_task_report(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
                     logger.debug("what next")
                     #driver.find_element_by_partial_link_text("Configure System").click()
                     #time.sleep(30)
                     logger.debug("what next")
                     driver.find_element_by_partial_link_text("Configure Host").click()
                     logger.debug("sleep for 60 seconds")
                     driver.find_element_by_xpath('//table/tbody/tr/td[@id="%s"]/a[@title="Shut down this host"]'%host_cm).click()
                     logger.debug("sleep for 60 seconds")
                     time.sleep(60)
                     logger.debug("restarting the host")
                     driver.find_element_by_xpath('//table/tbody/tr/td[@id="%s"]/a[@title="Host is fit now."]'%host_cm).click()
                     return True
            c_count+=1            
    return True

def check_migration_result(driver,xml_sub_child,xml_child,vm_name,vm_id,host_first,host_second,my_logger):
    logger.debug(" inside check_migration_result")
    path_row="//table[@id='listallvm']/tbody/tr"
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_header="//table[@id='listallvm']/thead/tr/th"
    if isTablePresent(driver,xml_child,path_col,my_logger):
        count=0
        host=""
        c_count=0
        vm_name1=""
        header_field=driver.find_elements_by_xpath(path_header)
        for hdata in header_field: 
            if hdata.text=="Name":
                vm_name_num=count
            if hdata.text=="Host":
                host_num=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==vm_name_num:
                vm_name1=data.text
            if c_count%col_count==host_num:
                host=data.text   
            if (c_count%col_count==col_count-1):
                  if (vm_name1==vm_name) & (host in host_second):
                      logger.debug("vm_name:" +str(vm_name)+ "host:"+str(host_second))
                      return True
            c_count+=1 
        return False

####### redundant functions also in test.py ############## 

def migrate_to_host(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    logger.debug("inside_migrate_operation")
    op_name=xml_sub_child.get("op")
    limit=0
    op_name=xml_sub_child.get("op")
    operation_name=op_list[op_name]
    operation_name
    path="//a[@title='Migrate this virtual machine']"
    host_second=""
    if isElementPresent(driver,xml_child,path,my_logger):
	driver.find_element_by_partial_link_text("All VMs").click()
        vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
        logger.debug("click_migrate_button")
	driver.find_element_by_xpath("//a[@title='Migrate this virtual machine']").click()
	if xml_sub_child.get("live")=="yes":
           message=message_flash(driver,xml_sub_child,xml_child,my_logger)
           message=str(message)
           if message=="No host available right now":
                logger.debug("No host available right now. Please start/create the new host")
                sys.exit()
           else:
                host_second= driver.find_element_by_xpath("//table/tbody/tr/td/select[@name='selected_host']/option").text
                print host_second
           	driver.find_element_by_xpath("//input[@name='live_migration']").click()
	   	driver.find_element_by_xpath("//input[@value='Migrate Host']").click()       
                result="Your task has been queued. please check your task list for status. "
                field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
                print_result(field_text,result,xml_child, my_logger)
                limit=1
	print "migration done"
    else:
        my_logger.debug("element not found  ")
    return host_second    
