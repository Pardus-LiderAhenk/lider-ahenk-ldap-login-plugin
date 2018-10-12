#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>

from base.plugin.abstract_plugin import AbstractPlugin
import re

class LDAPLogin(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            server_address = self.data['server-address']
            dn = self.data['dn']
            version = self.data['version']
            admin_dn = self.data['admin-dn']
            admin_password = self.data['admin-password']

            (result_code, p_out, p_err) = self.execute("/bin/bash /usr/share/ahenk/plugins/ldap-login/scripts/ldap-login.sh {0} {1} {2} {3} {4}".format(server_address, dn, admin_dn, admin_password, version))
            if result_code == 0:
                self.logger.info("Script has run successfully")
            else:
                self.logger.error("Script could not run successfully: " + p_err)

            self.change_configs()

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='LDAP Login başarı ile sağlandı',
                                         content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Dosya oluşturulamadı hata oluştu: {0}'.format(str(e)))
    def change_configs(self):

        # pattern for clearing file data from spaces, tabs and newlines
        pattern = re.compile(r'\s+')

        pam_scripts_original_directory_path = "/usr/share/ahenk/pam_scripts_original"

        ldap_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/ldap"
        ldap_original_file_path = "/usr/share/pam-configs/ldap"
        ldap_configured_file_path = "/usr/share/ahenk/plugins/ldap-login/config-files/ldap"

        pam_script_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/pam_script"
        pam_script_original_file_path = "/usr/share/pam-configs/pam_script"
        pam_script_configured_file_path = "/usr/share/ahenk/plugins/ldap-login/config-files/pam_script"

        #create pam_scripts_original directory if not exists
        if not self.is_exist(pam_scripts_original_directory_path):
            self.logger.info("Creating {0} directory.".format(pam_scripts_original_directory_path))
            self.create_directory(pam_scripts_original_directory_path)

        if self.is_exist(ldap_back_up_file_path):
            self.logger.info("Changing {0} with {1}.".format(ldap_original_file_path, ldap_configured_file_path))
            self.copy_file(ldap_configured_file_path, ldap_original_file_path)
        else:
            self.logger.info("Backing up {0}".format(ldap_original_file_path))
            self.copy_file(ldap_original_file_path, ldap_back_up_file_path)
            self.logger.info("{0} file is replaced with {1}.".format(ldap_original_file_path, ldap_configured_file_path))
            self.copy_file(ldap_configured_file_path, ldap_original_file_path)

        if self.is_exist(pam_script_back_up_file_path):
            self.copy_file(pam_script_configured_file_path, pam_script_original_file_path)
            self.logger.info("{0} is replaced with {1}.".format(pam_script_original_file_path, pam_script_configured_file_path))
        else:
            self.logger.info("Backing up {0}".format(pam_script_original_file_path))
            self.copy_file(pam_script_original_file_path, pam_script_back_up_file_path)
            self.logger.info("{0} file is replaced with {1}".format(pam_script_original_file_path, pam_script_configured_file_path))
            self.copy_file(pam_script_configured_file_path, pam_script_original_file_path)

        (result_code, p_out, p_err) = self.execute("DEBIAN_FRONTEND=noninteractive pam-auth-update --package")
        if result_code == 0:
            self.logger.info("'DEBIAN_FRONTEND=noninteractive pam-auth-update --package' has run successfully")
        else:
            self.logger.error("'DEBIAN_FRONTEND=noninteractive pam-auth-update --package' could not run successfully: " + p_err)


        # Configure nsswitch.conf
        file_ns_switch = open("/etc/nsswitch.conf", 'r')
        file_data = file_ns_switch.read()

        # cleared file data from spaces, tabs and newlines
        text = pattern.sub('', file_data)

        is_configuration_done_before = False
        if ("passwd:compatldap" not in text):
            file_data = file_data.replace("passwd:         compat", "passwd:         compat ldap")
            is_configuration_done_before = True

        if ("group:compatldap" not in text):
            file_data = file_data.replace("group:          compat", "group:          compat ldap")
            is_configuration_done_before = True

        if ("shadow:compatldap" not in text):
            file_data = file_data.replace("shadow:         compat", "shadow:         compat ldap")
            is_configuration_done_before = True

        if is_configuration_done_before:
            self.logger.info("nsswitch.conf configuration has been completed")
        else:
            self.logger.info("nsswitch.conf is already configured")

        file_ns_switch.close()
        file_ns_switch = open("/etc/nsswitch.conf", 'w')
        file_ns_switch.write(file_data)
        file_ns_switch.close()

        # Configure lightdm.service
        # check if 99-pardus-xfce.conf exists if not create
        pardus_xfce_path = "/usr/share/lightdm/lightdm.conf.d/99-pardus-xfce.conf"
        if not self.is_exist(pardus_xfce_path):
            self.logger.info("99-pardus-xfce.conf does not exist.")
            self.create_file(pardus_xfce_path)

            file_lightdm = open(pardus_xfce_path, 'a')
            file_lightdm.write("[Seat:*]\n")
            file_lightdm.write("greeter-hide-users=true")
            file_lightdm.close()
            self.logger.info("lightdm has been configured.")
        else:
            self.logger.info("99-pardus-xfce.conf exists. Delete file and create new one.")
            self.delete_file(pardus_xfce_path)
            self.create_file(pardus_xfce_path)

            file_lightdm = open(pardus_xfce_path, 'a')
            file_lightdm.write("[Seat:*]")
            file_lightdm.write("greeter-hide-users=true")
            file_lightdm.close()
            self.logger.info("lightdm.conf has been configured.")
        self.execute("systemctl restart nscd.service")
        self.logger.info("Operation finished")

def handle_task(task, context):
    plugin = LDAPLogin(task, context)
    plugin.handle_task()
    

