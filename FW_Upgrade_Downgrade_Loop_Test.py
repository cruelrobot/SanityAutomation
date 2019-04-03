import serial, re, time, paramiko, subprocess, telnetlib, getpass, sys
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
# from pysnmp import debug
# debug.setLogger(debug.Debug('mibbuild'))


def Snmp(action, CmIp, Community, oid, value):
    cmdGen = cmdgen.CommandGenerator ()

    if action == "get":
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd (
            cmdgen.CommunityData (Community),
            cmdgen.UdpTransportTarget ((CmIp, 161)),
            oid
        )
        for name, val in varBinds:
            return val.prettyPrint ()


    elif action == "set":
        cmdGen.setCmd (
            cmdgen.CommunityData (Community),
            cmdgen.UdpTransportTarget ((CmIp, 161)),
            (oid, value)
        )


if __name__ == "__main__":
    sysDescr = "1.3.6.1.2.1.1.1"
    ifPhysAddress = "1.3.6.1.2.1.2.2.1.6.2"
    Cmstatus = "1.3.6.1.4.1.4491.2.1.20.1.1.1.1.2"
    docsDevSwServer = "1.3.6.1.2.1.69.1.3.1.0"
    docsDevSwFilename = "1.3.6.1.2.1.69.1.3.2.0"
    docsDevSwAdminStatus = "1.3.6.1.2.1.69.1.3.3.0"
    docsDevSwOperStatus = "1.3.6.1.2.1.69.1.3.4.0"
    docsDevSwCurrentVers = "1.3.6.1.2.1.69.1.3.5.0"
    docsDevSerialNumber = "1.3.6.1.2.1.69.1.1.4.0"
    #ubeeRg = '1.3.6.1.4.1.4684.53'
    #wifiMgmt = '1.3.6.1.4.1.4684.38.2.2.2.1.18'

    TftpIP = "172.21.1.250"
    cmIP = input('Input your device IP: ')
    FWfilesname1 = "UBC1319AA00.alter.1.9.60.1006.15.alt_v1.0.0r18.d30.cdf"
    FWfilesname2 = "UBC1319AA00.ALTICE-D30.1910.1.9.60.1006.15.alt_v1.0.0r18.d30.cdf"
    runtime = input('Input total run time of this test: (in minutes) ')
    timeout = time.time() + 60 * int(runtime)

    file = open('UG_DG_loop_test.txt', 'w')

    while True:
        oldver = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.5.0", "")
        Snmp("set", cmIP, "private", "1.3.6.1.2.1.69.1.3.1.0", rfc1902.IpAddress(TftpIP))
        Snmp("set", cmIP, "private", "1.3.6.1.2.1.69.1.3.2.0", rfc1902.OctetString(FWfilesname1))
        Snmp("set", cmIP, "private", "1.3.6.1.2.1.69.1.3.3.0", rfc1902.Integer(1))

        Operationstatus = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.4.0", "")
        while Operationstatus != "3":
            Operationstatus = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.4.0", "")
            if Operationstatus == "4":
                file.write("Upgrade fail! Congestion occur!\n")
                break
            time.sleep(10)
        if Operationstatus == "4":
            continue

        latestver = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.5.0", "")
        SerialNum = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.1.4.0", "")
        Mac = Snmp("get", cmIP, "public", "1.3.6.1.2.1.2.2.1.6.2", "")
        if latestver == oldver:
            print("Fail! Old version: " + oldver + "   Upgrade version: " + latestver + "\n")
            file.write("Fail! Old version: " + oldver + "   Upgrade version: " + latestver + "\n")
            file.write("Serial Number:" + SerialNum + "\n")
            file.write("MAC address: " + Mac + "\n")

            time.sleep(20)
        else:
            print("Success! Old version: " + oldver + "   Upgrade version: " + latestver + "\n")
            file.write("Success! Old version: " + oldver + "   Upgrade version: " + latestver + "\n")
            file.write("Serial Number:" + SerialNum + "\n")
            file.write("MAC address: " + Mac + "\n")

            time.sleep(20)
        file.write('\n==============================================================================================\n')

        tmpFilename = FWfilesname1
        FWfilesname1 = FWfilesname2
        FWfilesname2 = tmpFilename

        if time.time() > timeout:
            break

    file.close()
    end = input("Test end!")

'''
    Ver1 = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.5.0", "")
    if Ver1 != FieldVers:
        print('Current Version is :' + Ver1 + '\n' + "=== downgrade ===")
    Cmstatus = Snmp("get", cmIP, "public", "1.3.6.1.4.1.4491.2.1.20.1.1.1.2", "")
    print(Cmstatus)
    if Cmstatus != "12":
        time.sleep(30)
        Cmstatus = Snmp("get", cmIP, "public", "1.3.6.1.4.1.4491.2.1.20.1.1.1.2", "")
    elif Cmstatus == "12":
        Snmp("set", cmIP, "private", "1.3.6.1.2.1.69.1.3.3.0", rfc1902.Integer(2))
        Snmp("set", cmIP, "private", "1.3.6.1.2.1.69.1.1.3.0", rfc1902.Integer(1))
        time.sleep(120)
        output = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.4.0", "")    #OperStatus inProgress(1)
        print(output)
        i = 0
        while output == "1":
            time.sleep(140)
            Cmstatus = Snmp("get", cmIP, "public", "1.3.6.1.4.1.4491.2.1.20.1.1.1.2", "")
            if Cmstatus != "12":
                time.sleep(140)
                Cmstatus = Snmp("get", cmIP, "public", "1.3.6.1.4.1.4491.2.1.20.1.1.1.2", "")
                i += 1

                if i > 2:
                    ser.write(b"/reset \n")
                    time.sleep(120)
                    i = 0

            while output != "1":
                output = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.3.0", "")  # docsDevSwAdminStatus = ignoreProvisioningUpgrade(3)
                if output == "3":
                    ser.write(b"/reset \n")

            output = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.4.0", "")   #docsDevSwOperStatus

        Cmstatus = Snmp("get", cmIP, "public", "1.3.6.1.4.1.4491.2.1.20.1.1.1.1.2", "")
        while Cmstatus != "12":
            time.sleep(30)
            Cmstatus = Snmp("get", cmIP, "public", "1.3.6.1.4.1.4491.2.1.20.1.1.1.1.2", "")
            if Cmstatus != "12":
                output = Snmp("get", cmIP, "public", "1.3.6.1.2.1.10.127.1.2.2.1.1.2", "")
        sysDescr = Snmp("get", cmIP, "public", "1.3.6.1.2.1.1.1.0", rfc1902.Integer(1))

        docsDevSwAdminStatus = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.3.0", "")
        print(docsDevSwAdminStatus)
        Ver2 = Snmp("get", cmIP, "public", "1.3.6.1.2.1.69.1.3.5.0", "")
        if docsDevSwAdminStatus == "3" and Ver2 in FieldVers:
            print("original version: " + Ver1 + '\n' + "current version: " + Ver2 + '\n' + "Downgrade is PASS!")
        else:
            print("original version: " + Ver1 + '\n' + "current version: " + Ver2 + '\n' + "Downgrade is FAIL!")
'''
