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
from helper import xml_connect
from helper import db_connection
from selenium.webdriver.common.keys import Keys
import sys
import time


#creating a logger for logging the records
logger = logging.getLogger("web2py.app.testapp")

#creating connection to remote database
baadal_db=db_connection() 


#creating connection to remote system
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#################################################################################################################
#                             The main test function for stress
                                           #
#################################################################################################################
def stress_script(m):
    
    
    logging.debug("inside thread: "+str(m))
    
    root = xml_connect()
    i=m
    for j in xrange(0,len(root[i])): 
        driver = webdriver.Remote(
       command_executor='http://127.0.0.1:4444/wd/hub',
       desired_capabilities=DesiredCapabilities.FIREFOX)#connect to selenium server
        driver.implicitly_wait(10)
        driver.get(root.get("url")) #url of the page to be hit 
        driver.find_element_by_link_text(root.get("href")).click()
        image=0
        for k in xrange(0,len(root[i][j])):
            field_type=root[i][j][k].get("type")
            xml_parent=root[i]
            xml_child=root[i][j]
            xml_sub_child=root[i][j][k]
					
            if field_type=="input": #checking for text fields
                vm_name1=isInput(driver,xml_sub_child)
                      
            elif field_type=="read_only": #checking for submit button
                isReadOnly(driver, xml_parent,xml_child,xml_sub_child)
						
            elif field_type=="submit": #checking for submit button
                isSubmit(driver, xml_parent,xml_child,xml_sub_child)
                driver.implicitly_wait(10)
						
            elif field_type=="button":#checking for button
                time.sleep(3)
                isButton(driver,xml_sub_child)
					
            elif field_type=="scroll":#scrolling the page up/down
                isScroll(driver,xml_sub_child)
				 		
            elif field_type=="href":
                isHref(driver,xml_sub_child)#clicking on the hyper link
                        
            elif field_type=="select":
                isSelect(driver,xml_sub_child)# selecting from dropdown menu
			 	
            elif field_type=="table":
                isTable(driver,xml_parent,xml_child,xml_sub_child)#checking for data in table
                         
            elif field_type=="img":#checking for sett
                table_path=xml_sub_child.get("path")
                isImage(driver,xml_child,xml_sub_child,table_path,image)
                 
								
            elif field_type=="check_tables":#cheking for host table
                isCheckTable(driver,xml_parent,xml_child,xml_sub_child,vm_name)
                
            elif field_type=="wait":
                isWait(driver,xml_parent,xml_child,xml_sub_child)#checking for data in table
                    
            elif field_type=="check_data":
                 operation_name=xml_sub_child.text
                 check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name)#checking for data in table
                        				
            else:
                logging.debug("report problem") #logging the report
                
            if k==5 | k==6:
                vm_name=vm_name1
        driver.close()#disconnect from server


def stress_test_script():
    for m in range(0,5):
        root = xml_connect()
        total_scripts=root.get("total_scripts")
        test_no=m%(int(total_scripts)-1)
        thread.start_new_thread( stress_script,(test_no,) )
        thread.start_new_thread( stress_script,(test_no,) )
        thread.start_new_thread( stress_script,(test_no,) )
        thread.start_new_thread( stress_script,(test_no,) )
        thread.start_new_thread( stress_script,(test_no,) )
        thread.start_new_thread( stress_script,(test_no,) )
        thread.start_new_thread( stress_script,(test_no,) )
        thread.start_new_thread( stress_script,(test_no,) )
        
        logging.debug("Thread: "+str(m))
        
    return


def graph_test(test_case_no):
#Checking memory utilizations
    print test_case_no
    root = xml_connect()
    i=int(test_case_no)
    xml_sub_child=root[i-1][0][0]
    xml_child=root[i-1][0]   
    ssh.connect(xml_child.get("ip_add"), username=xml_child.get("usrnam"), password=xml_child.get("password"))   
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_init_data"))
    initial_data=stdout.readlines()
    
    current_time=datetime.datetime.now()
   
    ini_data=str(initial_data[2])
    init_data=ini_data.split()
    ssh.connect("10.208.21.113", username="root", password="baadal_test")   
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_run_prgrm"))
    data=stdout.readlines()
    time.sleep(600)    
    ssh.connect(xml_child.get("ip_add"), username=xml_child.get("usrnam"), password=xml_child.get("password"))  
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_finl_data"))
    final_data=stdout.readlines()
    fin_data=str(final_data[2])
    finl_data=fin_data.split()
    print_graph_result(finl_data,init_data,xml_child)
    
def print_graph_result(finl_data,init_data,xml_child):
    logger.debug(xml_child.get("value") +" Initial_data:"+ str(init_data))
    logger.debug(xml_child.get("value") +" Final_data:"+ str(finl_data))
    for i in range(1,7):
        if init_data[i]=="-nan":
            i_data=0
        else:
            i_data=init_data[i]      
        diff=float(finl_data[i])-float(i_data)
        logger.debug(xml_child.get("value") +": Differnce "+ str(diff)) 
        if finl_data[i]=="-nan":
            logger.debug(xml_child.get("value") +':  '+"Incorrect Data")
        else :
            if diff<=0:
                logger.debug(xml_child.get("value") +':  '+"Incorrect Data") 
            else:
                logger.debug(xml_child.get("value") +':  '+"Correct Data")   


def print_graph(finl_data,xml_child):
    for i in range(1,7):
        if finl_data[i]=="-nan":
            logger.debug(xml_child.get("value") +':  '+"Correct Data")
        else :
            logger.debug(xml_child.get("value") +':  '+"Incorrect Data")  
#################################################################################################################
#                                       The main test function  for unit testing                                            #
#################################################################################################################
		
