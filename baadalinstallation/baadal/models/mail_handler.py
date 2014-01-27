# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global auth; auth = gluon.tools.Auth()
    global mail; auth = gluon.tools.Mail()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import get_config_file

config = get_config_file()

#Email templates and subject constants
VM_REQUEST_SUBJECT = "VM request successful"

VM_REQUEST_BODY="Dear {0[userName]},\n\nYour request for VM({0[vmName]}) creation has been successfully registered. "\
                    "Please note that you will be getting a separate email on successful VM creation.\n\nRegards,\nBaadal Admin"
                    
APPROVAL_REMINDER_SUBJECT = "Request waiting for your approval"

APPROVAL_REMINDER_BODY ="Dear {0[approverName]},\n\n{0[userName]} has made a '{0[requestType]}' request on {0[requestTime]}. "\
                            "It is waiting for your approval.\n\nRegards,\nBaadal Admin"
                    
VM_CREATION_SUBJECT = "VM created successfully"

VM_CREATION_BODY="Dear {0[userName]},\n\nThe VM {0[vmName]} requested on {0[requestTime]} is "\
                    "successfully created and is now available for use. The following operations are allowed on the VM:\n"\
                    "1. Start\n2. Stop\n3. Pause\n4. Resume\n5. Destroy\n6. Delete\n\nRegards,\nBaadal Admin"

TASK_COMPLETE_SUBJECT="{0[taskType]} task successful"

TASK_COMPLETE_BODY="Dear {0[userName]},\n\nThe '{0[taskType]}' task for VM({0[vmName]}) requested on {0[requestTime]} is complete."\
                    "\n\nRegards,\nBaadal Admin "


def push_email(to_address, email_subject, email_message, reply_to_address):
    if config.getboolean("MAIL_CONF","mail_active"):
        if not reply_to_address:
            mail.send(to=to_address, subject=email_subject, message = email_message)
        else:
            mail.send(to=to_address, subject=email_subject, message = email_message, reply_to=reply_to_address)


def send_email(to_address, email_subject, email_template, context):
    
    if to_address != None:
        email_message = email_template.format(context)
        reply_to_address = config.get("MAIL_CONF","mail_noreply")
    
        push_email(to_address, email_subject, email_message, reply_to_address)


def send_email_to_approver(approver_id, requester_id, request_type, request_time):

    approver_info = get_user_details(approver_id)
    requester_name = get_full_name(requester_id)
    context = dict(approverName = approver_info[0], 
                   userName = requester_name, 
                   requestType = request_type, 
                   requestTime=request_time.strftime("%A %d %B %Y %I:%M:%S %p"))
    send_email(approver_info[1], APPROVAL_REMINDER_SUBJECT, APPROVAL_REMINDER_BODY, context)


def send_email_to_requester(vm_name):

    user_info = get_user_details(auth.user.id)
    context = dict(vmName = vm_name, 
                   userName = user_info[0])

    send_email(user_info[1], VM_REQUEST_SUBJECT, VM_REQUEST_BODY, context)
    
def send_email_to_vm_user(task_type, vm_name, request_time, vm_users):

    for vm_user in vm_users:
        user_info = get_user_details(vm_user)
        context = dict(vmName = vm_name, 
                       userName = user_info[0],
                       taskType = task_type,
                       requestTime=request_time.strftime("%A %d %B %Y %I:%M:%S %p"))
        if task_type == TASK_TYPE_CREATE_VM:
            send_email(user_info[1], VM_CREATION_SUBJECT, VM_CREATION_BODY, context)
        else:
            subject = TASK_COMPLETE_SUBJECT.format(dict(taskType=task_type))
            send_email(user_info[1], subject, TASK_COMPLETE_BODY, context)
        

def send_email_to_admin(email_subject, email_message, email_type):
    if email_type == 'request':
        email_address = config.get("MAIL_CONF","mail_admin_bug_report")
    if email_type == 'report_bug':
        email_address = config.get("MAIL_CONF","mail_admin_request")
    if email_type == 'complaint':
        email_address = config.get("MAIL_CONF","mail_admin_complaint")
    user_email_address = auth.user.email
    logger.info("MAIL ADMIN: type:"+email_type+", subject:"+email_subject+", message:"+email_message+", from:"+user_email_address)
    push_email(email_address, email_subject, email_message, user_email_address)

