import subprocess
import paramiko
import wx
import time
import sys
import linecache


class ControllerFrame(wx.Frame):

    # Initialize the module and variable
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        pnl = wx.Panel(self, -1)
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
        test = 'iperf3 -c ' + str(ip)
        test_reverse = 'iperf3 -c ' + str(ip)

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

        testruntime = int(loop) * 2 * int(runtime)
        print('Your entered command is: \n' + test + '\nand \n' + test_reverse)
        print('Please wait for about ' + str(testruntime) + ' seconds.')
        file = open('Iperf_result.txt', 'w')
        for i in range(0, int(loop)):
            output = subprocess.Popen(test, stdout=subprocess.PIPE)
            for line in output.stdout:
                # print(line.decode('ascii'))
                file.write(line.decode('ascii'))
            time.sleep(1)
            output = subprocess.Popen(test_reverse, stdout=subprocess.PIPE)
            for line in output.stdout:
                # print(line.decode('ascii'))
                file.write(line.decode('ascii'))
            time.sleep(1)
            file.write('============================================================================================\n')
        file.close()

        myfile = open('Iperf_result.txt', 'r')
        tmplist = []
        for line in myfile:
            if udp:
                tmp = line.find('[  4]   0.00-' + str(runtime) + '.00   sec')
                if tmp != -1:
                    tmplist.append(line[38:42])
            else:
                tmp = line.find('receiver')
                if tmp != -1:
                    tmplist.append(line[38:42])
        myfile.close()

        resultfile = open('Iperf_loop_test.txt', 'w')
        resultfile.write('Time\t\tUS\t\tDS\n')
        bounder = int(loop) * 2
        print(tmplist)
        for i in range(0, bounder):
            looptime = str((i / 2) + 1)
            resultfile.write(looptime + '\t\t')
            if (i % 2) == 0:
                resultfile.write(tmplist[i] + '\t\t')
            elif (i % 2) == 1:
                resultfile.write(tmplist[i] + '\n')
        resultfile.close()

#        print(tmplist)
#        print('=================================================================================================')
#        print('Times\tUS\tDS\n')
#        print(tmplist[0])
#        print(tmplist[1])
#        for i in range(0, loop*2):
#            print((i+1) + '\t')
#            if (i % 2) == 0:
#                print(i % 2)
#                print(tmplist[i] + '\t')
#          if (i % 2) == 1:
#               print(i % 2)
#               print(tmplist[i] + '\n')

    def session_close(self, event):
        self.Close(True)


def main():
    ex = wx.App()
    ControllerFrame(None)
    ex.MainLoop()


if __name__ == '__main__':
    main()