def test_script(test_case_no):
    print test_case_no
    root = xml_connect()
    num=int(test_case_no)
    vm_status=1
    if root[num-1].get("id")==test_case_no:
       
        i=num-1
        vm_name=""  
        for j in xrange(0,len(root[i])):
        
            driver = webdriver.Firefox()#connect to selenium server
            driver.implicitly_wait(10)
            driver.get(root.get("url")) #url of the page to be hit 
            driver.find_element_by_link_text(root.get("href")).click()
            image=0
            for k in xrange(0,len(root[i][j])):
                if vm_status:
                    field_type=root[i][j][k].get("type")
                    xml_parent=root[i]
                    xml_child=root[i][j]
                    xml_sub_child=root[i][j][k]
                	
                    if field_type=="input": #checking for text fields
                        vm_name1=isInput(driver,xml_sub_child)
                      
                    elif field_type=="read_only": #checking for submit button
                        isReadOnly(driver, xml_parent,xml_child,xml_sub_child)
						
                    elif field_type=="submit": #checking for submit button
                        time.sleep(3)
                        
                        isSubmit(driver, xml_parent,xml_child,xml_sub_child)
                        
	
                    elif field_type=="scroll":#scrolling the page up/down
                        isScroll(driver,xml_sub_child)
				 	
                    elif field_type=="clear":#Clearing text from textarea 
                        isClear(driver,xml_sub_child)  
                        	
                    elif field_type=="href":
                        isHref(driver,xml_sub_child,xml_child)#clicking on the hyper link
                    
                    elif field_type=="select":
                        isSelect(driver,xml_sub_child)# selecting from dropdown menu
                    
                    elif field_type=="sanity_table":
                        isSanityCheck(driver, xml_parent, xml_child, xml_sub_child)# checking for data in  sanity table
			 	
                    elif field_type=="table":
                        isTable(driver,xml_parent,xml_child,xml_sub_child)#checking for data in table
                         
                    elif field_type=="img":#checking for setting image
                        table_path=xml_sub_child.get("path")
                        vm_name2=isImage(driver,xml_child,xml_sub_child,table_path)
				
                    elif field_type=="check_tables":#cheking for host table
                        isCheckTable(driver,xml_parent,xml_child,xml_sub_child)
                
                    elif field_type=="wait":
                        isWait(driver,xml_parent,xml_child,xml_sub_child)#checking for data in table
                    
                    elif field_type=="check_data":
                        isCheckdata(driver,xml_parent,xml_child,xml_sub_child,vm_name)#checking for data in table
                 
                    elif field_type=="task_table":
                         operation_name=xml_sub_child.text
                         vm_status1=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name)#checking for data in table
                
                    elif field_type=="attach_disk":
                        operation_name=xml_sub_child.text
                        attack_disk(driver,xml_sub_child,xml_child,vm_name,operation_name)#checking for data in table
                           				          				          				
                    else:
                        logging.debug("report problem") #logging the report
                    if k==33:
                        vm_status=vm_status1
                    if k==5:
                        vm_name=vm_name1
            driver.close()#disconnect from server        
        if vm_status==0:
            logger.debug("Your VM has not created.Please Check it!!!Either its in failed or pending task table!!!")
        

#################################################################################################################
#                                        Function  for Network testing                                            #
#################################################################################################################           
def packages_install_test(test_case_no): 
    root = xml_connect()
    xml_sub_child=root[test_case_no-1][0][0]
    print test_case_no
    xml_child=root[test_case_no-1][0]    
    ssh.connect(xml_child.get("ip_add"), username=xml_child.get("usrnam"), password=xml_child.get("password"))    
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_flush"))
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_pkg"))
    pkg_list=xml_sub_child.get("pkg_lst").split()
    for pkg in  pkg_list:
        cmd=xml_sub_child.get("cmd_srch") + " " +str(pkg)
        stdin, stdout, stderr =ssh.exec_command(cmd)	
        data=stdout.readlines()
        if data:
            logger.debug(xml_child.get("value") +': '+pkg +" :software has installed properly") 
            
        else:
            logger.debug(xml_child.get("value") +': '+pkg +" :software has not installed properly") 
 
                                                                                                                                                                        

                                         
def check_stat_on_host():
    import libvirt
    import commands
    import MySQLdb as mdb
    conn = libvirt.open("qemu+ssh://root@" + '10.208.21.70' + "/system")
    
    db=mdb.connect("10.208.21.111","baadaltesting","test_baadal","baadal")
    cursor1=db.cursor()
    cursor1.execute("select vm_name,vm_data.status,host_id from vm_data join host where host.id=vm_data.host_id and host_ip='10.208.21.70'")
    output=cursor1.fetchall()
    datas=str(output)
    lists=datas.split("), (")
    col_count=len(lists)
    print lists
    print col_count
    for i in range(0,col_count):
        datass=lists[i].split(",")
        newstr = datass[0].replace("'", "")
        if i==0:
            newstr=newstr.replace("((","")
        for id in conn.listDomainsID():
            dom = conn.lookupByID(id)
            infos = dom.info()
            if newstr==dom.name():
                print newstr
                print 'Name =  %s' % dom.name()
                print 'State = %d' % infos[0]
                print datass[1]
                if (((datass[1]==" 5L") & (infos[0]==1)) | ((datass[1]==" 6L") & (infos[0]==3))):
                    print "yes"                                           
 
#################################################################################################################
#                         Function for mailing
                                           #
#################################################################################################################    
def send_mail():
                                          
    from gluon.tools import Mail
    mail = Mail()
    mail.settings.server = 'smtp.iitd.ernet.in:25'
    mail.settings.sender = 'monika28.visitor@cse.iitd.ernet.in'
    mail.settings.login = 'jyoti11.visitor@cse.iitd.ernet.in:jyoti_saini'
    mail.send(to=['monika71990@gmail.com'],
          subject='hello',
          # If reply_to is omitted, then mail.settings.sender is used
          message="Error")
###############################################################################################################
#                             Functions used by the input field functions                                     #
###############################################################################################################		

# checking whether a table is present on the webpage
def isElementPresent(driver,xml_child,xpath):
    try:
        driver.find_element_by_xpath(xpath)
   
        return 1
    except :
        logger.debug(xml_child.get("value") +': Result:no element exists')
        return 0
   
        	


# checking whether an element is present on the webpage
def isTablePresent(driver,xml_child,xpath):
    try:
        driver.find_element_by_xpath(xpath)
        
        return 1
    except:
        logger.debug(xml_child.get("value") +': Result:no table exists')
        return 0	
   

				
#checking whether front end data and daatabase entries are equal and printing the result 		
def print_result(field_text,result,xml_child):
	
	query_result=str(result)
        logger.debug("screen=  "+str(field_text) )
        logger.debug("db=      "+query_result)
	if str(field_text)==str(query_result):
		logger.debug(xml_child.get("value") +': Result:correct input') 
		
	else:
		logger.error(xml_child.get("value") +': Result:Incorrect input')

	return 

	
#open error link on differnet page			
def open_error_page(driver,xml_parent,text,row_count):
	(driver.find_elements_by_link_text(text))[row_count].click()
	field=driver.find_element_by_xpath(xml_parent.get("error_page"))
	error_message=field.text
	driver.find_element_by_link_text(xml_parent.get("error_page_close_text")).click()
	return error_message

	
#converting vm status bits into status text			
def admin_vm_status(status):
    vm_status=["Running","Paused","Shutdown"]
    if status==2:
        result=vm_status[0]
    if status==3:
        result=vm_status[1]
    if status==4:
        result=vm_status[2]
    return result 

    	
#converting host status bits into status text    	    	    	
def host_status(status):
	host_status={0:"Down",1:"Up",2:"Maintenance"}	
	if status==0:
		result=host_status[0]
	if status==1:
		result=host_status[1]
	if status==2:
		result=host_status[2]
	return result

		
#converting  status bits into status text	
def org_task_status(status):
    task_status={0:"Approve  |  Reject",1:"Waiting for admin approval",2:"Remind Faculty"}
    if (status==0) | (status==2):
        result=task_status[0]
    if (status==3) :
        result=task_status[0]
    if (status==4) :
        result=task_status[1]
    if (status==1) :
        result=task_status[2]
    return result
    

        
    
#for executing sql-query			
def execute_query(sql_query,arg=None):
    cursor=baadal_db.cursor()
    if arg==None:
        cursor.execute(sql_query)
    else:
        cursor.execute(sql_query,arg)
    return cursor


