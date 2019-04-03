import subprocess
import paramiko
import wx
import time
import sys
import linecache
import serial


class ControllerFrame(wx.Frame):

    # Initialize the module and variable
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        pnl = wx.Panel(self, -1)
        icon_path = 'Assets/sunglasses_smiley.ico'
        self.SetIcon(wx.Icon(icon_path))
        wx.StaticBox(pnl, label='Iperf Server', pos=(5, 5), size=(485, 200))
        wx.StaticText(pnl, label='－Caution! Enable Iperf by this process would kill any other working Iperf Process－'
                      , pos=(20, 30))
        self.ServerIP = wx.TextCtrl(pnl, -1, pos=(90, 55), size=(150, -1))
        wx.StaticText(pnl, label='Server IP', pos=(15, 60))
        self.username = wx.TextCtrl(pnl, -1, pos=(90, 85), size=(100, -1))
        wx.StaticText(pnl, label='Username', pos=(15, 90))
        self.password = wx.TextCtrl(pnl, -1, pos=(285, 85), size=(100, -1))
        wx.StaticText(pnl, label='Password', pos=(210, 90))
        self.submit_btn = wx.Button(pnl, -1, label='Start Up', pos=(310, 170), size=(80, -1))
        self.submit_btn.Bind(wx.EVT_BUTTON, self.iperf_server, self.submit_btn)
        self.submit_btn = wx.Button(pnl, -1, label='Shutdown', pos=(400, 170), size=(80, -1))
        self.submit_btn.Bind(wx.EVT_BUTTON, self.session_close, self.submit_btn)

        wx.StaticBox(pnl, label='Iperf Client', pos=(5, 210), size=(485, 180))
        self.ClientUdp = wx.CheckBox(pnl, label='UDP Traffic', pos=(15, 235))
        # self.ClientReverse = wx.CheckBox(pnl, label='Reverse Mode', pos=(15, 260))
        self.ClientSerialPort = wx.TextCtrl(pnl, -1, pos=(350, 230), size=(100, -1))
        wx.StaticText(pnl, label='COM (EX: COM3)', pos=(225, 233))
        self.ClientPort = wx.TextCtrl(pnl, -1, pos=(100, 260), size=(100, -1))
        wx.StaticText(pnl, label='Port', pos=(15, 263))
        self.ClientLength = wx.TextCtrl(pnl, -1, pos=(350, 260), size=(100, -1))
        wx.StaticText(pnl, label='Length', pos=(225, 263))
        self.ClientTime = wx.TextCtrl(pnl, -1, pos=(100, 290), size=(100, -1))
        wx.StaticText(pnl, label='Transmit Time', pos=(15, 293))
        self.ClientParallel = wx.TextCtrl(pnl, -1, pos=(350, 290), size=(100, -1))
        wx.StaticText(pnl, label='Number of Parallel', pos=(225, 293))
        self.ClientBW = wx.TextCtrl(pnl, -1, pos=(100, 320), size=(100, -1))
        wx.StaticText(pnl, label='Bandwidth', pos=(15, 323))
        self.ClientLoop = wx.TextCtrl(pnl, -1, pos=(350, 320), size=(100, -1))
        wx.StaticText(pnl, label='Number of Loop', pos=(225, 323))
        # self.ClientIPv6 = wx.CheckBox(pnl, label='IPv6', pos=(15, 355))
        self.submit_btn = wx.Button(pnl, -1, label='Run', pos=(400, 355), size=(80, -1))
        self.submit_btn.Bind(wx.EVT_BUTTON, self.iperf_client, self.submit_btn)

        wx.StaticBox(pnl, label='System Output', pos=(505, 5), size=(485, 450))
        self.Message_Frame = wx.TextCtrl(pnl, -1, pos=(515, 25), size=(465, 420), style=wx.TE_MULTILINE|wx.TE_READONLY)

        # Make system output print on StaticText
        sys.stdout = self.Message_Frame

        self.SetSize((1010, 500))
        self.SetTitle('Static box')
        self.Centre()
        self.Show(True)

    def iperf_server(self, event):
        ip = self.ServerIP.GetValue()
        usr = self.username.GetValue()
        pwd = self.password.GetValue()
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(str(ip), port=22, username=str(usr), password=str(pwd))
        connection = session.invoke_shell()
        connection.send("killall iperf3\n")
        connection.send("iperf3 -s\n")
        print("Server on " + str(ip) + " listening")

    def iperf_client(self, event):
        ip = self.ServerIP.GetValue()
        udp = self.ClientUdp.GetValue()
        # reverse = self.ClientReverse.GetValue()
        runtime = self.ClientTime.GetValue()
        parallel = self.ClientParallel.GetValue()
        bw = self.ClientBW.GetValue()
        loop = self.ClientLoop.GetValue()
        length = self.ClientLength.GetValue()
        port = self.ClientPort.GetValue()
        serialport = self.ClientSerialPort.GetValue()
        # ipv6 = self.ClientIPv6.GetValue()
        test = 'iperf3 -c ' + str(ip)
        test_reverse = 'iperf3 -c ' + str(ip)

        ser = serial.Serial(serialport, 115200, timeout=1)
        ser.write(b"root\n")
        time.sleep(1)
        ser.write(b"ubfxcblrt\n")
        time.sleep(1)

        test_reverse = test_reverse + ' -R'

        if udp:
            test = test + ' -u'
            test_reverse = test_reverse + ' -u'
        if length != '':
            test = test + ' -l ' + str(length)
            test_reverse = test_reverse + ' -l ' + str(length)
        if port != '':
            test = test + ' -p ' + str(port)
            test_reverse = test_reverse + ' -p ' + str(port)
        if runtime != '':
            test = test + ' -t ' + str(runtime)
            test_reverse = test_reverse + ' -t ' + str(runtime)
        if bw != '':
            test = test + ' -b ' + str(bw)
            test_reverse = test_reverse + ' -b ' + str(bw)
        if parallel != '':
            test = test + ' -P ' + str(parallel)
            test_reverse = test_reverse + ' -P ' + str(parallel)

        testruntime = int(loop) * 2 * int(runtime) + int(loop) * 8
        print('Your entered command is: \n' + test + '\nand \n' + test_reverse)
        print('Please wait for about ' + str(testruntime) + ' seconds.')

        file = open('Iperf_result.txt', 'w')
        for i in range(0, int(loop)):
            if (i % 50) == 0:
                ser.write(b'/mnt/apps/etc/iperf/iperf3.startup\n')
                time.sleep(1)
                ser.write(b'\n')
                time.sleep(7)

            ser.write(test.encode('utf-8') + b'\n')
            time.sleep(int(runtime) + 1)
            ser.write(test_reverse.encode('utf-8') + b'\n')
            time.sleep(int(runtime) + 1)

            out = b''
            while ser.inWaiting() > 0:
                out += ser.read(1)
            out = out.decode('utf-8')
            out = out.strip()
            if out.find('httpd invoked oom-killer') != -1 or out.find('Exception stack') != -1 or \
                    out.find('free_cma:0') != -1 or out.find('Free swap  = 0kB') != -1:
                file.write('\n[  6]   0.00-10.03  sec   742 MBytes   fail  receiver\n')
                file.write('\n[  6]   0.00-10.03  sec   742 MBytes   fail  receiver\n')
                time.sleep(150)
                ser.write(b"root\n")
                time.sleep(1)
                ser.write(b"ubfxcblrt\n")
                time.sleep(1)

            # print(out)
            file.write(out)
            file.write('\n============================================================================================\n')
        file.close()

        myfile = open('Iperf_result.txt', 'r')
        tmplist = []
        for line in myfile:
            if udp:
                tmp = line.find('receiver')
                # tmp = line.find('[  4]   0.00-' + str(runtime) + '.0')
                if tmp != -1:
                    tmplist.append(line[38:43])
            # else:
            #    tmp = line.find('receiver')
            #    if tmp != -1:
            #        tmplist.append(line[38:42])
        myfile.close()

        resultfile = open('Iperf_loop_test.txt', 'w')
        resultfile.write('Time\tUS\t\tDS\n')
        bounder = int(loop) * 2
        print(tmplist)
        for i in range(0, bounder):
            if (i % 2) == 0:
                looptime = str((i / 2) + 1)
                resultfile.write(looptime + '\t\t')
                print(i)
                resultfile.write(tmplist[i] + '\t')
            elif (i % 2) == 1:
                print(i)
                try:
                    resultfile.write(tmplist[i] + '\n')
                except ValueError:
                    resultfile.write('0' + '\n')
                    print('Error Occurred.')

        resultfile.close()

    def session_close(self, event):
        self.Close(True)


def main():
    ex = wx.App()
    ControllerFrame(None)
    ex.MainLoop()


if __name__ == '__main__':
    main()