import os
import sys
import traceback

import sh
import time
from bs4 import BeautifulSoup

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtpd import COMMASPACE
import smtplib

import logging
import logging.handlers

TO_SOMEONE = ["dongpl@spreadst.com"]
MAIL_ACCOUNT = "pl.dong@spreadtrum.com"
PASSWD = "123@afAF"
MAIL_FROM = "Get Repository <pl.dong@unisoc.com>"
SMPT_HOST = "smtp.unisoc.com"
SMPT_PORT = 587
DOCMD = "ehlo"

LOG_FILE = "./lava_submitter.log"
LOG_LEVEL = logging.INFO
logger = logging.getLogger(__name__)

MY_GIT = os.getcwd() + os.sep + 'git.sh'

def logger_init():
    logger.setLevel(level = LOG_LEVEL)
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def send_mail(sub, content, send_mail_list):
    try:
        mail_obj = smtplib.SMTP(SMPT_HOST, SMPT_PORT)
        mail_obj.docmd(DOCMD, MAIL_ACCOUNT)
        mail_obj.starttls()
        mail_obj.login(MAIL_ACCOUNT, PASSWD)
        msg = MIMEMultipart()
        msg['From'] = MAIL_FROM
        msg['To'] = COMMASPACE.join(send_mail_list)
        msg['Subject'] = sub
        con = MIMEText(content, 'html', 'utf-8')
        msg.attach(con)
        mail_obj.sendmail(MAIL_ACCOUNT, send_mail_list, msg.as_string())
        mail_obj.quit()
    except:
        traceback.print_exc()
        logger.error(traceback.format_exc())

def _get_time_stamp():
    ltime = time.localtime()
    return time.strftime("%Y%m%d%H%M%S", ltime)

def get_manifests(branch):
    manifest_dir = '{}_{}'.format(branch, _get_time_stamp())
    sh.mkdir(manifest_dir)
    sh.cd(manifest_dir)

    my_git = sh.Command(MY_GIT)
    my_git('-i', '~/.ssh/gerritkey/id_rsa', 'clone', 'gitadmin@gitmirror.spreadtrum.com:platform/manifest', '-b', branch)

    menifests_path = os.getcwd()

    return menifests_path + os.sep + 'manifest'

def get_sqrecp_repo(sprdtrusty_xml):
    soup = BeautifulSoup(sprdtrusty_xml, 'lxml')
    projects = soup.find_all('project')
    repos = map(lambda r : r.get('name'), projects)
    return repos


if __name__ == '__main__':
        logger_init()
    try:
        branch = sys.argv[1]
        # branch = 'sprdroid8.1_trunk'
        manifest_path = get_manifests(branch)
        sprdtrusty_xml = manifest_path + os.sep + 'sprdtrusty.xml'
        if os.path.exists(sprdtrusty_xml):

            with open(sprdtrusty_xml, 'r') as fd:
                sprdtrusty_repo_list = get_sqrecp_repo(fd)
                other_repo_list = ['kernel/common', 'u-boot15', 'chipram',
                                   'whale_security/ATF/arm-trusted-firmware-1.3',
                                   'whale_security/ATF/arm-trusted-firmware']
                if len(sprdtrusty_repo_list) != 0:
                    all =  sprdtrusty_repo_list + other_repo_list
                    print  all
    except:
        send_mail('Occur Exception', traceback.format_exc(), TO_SOMEONE)