#perform action on setting button of vm's
def click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id):
    print vm_id
    id=xml_sub_child.get("id")
    driver.find_element_by_xpath("//*[@href='/user/"+ str(id) +"/"+ str(vm_id) +"']").click()
    logger.debug(xml_child.get("value") +': Result:Setting button works properly') 
    return
    
    
#open dialogbox when error occurs in falied tasks            
def click_on_dialogbox(driver):
    alert = driver.switch_to_alert()
    alert.accept()
    return
    
#add extra disk to a VM
def add_extra_disk(driver,xml_sub_child,xml_child,vm_name,vm_id):
    isInput_add(driver, xml_sub_child)
    value=xml_sub_child.get("add_button")
    isButton_add(driver, xml_sub_child,value)
    
    return
    
#add additional user to a VM
def add_user(driver,xml_sub_child,xml_child,vm_name,vm_id):
    isInput_add(driver, xml_sub_child)
    value=xml_sub_child.get("add_submit")
    isButton_add(driver, xml_sub_child,value)
    time.sleep(3)
    status=isElementPresent(driver,xml_child,value)
    print status
    if status==1:
        logger.error("User is already VM user")
        user=0
    else:
        val=xml_sub_child.get("add_button")
        isButton_add(driver, xml_sub_child,val)
        user=1
    return user

       


#getting snapshot id of a VM

def get_snapshot_id(driver,xml_sub_child,xml_child,vm_name):
    query_result=execute_query( xml_sub_child.get("query_snap_id"),(str(vm_name))).fetchone()
    field=driver.find_elements_by_xpath(xml_sub_child.get("xpath_snap"))
    for t in field:
        if str(query_result[1]) in t.text:
            snap_id=query_result[0]
    return snap_id


# performing attach disk operation on vm 
def attack_disk(driver,xml_sub_child,xml_child,vm_name,operation_name):
    print vm_name
    query_result=execute_query("select id,status from request_queue where vm_name=%s",(str(vm_name))).fetchone()
    baadal_db.commit()
    query_result=execute_query("select id from vm_data where vm_name=%s",(str(vm_name))).fetchone()
    baadal_db.commit()
    if query_result!=():
        query_result=execute_query("select id from vm_data where vm_name=%s",(str(vm_name))).fetchone()
        print query_result
        vm_id=query_result[0]
        print vm_id
        click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
        click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id)
    return
          
        
#getting user id of a user access to a VM                        
def get_user_id(driver,xml_sub_child,xml_child,vm_name):
    query_result=execute_query( xml_sub_child.get("query_user_id"),(str(vm_name))).fetchone()
    field=driver.find_elements_by_xpath(xml_sub_child.get("xpath_user"))
    for t in field:
        if str(query_result[1]) in t.text:
            user_id=query_result[0]
            logger.debug("user_id :" + " " + str(user_id))
    return user_id



#performing add_user operation on vm
def op_user(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")               
    driver.find_element_by_xpath("//*[@title='Attach Extra Disk']").click()
    if add_user(driver,xml_sub_child,xml_child,vm_name,vm_id):
        if xml_sub_child.get("op_typ")!="cancel_user":
            field_text=message_flash(driver,xml_sub_child,xml_child)
            result=message_in_db(xml_sub_child)
            print_result(field_text,result,xml_child)
            if xml_sub_child.get("name") in vm_mode_type:
                check_user_table(driver,xml_sub_child,xml_child,vm_name,vm_id)
    return

#checking whether username is in vm_users table or not
def  check_user_table(driver,xml_sub_child,xml_child,vm_name,vm_id):
    username=xml_sub_child.get("user_id_data")
    print username
    query_length=execute_query( xml_sub_child.get("query5"),(str(vm_name))).fetchone()
    length=len(query_length)
    print length
    query_result=execute_query("select concat(user.first_name,' ',user.last_name) as user_name from user where username=%s",(str(username))).fetchone()
    path="//table[@id='vm_users']/tbody/tr"
    field=driver.find_elements_by_xpath(path)
    count=0
    a=0
    for data in field:
        if query_result[0] in data.text:
            print query_result[0]
            print data.text
            logger.debug("User name is added to VM")
            count=1
        a=a+1
    if a==length:
    	if count==0:
    		logger.errot("Error ")    
    return
    
#list of vm mode 
vm_mode_type=['vm_running_Setting_intgrtn','vm_paused_Setting_integrtn','vm_shutdown_Setting_integrtn']


#performing delete operation on vm
def op_delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id):   
    op_name=xml_sub_child.get("op")    
             
    driver.find_element_by_xpath(xml_sub_child.get("title")).click()
    click_on_dialogbox(driver)
    click_on_dialogbox(driver)
    field_text=message_flash(driver,xml_sub_child,xml_child)
    path=xml_sub_child.get("xpath_user")
    if isElementPresent(driver,xml_child,path):
        result=message_in_db(xml_sub_child)
        print_result(field_text,result,xml_child)
        if xml_sub_child.get("name") in vm_mode_type:
            operation_name=op_list[op_name]
            check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name)            

    return

#performing snapshot operation on vm
def op_snap_vm(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op") 
    if op_name=="snapshot": 
        path=xml_sub_child.get("xpath_conf")
    else:
        path=xml_sub_child.get("xpath_snap")
    print path
    if isElementPresent(driver,xml_child,path):  
        if op_name=="snapshot":
            driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) + "']").click()
        else:
            snapshot_id=get_snapshot_id(driver,xml_sub_child,xml_child,vm_name) 
            driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"/"+ str(snapshot_id) + "']").click()
        result=snap_result(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name)
        if  (result=="Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot.") | (result=="Snapshot request already in queue.") | (result==""):
            logger.debug(result )
        else:
            if xml_sub_child.get("name")in vm_mode_type:
                operation_name=op_list[op_name]
                check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name)        
    return
    

#performing  delete add_user operation on vm
def op_del_user_vm(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op") 
    path=xml_sub_child.get("xpath_user")
    if isElementPresent(driver,xml_child,path):  
        user_id=get_user_id(driver,xml_sub_child,xml_child,vm_name) 
        driver.find_element_by_xpath("//*[@href='/admin/"+ str(op_name) +"/"+ str(vm_id) +"/"+ str(user_id) + "']").click()
        result="User access is eradicated."
        field_text=message_flash(driver,xml_sub_child,xml_child)
        print_result(field_text,result,xml_child)
        if xml_sub_child.get("name") in vm_mode_type:
            check_delete_user(driver,user_id,op_name,xml_child,xml_sub_child)
    return
            

#checking whether user access removed for a vm or not                        
def  check_delete_user(driver,user_id,op_name,xml_child,xml_sub_child):
    operation_name=op_list[op_name]
    user_name=execute_query("select concat(first_name,' ',last_name) as user_name from user where id=%s",(str(user_id))).fetchone()
    path=xml_sub_child.get("xpath_user")
    if isTablePresent(driver,xml_child,path):
        user_table=driver.find_element_by_xpath(path)
        if user_name[0] in user_table.text:
            logger.error("User has not been deleted")
        else:
            logger.debug("User access is eradicated")
    else:
        logger.debug("User access is eradicated")
    return
#performing attach disk operation on vm
def op_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")    
    driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"']").click()
    add_extra_disk(driver,xml_sub_child,xml_child,vm_name,vm_id)
    field_text=message_flash(driver,xml_sub_child,xml_child)
    result=xml_sub_child.get("print")
    print_result(field_text,result,xml_child)
    if xml_sub_child.get("name")in vm_mode_type:
        operation_name=op_list[op_name]
        check_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id,operation_name)

