#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>

from base.plugin.abstract_plugin import AbstractPlugin
import re


class Login(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            self.execute("sudo apt purge libpam-ldap libnss-ldap ldap-utils -y")
            self.execute("sudo apt autoremove -y")

            self.change_configs()

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message= 'LDAP Login başarı ile sağlandı',
                                         content_type= self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Dosya oluşturulamadı hata oluştu: {0}'.format(str(e)))

    def change_configs(self):

        # pattern for clearing file data from spaces, tabs and newlines
        pattern = re.compile(r'\s+')

        # Configure nsswitch.conf
        file_ns_switch = open("/etc/nsswitch.conf", 'r')
        file_data = file_ns_switch.read()

        # cleared file data from spaces, tabs and newlines
        text = pattern.sub('', file_data)

        did_configuration_change = False
        if "passwd:compatldap" in text:
            file_data = file_data.replace("passwd:         compat ldap", "passwd:         compat")
            did_configuration_change = True

        if "group:compatldap" in text:
            file_data = file_data.replace("group:          compat ldap", "group:          compat")
            did_configuration_change = True

        if "shadow:compatldap" in text:
            file_data = file_data.replace("shadow:         compat ldap", "shadow:         compat")
            did_configuration_change = True

        if did_configuration_change:
            self.logger.info("nsswitch.conf configuration has been configured")
        else:
            self.logger.info("nsswitch.conf has already been configured")

        file_ns_switch.close()
        file_ns_switch = open("/etc/nsswitch.conf", 'w')
        file_ns_switch.write(file_data)
        file_ns_switch.close()

        # Configure common-password

        file_common_password = open("/etc/pam.d/common-password", 'r')
        file_data = file_common_password.read()

        # cleared file data from spaces, tabs and newlines
        text = pattern.sub('', file_data)

        original_configuration = "password	[success=1 user_unknown=ignore default=die]	pam_ldap.so try_first_pass"
        new_configuration = "password	[success=1 user_unknown=ignore default=die]	pam_ldap.so use_authtok try_first_pass"

        if "password[success=1user_unknown=ignoredefault=die]pam_ldap.sotry_first_pass" in text:
            file_data = file_data.replace(original_configuration, new_configuration)
            self.logger.info("common-password configuration has been configured")
        else:
            self.logger.info("common-password has already been configured")

        file_common_password.close()
        file_common_password = open("/etc/pam.d/common-password", 'w')
        file_common_password.write(file_data)
        file_common_password.close()


        #Configure common-session

        file_common_session = open("/etc/pam.d/common-session", 'r')

        file_data = file_common_session.read()
        text = pattern.sub('', file_data)

        if "sessionrequiredpam_mkhomedir.soskel=/etc/skelumask=0022" in text:
            file_data = file_data.replace("session required        pam_mkhomedir.so skel=/etc/skel umask=0022", "")
            self.logger.info("common-session configuration has been configured")
        else:
            self.logger.info("common-session has already been configured")

        file_common_password.close()
        file_common_password = open("/etc/pam.d/common-session", 'w')
        file_common_password.write(file_data)
        file_common_password.close()

        # Configure lightdm.service
        pardus_xfce_path = "/usr/share/lightdm/lightdm.conf.d/99-pardus-xfce.conf"
        if self.is_exist(pardus_xfce_path):
            self.logger.info("99-pardus-xfce.conf exists. Delete file and create new one.")
            self.delete_file(pardus_xfce_path)

        self.execute("systemctl restart nscd.service")
        self.logger.info("Operation finished")


def handle_task(task, context):
    plugin = Login(task, context)
    plugin.handle_task()
    

