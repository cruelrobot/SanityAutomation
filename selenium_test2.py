from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pysnmp.entity.rfc3413.oneliner import cmdgen
import time
import json


class GetSnmp():
    # OID列表
    def make_list(self,*oid):
        oid_list = []
        for o in oid:
            oid_list.append(o)
        return oid_list

    # 擷取SNMP信息
    def info(self,oid,ip,commu):
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBindTable = cmdGen.nextCmd(
            cmdgen.CommunityData(commu),
            cmdgen.UdpTransportTarget((ip, 161)),
            oid,
        )
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBindTable[-1][int(errorIndex)-1][0] or '?'
                    )
                )
            else:
                var_dict={}
                for varBindTableRow in varBindTable:
                    for name, val in varBindTableRow:
                        var_dict[name.prettyPrint()]=str(val.prettyPrint())
                return var_dict

    # 循環OID表，提取整理信息
    def get_info(self,oid,ip,commu='public'):
        info_dict={}
        for o in oid:
            info = self.info(o,ip,commu)
            info_dict[o]=info
        info_json=json.dumps(info_dict,indent=4)
        return info_json

if __name__ == "__main__":
    wifiRadioEnable = "1.3.6.1.4.1.4684.38.2.2.2.1.18.1.1.2.1.12"
    wifiBssSsid = "1.3.6.1.4.1.4684.38.2.2.2.1.18.1.2.1.1.3"
    wifiBssSecurityMode = "1.3.6.1.4.1.4684.38.2.2.2.1.18.1.2.1.1.4"
    wifiBssWpaPreSharedKey = "1.3.6.1.4.1.4684.38.2.2.2.1.18.1.2.3.4.1.2"
    wifiBssClosedNetwork = "1.3.6.1.4.1.4684.38.2.2.2.1.18.1.2.1.1.5"
    #实例化类
    test = GetSnmp()

    UserName = input('Please enter your username of ACS web GUI: ')
    UserPass = input('Please enter your password of ACS web GUI: ')
    CMMAC = input('Please enter MAC address of DUT: (EX: 68140124A47A) ')
    # CMIP = input('Please input IP address of DUT: (EX: "10.39.1.14") ')

    # Start auto web driver with Chrome
    Browser = webdriver.Chrome()
    LoginUrl = ('https://sandbox.smartrg.com/prime-home/')

    # Login to ACS server web GUI
    Browser.get(LoginUrl)
    Browser.find_element_by_id('username').send_keys(UserName)
    Browser.find_element_by_id('password').send_keys(UserPass)
    Browser.find_element_by_id('password').send_keys(Keys.ENTER)
    time.sleep(3)

    # Search fot the CM that we registered
    Browser.find_element_by_class_name('searchQuery').send_keys(CMMAC)
    Browser.find_element_by_class_name('searchQuery').send_keys(Keys.ENTER)
    time.sleep(3)
    Browser.find_element_by_link_text('68140124A47A').click()
    time.sleep(3)

    # Expand tha container
    Browser.find_element_by_css_selector('.serviceGroupContainer:nth-child(2) > .bcol1sep > span').click()
    Browser.find_element_by_css_selector('.serviceGroupContainer:nth-child(2) .serviceListItem:nth-child(3)').click()

    # Set parameter
    Browser.find_element_by_css_selector('div.column > select').click()
    Browser.find_element_by_xpath("//option[@value='param_set']").click()
    Browser.find_element_by_css_selector('button.addScript').click()
    Browser.find_element_by_css_selector('.backgroundB:nth-child(1) > .field-value > input:nth-child(1)').send_keys('Device.WiFi.Radio.10101.Enable')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(2) > .field-value > input:nth-child(1)').send_keys('boolean')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(3) > .field-value > input:nth-child(1)').send_keys('false')
    Browser.find_element_by_css_selector('.ui-dialog-buttonset > .generated:nth-child(2)').click()
    time.sleep(3)

    Browser.find_element_by_css_selector('button.addScript').click()
    Browser.find_element_by_css_selector('.backgroundB:nth-child(1) > .field-value > input:nth-child(1)').send_keys('Device.WiFi.SSID.10001.SSID')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(2) > .field-value > input:nth-child(1)').send_keys('string')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(3) > .field-value > input:nth-child(1)').send_keys('TR069_test')
    Browser.find_element_by_css_selector('.ui-dialog-buttonset > .generated:nth-child(2)').click()
    time.sleep(3)

    Browser.find_element_by_css_selector('button.addScript').click()
    Browser.find_element_by_css_selector('.backgroundB:nth-child(1) > .field-value > input:nth-child(1)').send_keys('Device.WiFi.AccessPoint.10001.Security.ModeEnabled')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(2) > .field-value > input:nth-child(1)').send_keys('string')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(3) > .field-value > input:nth-child(1)').send_keys('None')
    Browser.find_element_by_css_selector('.ui-dialog-buttonset > .generated:nth-child(2)').click()
    time.sleep(3)

    Browser.find_element_by_css_selector('button.addScript').click()
    Browser.find_element_by_css_selector('.backgroundB:nth-child(1) > .field-value > input:nth-child(1)').send_keys('Device.WiFi.AccessPoint.10101.Security.KeyPassphrase')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(2) > .field-value > input:nth-child(1)').send_keys('unsignedint')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(3) > .field-value > input:nth-child(1)').send_keys('1234567890')
    Browser.find_element_by_css_selector('.ui-dialog-buttonset > .generated:nth-child(2)').click()
    time.sleep(3)

    Browser.find_element_by_css_selector('button.addScript').click()
    Browser.find_element_by_css_selector('.backgroundB:nth-child(1) > .field-value > input:nth-child(1)').send_keys('Device.WiFi.AccessPoint.10001.SSIDAdvertisementEnabled')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(2) > .field-value > input:nth-child(1)').send_keys('boolean')
    Browser.find_element_by_css_selector('.backgroundB:nth-child(3) > .field-value > input:nth-child(1)').send_keys('true')
    Browser.find_element_by_css_selector('.ui-dialog-buttonset > .generated:nth-child(2)').click()
    time.sleep(3)

    Browser.find_element_by_id('saveButton').click()
    time.sleep(120)
    #Browser.refresh()
    #Browser.find_element_by_id('refreshButton').click()
    #time.sleep(180)

    #生成list
    oid_list = test.make_list(
        wifiRadioEnable,
        wifiBssSsid,
        wifiBssSecurityMode,
        wifiBssWpaPreSharedKey,
        wifiBssClosedNetwork,
        )
    #info_pass = ("SNMPv2-MIB::sysDescr.0", SW_version,'')
    #print(info_pass)

    #輸出信息
    info = test.get_info(oid_list, "10.39.1.14")
    file = open('tr069_wifi_test.txt', 'w')
    file.write(info)
    file.close()

    Pass1 = 0
    Pass2 = 0
    Pass3 = 0
    Pass4 = 0
    Pass5 = 0

    myfile = open('tr069_wifi_test.txt', 'r')
    for line in myfile:
        tmp = line.find('        "SNMPv2-SMI::enterprises.4684.38.2.2.2.1.18.1.1.2.1.12.10101": "2"')
        if tmp != -1:
            Pass1 = 1
        tmp = line.find('        "SNMPv2-SMI::enterprises.4684.38.2.2.2.1.18.1.2.1.1.3.10001": "TR069_test",')
        if tmp != -1:
            Pass2 = 1
        tmp = line.find('        "SNMPv2-SMI::enterprises.4684.38.2.2.2.1.18.1.2.1.1.4.10001": "0",')
        if tmp != -1:
            Pass3 = 1
        tmp = line.find('        "SNMPv2-SMI::enterprises.4684.38.2.2.2.1.18.1.2.3.4.1.2.10101": "1234567890"')
        if tmp != -1:
            Pass4 = 1
        tmp = line.find('        "SNMPv2-SMI::enterprises.4684.38.2.2.2.1.18.1.2.1.1.5.10001": "1"')
        if tmp != -1:
            Pass5 = 1
    myfile.close()

    if Pass1 == 1 and Pass2 == 1 and Pass3 == 1 and Pass4 == 1 and Pass5 == 1:
        print('***************************************************************************')
        print('After Checking through SNMP, all parameters have being set from ACS server.')
        print('Test Pass!!!')
        print('***************************************************************************')
    else:
        print('***************************************************************************')
        print('Test failed!!!')
        print('***************************************************************************')

    Browser.save_screenshot('test.png')
    Browser.quit()