#performing migrate operation on vm
def op_migrate_vm(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")
    driver.find_element_by_xpath("//*[@href='/admin/"+ str(op_name) +"/"+ str(vm_id) +"']").click()
    query_snap=execute_query(xml_sub_child.get("query_snapshot"),str(vm_id)).fetchall()
    length_snap=len(query_snap)
    print length_snap
    if length_snap!=0:
        result="Cannot migrate a vm with snapshot(s)"
        field_text=message_flash(driver,xml_sub_child,xml_child)
        print_result(field_text,result,xml_child)
    else:
        driver.find_element_by_xpath("//input[@value='Migrate']").click()
        query_status=execute_query("select status from vm_data where id=%s",str(vm_id)).fetchone()
        print query_status
        if query_status[0]=="2":
            result="Your VM is already running. Kindly turn it off and then retry!!!"
            field_text=message_flash(driver,xml_sub_child,xml_child)
            print_result(field_text,result,xml_child)
        else:
            result="Your task has been queued. please check your task list for status. "
            field_text=message_flash(driver,xml_sub_child,xml_child)
            print_result(field_text,result,xml_child)
            if xml_sub_child.get("name")in vm_mode_type:
                operation_name=op_list[op_name]
                check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name)
        
#performing   operation on vm        
def operation_on_vm(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")
    
    driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"']").click()
    field_text=message_flash(driver,xml_sub_child,xml_child)
    result=message_in_db(xml_sub_child)
    print_result(field_text,result,xml_child)
    if xml_sub_child.get("name") in vm_mode_type:
        operation_name=op_list[op_name]
        check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name)

#performing  edit vm config operation on vm
def op_edit_vm_conf(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")
    driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"']").click()
    driver.find_element_by_xpath("//input[@type='submit']").click()
    result="Your request has been queued!!!"
    field_text=message_flash(driver,xml_sub_child,xml_child)
    print_result(field_text,result,xml_child)
 
#selecting operation to be perform    
def click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id):   
    op_name=xml_sub_child.get("op")               
    if op_name=="user_details":
        op_user(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name=="Delete":
        op_delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name in {"revert_to_snapshot","delete_snapshot","snapshot"}:         
        op_snap_vm(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name=="delete_user_vm": 
        op_del_user_vm(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name in {"attach_extra_disk","clone_vm"}:
        op_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name=="edit_vm_config":
        op_edit_vm_conf(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name=="migrate_vm":
        op_migrate_vm(driver,xml_sub_child,xml_child,vm_name,vm_id)
        
    else:
        operation_on_vm(driver,xml_sub_child,xml_child,vm_name,vm_id)
    return 
    
# list of operation to be performed     
op_list={'revert_to_snapshot':0,'delete_snapshot':1,'snapshot':'Snapshot VM','pause_machine':'Suspend VM','Delete':'Delete VM','shutdown_machine':'Stop VM','destroy_machine':'Destroy VM','start_machine':'Start VM','user_details':'Add User','attach_extra_disk':"Attach Disk",'clone_vm':'Clone ','delete_user_vm':'Delete User','adjrunlevel':'Adjust Run Level','edit_vm_config':'Edit VM Config','resume_machine':'Resume VM','migrate_vm':'Migrate VM'}

#message display on screen
def message_in_db(xml_sub_child):
    op_name=xml_sub_child.get("op")
    if op_name=="shutdown_machine":
        result="Request to shutdown machine added to queue"
    if op_name=="pause_machine":
        result="Request to pause machine added to queue"
    if op_name=="start_machine":
        result="Request to start machine added to queue"
    if op_name=="destroy_machine":
        result="Request to destroy machine added to queue"
    if op_name=="resume_machine":
        result="Request to resume machine added to queue"
    if op_name=="adjrunlevel":
        result="Request to change level added to queue"
    if op_name=="Delete":
        result="Request to delete machine added to queue"
      
    if op_name=="user_details":
        result="User is added to vm" 
   
    return result
    

#retreiving message from given xpath        
def message_flash(driver,xml_sub_child,xml_child):
    path=driver.find_element_by_xpath('//flash[@id="flash_message"]')
    field_text=path.text
    return field_text

#checking snapshot
def snap_result(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name):
    query_result=execute_query( xml_sub_child.get("query4"),(str(vm_name))).fetchall()
    query_snap=execute_query(xml_sub_child.get("query_snap"),str(vm_id)).fetchall()
    length_snap=len(query_result)
    result=snap_db_result(xml_sub_child,op_name,length_snap, query_snap)
    field_text=message_flash(driver,xml_sub_child,xml_child)
    print_result(field_text,result,xml_child)
    return result

#printing result correspondence to snapshot
def snap_db_result(xml_sub_child,op_name,length_snap, query_snap):
    if op_name=="delete_snapshot":
        result="Your delete snapshot request has been queued"
    else:
        if str(length_snap)==xml_sub_child.get("max"):
            result="Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot."
        elif (query_snap!=()) |  (query_snap!="None"):
            result="Snapshot request already in queue."
        else :
            if op_name=="revert_to_snapshot":
                result="Your revert to snapshot request has been queued"
            else:
                result="Your request to snapshot VM has been queued"
    return result



def graph_test_mode(xml_child,xml_sub_child,driver,vm_name,vm_id):
    ssh.connect(xml_child.get("ip_add"), username=xml_child.get("usrnam"), password=xml_child.get("password"))   
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_finl_data")+vm_name +xml_sub_child.get("cmd"))
    initial_data=stdout.readlines()
    print initial_data
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
    click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id)
    time.sleep(900)
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_finl_data")+vm_name +xml_sub_child.get("cmd"))
    final_data=stdout.readlines()
    fin_data=str(final_data[2])
    finl_data=fin_data.split()
    print finl_data
    print_graph(finl_data,xml_child)

   
     
def vm_mode(xml_child,xml_sub_child,driver):
    query_result=execute_query( xml_sub_child.get("query3")).fetchall()
    print query_result
    count=0
    col_count=len(query_result[0])
    row_count=len(query_result)
    for length in range(0,(row_count)):
        vm_id=query_result[length][1]
        vm_name=query_result[length][0]
        status=query_result[length][col_count-1]
        if str(status)==xml_sub_child.get("status"):
            vm_mode_op(xml_child,xml_sub_child,driver,vm_name,vm_id)
            break
        if (str(status)==xml_sub_child.get("other_status1")) | (str(status)==xml_sub_child.get("other_status2")):
            if (row_count-1)==count: 
                logger.debug(xml_sub_child.get("print_mode"))
                break
            count+=1
            continue
       
    return
    
    
def vm_mode_op(xml_child,xml_sub_child,driver,vm_name,vm_id):
    if xml_sub_child.get("task")=="graph":
        graph_test_mode(xml_child,xml_sub_child,driver,vm_name,vm_id)
        click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
    else:
        click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
        if xml_sub_child.get("name") in {"vm_running_Setting_intgrtn","vm_running_Setting"}:
            check_snapshot(vm_name,driver,xml_child,xml_sub_child)
            check_user(driver,xml_child,xml_sub_child,vm_name)
            check_vm_configuration(driver,xml_child,xml_sub_child,vm_name) 
        click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id)
    return

# Checking data on front end and in back end                                            
                                               
def result_setting_page(field,query_result,driver,xml_child,xml_sub_child):
    i=0
    for t in field:
        print "screen=" + str(t.text)
        print "db=" + str(query_result[i][0])
        if str(query_result[i][0]) in t.text:
            logger.debug("correct inputs")
        else :
            logger.debug("Incorrect inputs")
        i+=1 
    return

#Checking data in Snapshot table  
                                                
def check_snapshot(vm_name,driver,xml_child,xml_sub_child):
    logger.debug("Checking for entries in current snapshot table")
    path=xml_sub_child.get("xpath_snap")
    if isElementPresent(driver,xml_child,path):
        query_result=execute_query(xml_sub_child.get("query4"),(str(vm_name))).fetchall()
        total_snap=len(query_result)
        field=driver.find_elements_by_xpath(path)
        result_setting_page(field,query_result,driver,xml_child,xml_sub_child)
        return total_snap
    else :
        total_snap=""
        return total_snap
        
 
#Checking data in User table         
       
def check_user(driver,xml_child,xml_sub_child,vm_name):
    logger.debug("Checking for entries in user table")
    path=xml_sub_child.get("xpath_user")
    print path
    if isElementPresent(driver,xml_child,path):
        query_result=execute_query( xml_sub_child.get("query5"),(str(vm_name))).fetchall()
        print query_result
        field=driver.find_elements_by_xpath(path)
        logger.debug("Checking for entries in Additional user table")
        result_setting_page(field,query_result,driver,xml_child,xml_sub_child)

      
#Checking data in Configuration table  
  
def check_vm_configuration(driver,xml_child,xml_sub_child,vm_name):
    logger.debug("Checking for entries in  configuration table")
    path=xml_sub_child.get("xpath_conf")
    if isElementPresent(driver,xml_child,path):
        query_result=execute_query( xml_sub_child.get("query6"),(str(vm_name))).fetchall()
        field=driver.find_elements_by_xpath(path)
        i=0
        for data in field:
            logger.debug("screen=" + str(data.text))
            logger.debug("db=" + str(query_result[0][i]))
            if str(query_result[0][i]) in data.text:
                logger.debug("correct inputs")
            else :
                logger.debug("Incorrect inputs")
            i+=1
    return

#Checking data in task table

def check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name):
    current_time=datetime.datetime.now()
    break_pt_time=current_time + datetime.timedelta(seconds=220) 
    print datetime.datetime.now()
    print break_pt_time 
    time.sleep(120)
    count=1
    while(count):
        if(datetime.datetime.now()<=break_pt_time):
            datas=check_vm_in_pending_task(driver,xml_sub_child,xml_child,vm_name,operation_name)
            print datas
            if datas!="":
                vm_in_pending=datas[0]
                task_start_time=datas[2:]
                if vm_in_pending!="1":
                    vm_in_complted=check_vm_in_completed_task(driver,xml_sub_child,vm_name,operation_name,task_start_time)
                    if vm_in_complted==1:
                        logger.debug("VM is in Completed Task Table!!!")
                        count=0
                        return 1
                    else:
                        vm_in_failed=check_vm_in_failed_task(driver,xml_sub_child,vm_name,operation_name,task_start_time)
                        if vm_in_failed==1:
                            logger.debug("VM is in Failed Task Table!!!")
                            count=0
                            return 0
                        else:
                            logger.debug("VM does not exist in any table,please check it!!!")
        else:
            count=0
    if (vm_in_pending=="1"):
        logger.error("VM is in Pending Task Table!!!")    
        return 0

       
#retrieving task_start_time
       
def get_task_start_time(driver,xml_sub_child,xml_child,vm_name,operation_name):
    vm_nam=str(vm_name)
    vm_oprtn=str(operation_name)
    qury_result=execute_query(xml_sub_child.get("task_query"),(vm_nam,vm_oprtn)).fetchone()                
    baadal_db.commit()
    if qury_result!=():
        query_result=execute_query(xml_sub_child.get("task_query"),(vm_nam,vm_oprtn)).fetchone()
        if (query_result!="None") | (query_result!=()):
            task_start_time=query_result[1]  
            print task_start_time
        else:
            logger.debug("Error")
        baadal_db.commit()
    return task_start_time
       
#Checking data in Pending task table    
    
def check_vm_in_pending_task(driver,xml_sub_child,xml_child,vm_name,operation_name):
    datas=""
    if xml_sub_child.get("id")=="clone_vm":
        driver.find_element_by_partial_link_text("My Tasks").click()
    else:
        driver.find_element_by_partial_link_text("Tasks").click()
    path="//table[@id='pendingtasks']/tbody/tr"
    vm_in_pending=0
    task_start_time=get_task_start_time(driver,xml_sub_child,xml_child,vm_name,operation_name)
    if isTablePresent(driver,xml_child,path):
        field=driver.find_elements_by_xpath(path)
        for x in field:          
            if (vm_name in x.text) & (operation_name in x.text)  & (str(task_start_time) in x.text): 
                print vm_name
                print task_start_time           
                vm_in_pending=1
                print vm_in_pending
    datas=str(vm_in_pending)+ " " +str(task_start_time) 
    return datas



#Checking data in Completed task table                      
def check_vm_in_completed_task(driver,xml_sub_child,vm_name,operation_name,task_start_time):
    driver.find_element_by_partial_link_text("Completed Tasks").click()
    field=driver.find_elements_by_xpath("//table[@id='completedtasks']/tbody/tr")
    vm_in_complted=0
    vm_nam=str(vm_name)
    for x in field:
        if (vm_name in x.text) & (operation_name in x.text)  & (str(task_start_time) in x.text):
                     
            logger.debug("Your request is Completed!!!!")
            vm_in_complted=1
    return vm_in_complted
                

#Checking data in Failed task table  		
def check_vm_in_failed_task(driver,xml_sub_child,vm_name,operation_name,task_start_time):
    driver.find_element_by_partial_link_text("Failed Tasks").click()
    field=driver.find_elements_by_xpath("//table[@id='failedtasks']/tbody/tr")
    vm_in_failed=0
    for x in field:
        if (vm_name in x.text) & (operation_name in x.text)  & (str(task_start_time) in x.text):
            logger.error("Your request is Failed!!!!")
            vm_in_failed=1       
    return vm_in_failed



#checking data in attach_disk table

def check_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id,operation_name):  
    driver.find_element_by_partial_link_text("Pending Requests").click()
    
    driver.find_element_by_partial_link_text("Attach Disk").click()
    field=driver.find_elements_by_xpath("//table[@id='sortTable2']/tbody/tr")
    qery_result=execute_query('select id,vm_name from request_queue where status=4 and vm_name=%s order by start_time desc',(str(vm_name))).fetchone()
    baadal_db.commit()
    if qery_result!=():
        query_result=execute_query('select id,vm_name from request_queue where status=4 and vm_name=%s order by start_time desc',(str(vm_name))).fetchone() 
        vm_ids= query_result[0]
        if xml_sub_child.get("action")=="approve_request":    
            driver.find_element_by_xpath("//*[@href='/admin/approve_request/"+ str(vm_ids) +"']").click()        
    else:
        
        driver.find_element_by_xpath("//*a[@href='/admin/reject_request/"+ str(vm_ids) +"']").click()
       
    return
    
# providing connection to all host exists
def conn_host(host_name,vm_status,vm_name,message,total_vm):
    import libvirt
    import commands
    query_result=execute_query("select host_name,host_ip from host").fetchall()
    no_of_cols=len(query_result)#calculate number of columns of query
    for host in range(0,no_of_cols):
        host_nam=query_result[host][0]
        host_ip=query_result[host][1]
        
        conn = libvirt.open("qemu+ssh://root@" +str(host_ip)+ "/system")
        for id in conn.listDomainsID():
            dom = conn.lookupByID(id)
            infos = dom.info()
            status=infos[0]
            status_vm=check_vm_status_on_host(status)
            print_sanity_result(status_vm,host_name,vm_status,vm_name,message,total_vm,host_ip,host_nam)
        for vm in conn.listDefinedDomains():
            status_vm="Off"
            print_sanity_result(status_vm,host_name,vm_status,vm_name,message,total_vm,host_ip,host_nam)	   



#checking data in sanity table
def print_sanity_result(status_vm,host_name,vm_status,vm_name,message,total_vm,host_ip,host_nam):
    for i in range(0,total_vm):
        vm_nm=vm_name[i]
        if ((vm_nm==vm_name[i]) & (host_nam==host_name[i])):
            messg=check_messg_in_db(vm_nm,host_ip,host_nam)
            if vm_nm==vm_name[i]:
                logger.debug('host='+vm_nm)
                logger.debug('screen='+vm_name[i])
                logger.debug('Result:correct input')
            else:
                logger.debug('host='+vm_nm)
                logger.debug('screen='+vm_name[i])
                logger.debug('Result:Incorrect input')
                
            if status_vm==vm_status[i]:
                logger.debug('host='+status_vm)
                logger.debug('screen='+vm_status[i])
                logger.debug('Result:correct input')
            else:
                logger.debug('host='+status_vm)
                logger.debug('screen='+vm_status[i])
                logger.debug('Result:Incorrect input')
                	
            if messg==message[i]:
                logger.debug('host='+messg)
                logger.debug('screen='+message[i])
                logger.debug('Result:correct input')
            else:
                logger.debug('host='+messg)
                logger.debug('screen='+message[i])
                logger.debug('Result:Incorrect input')
                
            if host_nam==host_name[i]:
                logger.debug('host='+host_nam)
                logger.debug('screen='+host_name[i])
                logger.debug('Result:correct input')
            else:
                logger.debug('host='+host_nam)
                logger.debug('screen='+host_name[i])
                logger.debug('Result:Incorrect input')



#converting vm status bits on host into status text		
def check_vm_status_on_host(status):
	if status==1:
		status_vm="Running"
	if status==3:
		status_vm="Paused"
	return status_vm

	
#checking whether data in sanity table is correct or incorrect    
def check_messg_in_db(vm_nm,host_ip,host_nam):    
    fetch_result=execute_query(" select vm_name,vm_data.status from vm_data,host where vm_data.host_id=host.id and host_ip=%s",(str(host_ip))).fetchall()
    
    no_vm_in_db=len(fetch_result)
    if fetch_result!=():
        for j in range(0,no_vm_in_db):
            if vm_nm==fetch_result[j][0]:
                vm_in_db="True"
                messg="VM is on expected host "+host_nam
            else:
                vm_in_db="False"
                messg="Orphan, VM is not in database"
       
    else:
        messg="Orphan, VM is not in database"                
    return messg
##############################################################################################################
#  					           functions for various types of input fields  				          	     #
##############################################################################################################
		
def isInput(driver, xml_sub_child):
    current_time=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    field = driver.find_element_by_id(xml_sub_child.get("id"))
    if xml_sub_child.text!=None:
        field.send_keys(xml_sub_child.text) # sending the user name/password/vm name/purpose etc
    else:
        if not (xml_sub_child.get("id") in ["user_password","user_username"]):
            field.send_keys(str(current_time))	
    return current_time

def	isInput_add(driver, xml_sub_child):
    field = driver.find_element_by_id(xml_sub_child.get("user_id"))
    field.send_keys(xml_sub_child.get("user_id_data"))
    return

def isReadOnly(driver, xml_parent,xml_child,xml_sub_child):
    current_time=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    field = driver.find_element_by_id(xml_sub_child.get("id"))
    if field.get_attribute("value")!='':
        field.send_keys(xml_sub_child.text) # sending the user name/password/vm name/purpose etc
        if field.get_attribute("value")==xml_sub_child.text:
            logger.debug(xml_child.get("value")  +': Result:error') #logging the report
        else:
            logger.debug(xml_child.get("value")  +': Result:no error') #logging the report
    else:
        logger.debug(xml_child.get("value")  +': Result:empty') #logging the report
    return 

def isWait( driver, xml_parent, xml_child, xml_sub_child):
    if xml_sub_child.get("id")=="wait":
        time.sleep(300)
    else:
        time.sleep(3)
    return

def isSubmit( driver, xml_parent, xml_child, xml_sub_child):
    driver.find_element_by_xpath(xml_sub_child.text).click()
    time.sleep(10)    
    if xml_sub_child.get("id")=="check_data":
        xpath=xml_sub_child.get("xpath")
        status=isElementPresent(driver,xml_child,xpath)

        if status==1:
            logger.debug(str(xml_child.get("value")) +": Correct data")
        else:
            logger.debug(str(xml_child.get("value")) +": Incorrect data")
    return
	
			
def isButton_add(driver, xml_sub_child,value):
    driver.find_element_by_xpath(value).click()
    print "Clear"
    return


def isClear(driver,xml_sub_child) :
	driver.find_element_by_id(xml_sub_child.get("id")).clear()	
	return
	
def isScroll(driver, xml_sub_child):
	field=driver.find_element_by_tag_name("html")
	field.send_keys(xml_sub_child.text)
	driver.execute_script("window.scrollBy(0,200)", "")
	return
	
def isHref(driver, xml_sub_child,xml_child):
    driver.find_element_by_partial_link_text(xml_sub_child.text).click()
    if xml_sub_child.get("id")=="collaborator":
        xpath=xml_sub_child.get("xpath")
        if isElementPresent(driver,xml_child,table_path):
         
            field=driver.find_element_by_xpath(xpath)    
            result=xml_sub_child.get("result")
            field_text=field.get_attribute("innerHTML")
            print_result(field_text,result,xml_child)
        else:
            logger.error("Error in the form")
	return

def isSelect(driver, xml_sub_child):
	driver.find_element_by_xpath(xml_sub_child.text).click()
	return

def isImage(driver,xml_child,xml_sub_child,a):	
    if isElementPresent(driver,xml_child,a):
        vm_mode(xml_child,xml_sub_child,driver)
    return 
    
def isTable(driver,xml_parent,xml_child,xml_sub_child):
    status_list={0:"Error",1:"failed_tasks",2:"TRY AGAIN | IGNORE",3:"my_pending_vm",4:"admin_pending_attach_disk",5:"pending_user_install_vm",6:"pending_user_clone_vm",7:"pending_user_attach_disk",8:"pending_user_edit_conf",9:"host_and_vm",10:"Configure_host",11:"admin_pending_clone_vm",12:"admin_pending_install_vm" ,13:'Configure_security',14:'pending_fac_install_vm',15:'pending_org_install_vm',16:'pending_org_clone_vm',17:'pending_org_attach_disk',18:'pending_org_edit_conf',19:"admin_pending_edit_conf" ,20:'list_my_vm'}
    table_path=xml_sub_child.text
    if isTablePresent(driver,xml_child,table_path):
        cur=execute_query( xml_child.get("query3"))
        query_result=cur.fetchall()
        cur.close()
        length=len(query_result[0])#calculate number of columns of query
        length_row=len(query_result)#calculate number of columns of query
        row_count=0 #number of rows in the table
        col_count=0 #number of columns in the table
        field=driver.find_elements_by_xpath(xml_sub_child.text)#data from gui
        count=0
        for col in field:
            field_text=col.text
            
            if field_text!="":
                count=count+1
        print count
        total=length_row*length
        print total
        if (str(total)==str(count)):
            for col in field:
                field_text=col.text
                if (field_text!=""):
            
                    if field_text==status_list[0]:
                        text=open_error_page(driver,xml_parent,field_text,row_count)
                        result=query_result[row_count][col_count]#data form query
                        print_result(text,result,xml_child)
                    
                    elif (query_result[row_count][col_count]==4) & (xml_parent.get("name")==status_list[1]):
                        result=status_list[2]
                        print_result(field_text,result,xml_child)
                    
                    elif (col_count%int(length)==7) & (xml_parent.get("name")==status_list[20]):
                    	status=query_result[row_count][col_count]
                        result=admin_vm_status(status)
                        print result
                        print_result(field_text,result,xml_child)
                    
                    elif ((col_count%int(length)==3) & ( (xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15]) | (xml_parent.get("name")==status_list[16]) | (xml_parent.get("name")==status_list[17]))) | (col_count%int(length)==4) & ((xml_parent.get("name")==status_list[4]) | (xml_parent.get("name")==status_list[7]) | (xml_parent.get("name")==status_list[6]) | (xml_parent.get("name")==status_list[5]) | (xml_parent.get("name")==status_list[11])) | ((col_count%int(length)==5) & (
                    xml_parent.get("name")==status_list[12])) :
                        ram=query_result[row_count][col_count]
                        result=check_vm_ram(ram)
                        print_result(field_text,result,xml_child) 
                    
                    elif (col_count%int(length)==4) & ( (xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15]) )  | ((col_count%int(length)==6) & (xml_parent.get("name")==status_list[12])) | (col_count%int(length)==5) & (xml_parent.get("name")==status_list[5]) :
                        extra_disk=query_result[row_count][col_count]
                        result=check_extra_disk(extra_disk)
                        print_result(field_text,result,xml_child)   
                    
                   
                    
                    elif ((col_count%int(length)==6) & (xml_parent.get("name")==status_list[5])) | ((col_count%int(length)==7) & (xml_parent.get("name")==status_list[12]) ) | ((col_count%int(length)==5) & ((xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15]) )) :
                        security_domain=query_result[row_count][col_count]
                        print security_domain
                        result=check_security_domain(security_domain)
                        print result
                        print_result(field_text,result,xml_child)   
                    
                 
   
                    elif (((col_count%int(length)==4) |  (col_count%int(length)==5) | (col_count%int(length)==6 )) &  (xml_parent.get("name")==status_list[17]) ) |  ((col_count%int(length)==4) & (xml_parent.get("name")==status_list[16])) | ((col_count%int(length)==5) & ((xml_parent.get("name")==status_list[11]) | (xml_parent.get("name")==status_list[6]))) | ((col_count%int(length)==7) & (xml_parent.get("name")==status_list[4]))  | (((col_count%int(length)==7) |  (col_count%int(length)==5) | (col_count%int(length)==6 )) & ((xml_parent.get("name")==status_list[7]) | (xml_parent.get("name")==status_list[4]))):
                        mem=query_result[row_count][col_count]
                        result=check_mem(mem)
                        print_result(field_text,result,xml_child)  
                 
                    elif (((col_count%int(length)==8)| (col_count%int(length)==9)) & (xml_parent.get("name")==status_list[4])) | (((col_count%int(length)==7) | (col_count%int(length)==8)) & (xml_parent.get("name")==status_list[11])) | (((col_count%int(length)==8)| (col_count%int(length)==9)) & (xml_parent.get("name")==status_list[12])):
                        logger.debug("correct entries")
                    
                    elif (col_count%int(length)==4) & (xml_parent.get("name")==status_list[13]):
                        status=query_result[row_count][col_count]
                        result=check_security_visibilty(status)
                        print_result(field_text,result,xml_child)
                    
                    elif (col_count%int(length)==2) & (xml_parent.get("name")==status_list[10]):
                        status=query_result[row_count][col_count]
                        result=host_status(status)
                        print_result(field_text,result,xml_child)   
                     
                    elif (col_count%int(length)==7) & ( (xml_parent.get("name")==status_list[5]) | (xml_parent.get("name")==status_list[6])) | ((col_count%int(length)==8) & (xml_parent.get("name")==status_list[7])):
                        status=query_result[row_count][col_count]
                        result=user_vm_status(status)
                        print_result(field_text,result,xml_child)  
                        
                    elif (col_count%int(length)==2) & ( (xml_parent.get("name")==status_list[17]) | (xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15])) | ((col_count%int(length)==5) &  (xml_parent.get("name")==status_list[16])) | ((col_count%int(length)==6) &  ((xml_parent.get("name")==status_list[11])  | (xml_parent.get("name")==status_list[6]))) | ((col_count%int(length)==3) & ( (xml_parent.get("name")==status_list[4]) | (xml_parent.get("name")==status_list[7]) | (xml_parent.get("name")==status_list[5]))) | ((col_count%int(length)==4) &  (xml_parent.get("name")==status_list[12])):
                        status=query_result[row_count][col_count]
                        result=check_vcpu(status)
                        print_result(field_text,result,xml_child)  
                        
                    elif (col_count%int(length)==6) & (xml_parent.get("name")==status_list[14]):
                        owner_name_db=query_result[row_count][col_count]
                        owner_name_screen=xml_child[0].text
                        print owner_name_db
                        print owner_name_screen
                        result=faculty_vm_stataus(owner_name_db,owner_name_screen)
                        print_result(field_text,result,xml_child)     
                    
                    elif (col_count%int(length)==6) & ((xml_parent.get("name")==status_list[15]) | (xml_parent.get("name")==status_list[16]) ) | ((col_count%int(length)==7) & (xml_parent.get("name")==status_list[17])):
                    	status=query_result[row_count][col_count]
                    	result=org_task_status(status)
                    	print_result(field_text,result,xml_child)
                        
                    elif (col_count%int(length)==2) & (xml_parent.get("name")==status_list[12]):
                        vm_name=query_result[row_count][4]
                        query_results=execute_query( xml_sub_child.get("query_collbtr"),(str(vm_name))).fetchall()
                        len_query=len(query_results)
                        if query_results!="None":
                            for m in range(0,len_query):
                                result=query_results[m][0]
                                print_result(field_text,result,xml_child)
                        else:
                            logger.debug(xml_child.get("value") +': Result:correct input')		
                    else:
                        result=query_result[row_count][col_count]
                        print_result(field_text,result,xml_child)
                    col_count+=1
                    if col_count%int(length)==0:
                        row_count+=1
                        col_count=0	
        else:
            logger.error("Error:tuple out of index")
    return

def faculty_vm_stataus(owner_name_db,owner_name_screen):
	
	if owner_name_screen==str(owner_name_db):
		result="Approve  |  Reject"
	else:
		result="Remind Faculty"
	return result

def user_vm_status(status):
	if (status==1) | (status==4):
		result="Waiting for admin approval"
	if status==2:
		result="Approved. In Queue."
	if status==3:
		result=" Waiting for org admin approval"
	if status==-1:
		result='Task failed. Contact administrator.'
	return result
#converting port status bits into status text
def check_port_enabled(vm_name):
    query_result=execute_query("select enable_ssh,enable_http from request_queue where vm_name=%s",(str(vm_name))).fetchall()
    enable_ssh=query_result[0][0]
    enable_http=query_result[0][1]
    if (enable_ssh=="F") & (enable_http=="F"):
        result="-"
    if (enable_ssh=="T") & (enable_http=="F"):
        result="SSH"
    if (enable_ssh=="F") & (enable_http=="T"):
        result="HTTP"
    if (enable_ssh=="T") & (enable_http=="T"):
        result="SSH,HTTP"
    return result


#converting security domain status bits into status text                                
def check_security_domain(security_domain):
    if security_domain==1:
        result="Research"
    if security_domain==2:
        result="IITD_SD"
    return result

#converting security visibility status bits into status text
def check_security_visibilty(status):
    if status=="T":
        result="ALL"
    else:
        result="NO"
    return result


#converting vCPU status bits into status text
def check_vcpu(status):
	status=str(status) + " CPU"
	return status
#converting memory bits into  text
def check_mem(mem):
    if mem==0:
        result="None"
    else:
        result=str(mem)+"GB"
    return result
    

#converting extra disk bits into  text
def check_extra_disk(extra_disk):
    if extra_disk==0:
        result="40GB"
    else:
        result="40GB + " + str(extra_disk) + "GB" 
    return result

#converting ram bits into  text
def check_vm_ram(ram):
    if ram==1024:
        result="1GB"
    if ram==2048:
        result="2GB"
    if ram==4096:
        result="4GB"
    if ram==8192:
        result="8GB"
    return result



#checking data into host table
def isCheckTable(driver, xml_parent, xml_child, xml_sub_child):
    field=driver.find_elements_by_xpath(xml_sub_child.get("path"))
    query_result=execute_query(xml_parent.get("query3")).fetchall()
    print query_result
    table=0
    for header in field:
        host_ip=query_result[table][0]
        if query_result[table][0] in header.text:
            table_path=xml_sub_child.text
            if isTablePresent(driver,xml_child,table_path):
                result_fetch=execute_query(xml_parent.get("query4"),str(host_ip)).fetchall()
                if result_fetch!=():
                    field=driver.find_elements_by_xpath(xml_sub_child.text)
                    no_of_cols=len(result_fetch[0])#calculate number of columns of query
                    #print field.text
                    row_count=0
                    col_count=0
                    for col in field:
                        field_text=col.text
                        if field_text!="":
                            if col_count%int(no_of_cols)==5:
                                status=result_fetch[row_count][col_count]
                           
                                result=admin_vm_status(status)
                            else:
                                result=result_fetch[row_count][col_count]
                            print_result(field_text,result,xml_child)
                            col_count+=1
                            if col_count%int(no_of_cols)==0:
                                row_count+=1
                                col_count=0	
                else:
                    logger.debug("No VM Exists on "+str(host_ip))
        table=table+1
    return


#approving or rejecting vm operations   
def isCheckdata(driver,xml_parent, xml_child, xml_sub_child,vm_name):
    print vm_name
    table_path=xml_sub_child.text
    if isTablePresent(driver,xml_child,table_path):
        field=driver.find_elements_by_xpath(xml_sub_child.text)#data from gui
        if  xml_sub_child.get("data")=="integeration":
            query_result=execute_query( xml_sub_child.get("query3"),str(vm_name)).fetchone()
            baadal_db.commit()
            query_result=execute_query( xml_sub_child.get("query3"),str(vm_name)).fetchone()
            print query_result
            result=query_result[0]
        else:
            query_result=execute_query( xml_sub_child.get("query3")).fetchone()
            print query_result
            result=query_result[1]
        for a in field:
            row=a.text
            op_id=xml_sub_child.get("id")
            if vm_name!="":
            
                if ("Approve  |  Reject" in row) | (op_id=="admin"):
                    check_operation(driver,xml_parent, xml_child, xml_sub_child,op_id,result)
                    break
               
            else:
                if ("Approve  |  Reject" in row & str(vm_name) in row) | (op_id=="admin") :
                
                    check_operation(driver,xml_parent, xml_child, xml_sub_child,op_id,result)
                    break
    return


def check_operation(driver,xml_parent, xml_child, xml_sub_child,op_id,result):
    request=xml_sub_child.get("click")
    driver.find_element_by_xpath("//*[@href='/"+ str(op_id) +"/"+str(request)+"/"+str(result) +"']").click()
    result=xml_sub_child.get("print_data")
    field_text=message_flash(driver,xml_sub_child,xml_child)
    print_result(field_text,result,xml_child)
    return


def isSanityCheck(driver, xml_parent, xml_child, xml_sub_child):
  
    field=driver.find_elements_by_xpath("//div[@id='sanity_check_table']/table/tbody/tr/td")
#print field.text
    row_count=0
    col_count=0
    host_name=[]
    vm_status=[]
    vm_name=[]
    message=[]
    operation=[]
    for col in field:
        field_text=col.text
        if col_count%5==0:
            host_name.insert(row_count,field_text)
           
        if col_count%5==1:
            vm_status.insert(row_count,field_text)
           
        if col_count%5==2:
            vm_name.insert(row_count,field_text)
           
        if col_count%5==3:
            message.insert(row_count,field_text)
           
        if col_count%5==4:
            operation.insert(row_count,field_text)
           
        if col_count%5==0:
            
            row_count+=1
            col_count=0	
        col_count+=1
       
    total_vm=len(vm_name)  
    
    conn_host(host_name,vm_status,vm_name,message,total_vm)
