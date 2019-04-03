import sys
import time
import subprocess
import paramiko
import wx


# Layout of Controller GUI.
class ControllerFrame(wx.Frame):

    # Initialize the module and variable
    def __init__(self, *args, **kw):
        CMTS_Category = ['C10G', 'C40G-33', 'C40G-35', 'C4C', 'E6000', 'CBR8']
        IP_Provision_Mode = ['Dual Stack', 'IPv4 Only', 'IPv6 Only']
        Service_group = ['Service Group 1', 'Service Group 2', 'Service Group 3', 'No Setting']
        Channel_Width = ['US', 'EU']
        Modulation = ['No Changed', 'QPSK', '8-QAM', '16-QAM', '32-QAM', '64-QAM', '128-QAM', '512-QAM', '1024-QAM',
                      '2048-QAM', '4096-QAM']
        wx.Frame.__init__(self, *args, **kw)
        pnl = wx.Panel(self, -1)
        wx.StaticBox(pnl, label='CMTS_Controller', pos=(5, 5), size=(490, 400))
        wx.StaticBox(pnl, label='Docsis', pos=(10, 25), size=(475, 210))
        self.CMTS_Choices = wx.ComboBox(pnl, -1, pos=(130, 45), size=(100, -1), choices=CMTS_Category)
        wx.StaticText(pnl, label='CMTS Category', pos=(15, 50))
        self.Service_Group = wx.ComboBox(pnl, -1, pos=(130, 75), size=(100, -1), choices=Service_group)
        wx.StaticText(pnl, label='Service Group', pos=(15, 80))
        self.Provision_Mode = wx.ComboBox(pnl, -1, pos=(130, 105), size=(100, -1), choices=IP_Provision_Mode)
        wx.StaticText(pnl, label='IP Provision Mode', pos=(15, 110))
        self.Start_Frequency_Value = wx.TextCtrl(pnl, -1, pos=(365, 45), size=(100, -1))
        wx.StaticText(pnl, label='Start Frequency', pos=(265, 50))
        self.Channel_Witdh_Standard = wx.ComboBox(pnl, -1, pos=(365, 75), size=(100, -1), choices=Channel_Width)
        wx.StaticText(pnl, label='Region', pos=(265, 80))
        wx.StaticText(pnl, label='-------------------------------------------------------------------------------------'
                                 '------', pos=(20, 140))
        self.DS_SCQAM_Modulation_Choice = wx.ComboBox(pnl, -1, pos=(130, 165), size=(100, -1), choices=Modulation)
        wx.StaticText(pnl, label='3.0 DS Modulation', pos=(15, 170))
        self.US_SCQAM_Modulation_Choice = wx.ComboBox(pnl, -1, pos=(130, 195), size=(100, -1), choices=Modulation)
        wx.StaticText(pnl, label='3.0 US Modulation', pos=(15, 200))

        wx.StaticBox(pnl, label='System Output', pos=(505, 5), size=(485, 745))
        self.Message_Frame = wx.TextCtrl(pnl, -1, pos=(515, 25), size=(465, 715), style=wx.TE_MULTILINE|wx.TE_READONLY)

        wx.StaticBox(pnl, label='Downstream', pos=(10, 240), size=(230, 110))
        wx.StaticText(pnl, label='SC-QAM', pos=(40, 270))
        self.DS_SCQAM_input = wx.SpinCtrl(pnl, value='1', pos=(110, 265), size=(100, -1), min=0, max=32)
        wx.StaticText(pnl, label='OFDM', pos=(40, 310))
        self.DS_OFDM_input = wx.SpinCtrl(pnl, value='1', pos=(110, 305), size=(100, -1), min=0, max=2)
        wx.StaticBox(pnl, label='Upstream', pos=(255, 240), size=(230, 110))
        wx.StaticText(pnl, label='SC-QAM', pos=(285, 270))
        self.US_SCQAM_input = wx.SpinCtrl(pnl, value='1', pos=(355, 265), size=(100, -1), min=0, max=32)
        wx.StaticText(pnl, label='OFDMA', pos=(285, 310))
        self.US_OFDMA_input = wx.SpinCtrl(pnl, value='1', pos=(355, 305), size=(100, -1), min=0, max=2)

        # Create a button and button event. Binding with function SSH access.
        self.submit_btn = wx.Button(pnl, -1, label='Submit', pos=(310, 370), size=(80, -1))
        self.submit_btn.Bind(wx.EVT_BUTTON, self.SSH_Access, self.submit_btn)

        # Create a button and button event. Binding with function close.
        self.exit_btn = wx.Button(pnl, -1, label='Exit', pos=(400, 370), size=(80, -1))
        self.exit_btn.Bind(wx.EVT_BUTTON, self.OnClose, self.exit_btn)

        # Iperf server
        wx.StaticBox(pnl, label='Iperf Server', pos=(5, 410), size=(490, 150))
        wx.StaticText(pnl, label='－Caution! Enable Iperf by this process would kill any other working Iperf Process－'
                      , pos=(20, 435))
        self.ServerIP = wx.TextCtrl(pnl, -1, pos=(90, 460), size=(150, -1))
        wx.StaticText(pnl, label='Server IP', pos=(15, 465))
        self.username = wx.TextCtrl(pnl, -1, pos=(90, 490), size=(100, -1))
        wx.StaticText(pnl, label='Username', pos=(15, 495))
        self.password = wx.TextCtrl(pnl, -1, pos=(90, 520), size=(100, -1))
        wx.StaticText(pnl, label='Password', pos=(15, 525))
        self.submit_btn = wx.Button(pnl, -1, label='Start Up', pos=(310, 525), size=(80, -1))
        self.submit_btn.Bind(wx.EVT_BUTTON, self.iperf_server, self.submit_btn)
        self.submit_btn = wx.Button(pnl, -1, label='Shutdown', pos=(400, 525), size=(80, -1))
        self.submit_btn.Bind(wx.EVT_BUTTON, self.OnClose, self.submit_btn)

        wx.StaticBox(pnl, label='Iperf Client', pos=(5, 570), size=(490, 180))
        self.ClientUdp = wx.CheckBox(pnl, label='UDP Traffic', pos=(15, 595))
        self.ClientReverse = wx.CheckBox(pnl, label='Reverse Mode', pos=(15, 620))
        self.ClientTime = wx.TextCtrl(pnl, -1, pos=(100, 650), size=(100, -1))
        wx.StaticText(pnl, label='Transmit Time', pos=(15, 653))
        self.ClientParallel = wx.TextCtrl(pnl, -1, pos=(350, 650), size=(100, -1))
        wx.StaticText(pnl, label='Number of Parallel', pos=(225, 653))
        self.ClientBW = wx.TextCtrl(pnl, -1, pos=(100, 680), size=(100, -1))
        wx.StaticText(pnl, label='Bandwidth', pos=(15, 683))
        self.submit_btn = wx.Button(pnl, -1, label='Run', pos=(400, 715), size=(80, -1))
        self.submit_btn.Bind(wx.EVT_BUTTON, self.iperf_client, self.submit_btn)

        # Make system output print on StaticText
        sys.stdout = self.Message_Frame

        self.SetSize((1010, 800))
        self.SetTitle('Static box')
        self.Centre()
        self.Show(True)

    # Access CMTS via SSH
    def SSH_Access(self, event):
        self.DS_SCQAM = int(self.DS_SCQAM_input.GetValue())
        self.US_SCQAM = int(self.US_SCQAM_input.GetValue())
        self.DS_SCQAM_Modulation_used = str(self.DS_SCQAM_Modulation_Choice.GetValue())
        self.US_SCQAM_Modulation_used = str(self.US_SCQAM_Modulation_Choice.GetValue())
        self.session = paramiko.SSHClient()
        self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Enter section of Controlling C10G. ---------------------------------------------------------------------------
        if self.CMTS_Choices.GetValue() == 'C10G':
            if self.DS_OFDM_input.GetValue() != 0:
                print('Error:\nC10G is 3.0 which does not support OFDM. Please switch the value to 0.')
                return
            if self.US_OFDMA_input.GetValue() != 0:
                print('Error:\nC10G is 3.0 which does not support OFDMA. Please switch the value to 0.')
                return

            self.session.connect("172.21.36.254", port=22, username="root", password="casa")
            self.connection = self.session.invoke_shell()
            self.connection.send("enable\n")
            time.sleep(1)
            self.connection.send("casa\n")
            time.sleep(1)
            self.connection.send("config\n")
            time.sleep(1)

            # Modified IP provision mode.
            if self.Service_Group.GetValue() == 'Service Group 1':
                self.connection.send("interface docsis-mac 1\n")
                if self.Provision_Mode.GetValue() == 'Dual Stack':
                    self.connection.send("ip-provisioning-mode dual-stack\n")
                elif self.Provision_Mode.GetValue() == 'IPv4 Only':
                    self.connection.send("ip-provisioning-mode ipv4-only\n")
                elif self.Provision_Mode.GetValue() == 'IPv6 Only':
                    self.connection.send("ip-provisioning-mode ipv6-only\n")

            # Modified DS SCQAM Modulation
            if self.DS_SCQAM_Modulation_used == '64-QAM':
                for i in range(0, 8):
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("modulation 64qam\n")
            elif self.DS_SCQAM_Modulation_used == '128-QAM':
                for i in range(0, 8):
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("modulation 128qam\n")
            elif self.DS_SCQAM_Modulation_used == '256-QAM':
                for i in range(0, 8):
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("modulation 256qam\n")
            elif self.DS_SCQAM_Modulation_used == 'No Changed':
                pass
            else:
                print("DS SCQAM only support 64-QAM, 128-QAM, 256-QAM!")

            # Modified US SCQAM Modulation
            if self.US_SCQAM_Modulation_used == 'QPSK':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma qpsk off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma qpsk off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '8-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 8qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 8qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '16-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 16qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 16qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '32-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 32qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 32qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '64-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 64qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 64qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '128-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 128qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 128qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == 'No Changed':
                pass
            else:
                print("US SCQAM only support QPSK, 8-QAM, 16-QAM, 32-QAM, 64-QAM, 128-QAM!")

            # Change Frequency
            Frequency_Temp = self.Start_Frequency_Value.GetValue()
            if self.Channel_Witdh_Standard.GetValue() == "US":
                Gap = 6000000
                for i in range(0, 8):
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    for j in range(0, 4):
                        self.connection.send("channel " + str(j) + " frequency " + str(Frequency_Temp) + "\n")
                        Frequency_Temp = int(Frequency_Temp) + Gap
            elif self.Channel_Witdh_Standard.GetValue() == "EU":
                Gap = 8000000
                for i in range(0, 8):
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    for j in range(0, 4):
                        self.connection.send("channel " + str(j) + " frequency " + str(Frequency_Temp) + "\n")
                        Frequency_Temp = int(Frequency_Temp) + Gap
            elif self.Channel_Witdh_Standard.GetValue() == "":
                print("Note: No change in CMTS Frequency.")
            else:
                print("Error: Invalid input of Region!")

            # Modified DS channel based on customer's input.
            i_ds_upper = self.DS_SCQAM // 4
            j_ds_upper = self.DS_SCQAM % 4
            #        print(self.DS_SCQAM)
            #        print(i_upper, j_upper)
            for i in range(0, 8):
                for j in range(0, 4):
                    if (i < i_ds_upper) or (i == i_ds_upper and j < j_ds_upper):
                        self.connection.send("interface qam 0/" + str(i) + "\n")
                        self.connection.send("no channel " + str(j) + " shutdown\n")
                    else:
                        self.connection.send("interface qam 0/" + str(i) + "\n")
                        self.connection.send("channel " + str(j) + " shutdown\n")

            # Modified US channel based on customer's input.
            i_us_upper = self.US_SCQAM
            for i in range(0, 8):
                if i < i_us_upper:
                    self.connection.send("interface upstream 13/" + str(i) + ".0\n")
                    self.connection.send("no shutdown\n")
                else:
                    self.connection.send("interface upstream 13/" + str(i) + ".0\n")
                    self.connection.send("shutdown\n")
            print('Done!')

        # Enter section of controlling C40G-33(New). -------------------------------------------------------------------
        elif self.CMTS_Choices.GetValue() == 'C40G-33':
            self.DS_SCQAM = int(self.DS_SCQAM_input.GetValue())
            self.DS_OFDM = int(self.DS_OFDM_input.GetValue())
            self.US_SCQAM = int(self.US_SCQAM_input.GetValue())
            self.US_OFDMA = int(self.US_OFDMA_input.GetValue())

            self.session.connect("172.21.33.254", port=22, username="root", password="casa")
            self.connection = self.session.invoke_shell()
            self.connection.send("enable\n")
            time.sleep(1)
            self.connection.send("casa\n")
            time.sleep(1)
            self.connection.send("config\n")
            time.sleep(1)
            print('Not ready')

            # Modified IP provision mode.
            if self.Service_Group.GetValue() == 'Service Group 1':
                self.connection.send("interface docsis-mac 1\n")
                if self.Provision_Mode.GetValue() == 'Dual Stack':
                    self.connection.send("ip-provisioning-mode dual-stack\n")
                elif self.Provision_Mode.GetValue() == 'IPv4 Only':
                    self.connection.send("ip-provisioning-mode ipv4-only\n")
                elif self.Provision_Mode.GetValue() == 'IPv6 Only':
                    self.connection.send("ip-provisioning-mode ipv6-only\n")
            else:
                print('C40G-33 only provide one service group')
                return

            # Modified DS SCQAM Modulation
            if self.DS_SCQAM_Modulation_used == '64-QAM':
                for i in range(0, 8):
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("modulation 64qam\n")
            elif self.DS_SCQAM_Modulation_used == '128-QAM':
                for i in range(0, 8):
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("modulation 128qam\n")
            elif self.DS_SCQAM_Modulation_used == '256-QAM':
                for i in range(0, 8):
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("modulation 256qam\n")
            else:
                print("DS SCQAM only support 64-QAM, 128-QAM, 256-QAM!")

            # Modified US SCQAM Modulation
            if self.US_SCQAM_Modulation_used == 'QPSK':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma qpsk off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma qpsk off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '8-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 8qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 8qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '16-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 16qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 16qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '32-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 32qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 32qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '64-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 64qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 64qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            elif self.US_SCQAM_Modulation_used == '128-QAM':
                self.connection.send("exit\n")
                self.connection.send("modulation-profile 6\n")
                self.connection.send("a-short atdma 128qam off 104 12 75 338 6 16 shortened on 1 1536 qpsk1\n")
                self.connection.send("a-long atdma 128qam off 104 16 220 338 0 16 shortened on 1 1536 qpsk1\n")
                for i in range(0, 8):
                    self.connection.send("interface upstream 13/" + str(i) + ".0 \n")
                    self.connection.send("logical-channel 0 profile 6\n")
            else:
                print("US SCQAM only support QPSK, 8-QAM, 16-QAM, 32-QAM, 64-QAM, 128-QAM!")

            i_ds_sc_upper = self.DS_SCQAM
            for i in range(0, 32):
                if i < i_ds_sc_upper:
                    self.connection.send("interface qam 0/0\n")
                    self.connection.send("no channel " + str(i) + " shutdown\n")
                else:
                    self.connection.send("interface qam 0/0\n")
                    self.connection.send("channel " + str(i) + " shutdown\n")

            i_ds_ofdm_upper = self.DS_OFDM
            for i in range(0, 2):
                if i < i_ds_ofdm_upper:
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("no ofdm-channel 0 shutdown\n")
                else:
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("ofdm-channel 0 shutdown\n")

            i_us_sc_upper = self.US_SCQAM // 4
            j_us_sc_upper = self.US_SCQAM % 4
            for i in range(0, 2):
                for j in range(0, 4):
                    if (i < i_us_sc_upper) or (i == i_us_sc_upper and j < j_us_sc_upper):
                        self.connection.send("interface  upstream 5/" + str(i) + "." + str(j) + "\n")
                        self.connection.send("no shutdown\n")
                    else:
                        self.connection.send("interface  upstream 5/" + str(i) + "." + str(j) + "\n")
                        self.connection.send("shutdown\n")

            i_us_ofdma_upper = self.US_OFDMA
            for i in range(0, 2):
                if i < i_us_ofdma_upper:
                    self.connection.send("interface ofdma 5/" + str(i) + ".0\n")
                    self.connection.send("no shutdown\n")
                else:
                    self.connection.send("interface ofdma 5/" + str(i) + ".0\n")
                    self.connection.send("shutdown\n")
            print('Done!')

        # Enter section of controlling C40G-35(OLD). -------------------------------------------------------------------
        elif self.CMTS_Choices.GetValue() == 'C40G-35':
            self.DS_SCQAM = int(self.DS_SCQAM_input.GetValue())
            self.DS_OFDM = int(self.DS_OFDM_input.GetValue())
            self.US_SCQAM = int(self.US_SCQAM_input.GetValue())
            self.US_OFDMA = int(self.US_OFDMA_input.GetValue())

            self.session.connect("172.21.35.254", port=22, username="root", password="casa")
            self.connection = self.session.invoke_shell()
            self.connection.send("enable\n")
            time.sleep(1)
            self.connection.send("casa\n")
            time.sleep(1)
            self.connection.send("config\n")
            time.sleep(1)

            # Modified IP provision mode.
            if self.Service_Group.GetValue() == 'Service Group 1':
                self.connection.send("interface docsis-mac 1\n")
                if self.Provision_Mode.GetValue() == 'Dual Stack':
                    self.connection.send("ip-provisioning-mode dual-stack\n")
                elif self.Provision_Mode.GetValue() == 'IPv4 Only':
                    self.connection.send("ip-provisioning-mode ipv4-only\n")
                elif self.Provision_Mode.GetValue() == 'IPv6 Only':
                    self.connection.send("ip-provisioning-mode ipv6-only\n")

            i_ds_sc_upper = self.DS_SCQAM
            for i in range(0, 32):
                if i < i_ds_sc_upper:
                    self.connection.send("interface qam 0/0\n")
                    self.connection.send("no channel " + str(i) + " shutdown\n")
                else:
                    self.connection.send("interface qam 0/0\n")
                    self.connection.send("channel " + str(i) + " shutdown\n")

            i_ds_ofdm_upper = self.DS_OFDM + 1
            for i in range(1, 2):
                if i < i_ds_ofdm_upper:
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("no ofdm-channel 0 shutdown\n")
                else:
                    self.connection.send("interface qam 0/" + str(i) + "\n")
                    self.connection.send("ofdm-channel 0 shutdown\n")

            i_us_sc_upper = (self.US_SCQAM // 4) + 1
            j_us_sc_upper = self.US_SCQAM % 4
            for i in range(1, 3):
                for j in range(0, 4):
                    if (i < i_us_sc_upper) or (i == i_us_sc_upper and j < j_us_sc_upper):
                        self.connection.send("interface  upstream 5/" + str(i) + "." + str(j) + "\n")
                        self.connection.send("no shutdown\n")
                    else:
                        self.connection.send("interface  upstream 5/" + str(i) + "." + str(j) + "\n")
                        self.connection.send("shutdown\n")

            i_us_ofdma_upper = self.US_OFDMA
            for i in range(0, 2):
                if i < i_us_ofdma_upper:
                    self.connection.send("interface ofdma 5/" + str(i) + ".0\n")
                    self.connection.send("no shutdown\n")
                else:
                    self.connection.send("interface ofdma 5/" + str(i) + ".0\n")
                    self.connection.send("shutdown\n")
            print('Done!')

        # Enter section of controlling CBR8 ----------------------------------------------------------------------------
        elif self.CMTS_Choices.GetValue() == 'CBR8':
            self.DS_SCQAM = int(self.DS_SCQAM_input.GetValue())
            self.DS_OFDM = int(self.DS_OFDM_input.GetValue())
            self.US_SCQAM = int(self.US_SCQAM_input.GetValue())
            self.US_OFDMA = int(self.US_OFDMA_input.GetValue())

            self.session.connect("172.21.39.254", port=22, username="root", password="cisco")
            self.connection = self.session.invoke_shell()
            self.connection.send("enable\n")
            time.sleep(1)
            self.connection.send("cisco\n")
            time.sleep(1)
            self.connection.send("conf t\n")
            time.sleep(1)

            # Modified IP provision mode & service group.
            if self.Service_Group.GetValue() != 'No Setting':
                print('No service group setting in CBR8 CMTS. Please ignore this.')
                return

            i_ds_sc_upper = self.DS_SCQAM - 1
            print('test')
            self.connection.send("controller integrated-Cable 1/0/0\n")
            self.connection.send("no rf-chan 0 31\n")
            self.connection.send("rf-chan 0 " + str(i_ds_sc_upper) + "\n")
            self.connection.send("type DOCSIS\n")
            self.connection.send("frequency 303000000\n")
            self.connection.send("rf-output NORMAL\n")
            self.connection.send("power-adjust 0.0\n")
            self.connection.send("qam-profile 1\n")
            self.connection.send("docsis-channel-id 1\n")

            self.connection.send('end\n')
            self.connection.send('config t\n')
            i_us_sc_upper = self.US_SCQAM
            self.connection.send('interface cable 1/0/0\n')
            self.connection.send('cable upstream bonding-group 1001\n')
            for i in range(0, 8):
                self.connection.send('no upstream ' + str(i) + '\n')
            for j in range(0, i_us_sc_upper):
                self.connection.send('upstream ' + str(j) + '\n')

            self.connection.send('end\n')
            self.connection.send('config t\n')
            i_us_ofdma_upper = self.US_OFDMA
            self.connection.send('interface cable 1/0/0\n')
            self.connection.send('cable upstream bonding-group 2001\n')
            for i in range(0, 2):
                self.connection.send('no upstream 1' + str(i + 1) + '\n')
            for j in range(0, i_us_ofdma_upper):
                self.connection.send('upstream 1' + str(j + 1) + '\n')

            self.connection.send('end\n')
            self.connection.send('config t\n')
            i_ds_ofdm_upper = self.DS_OFDM
            self.connection.send('controller integrated-Cable 1/0/1\n')
            if i_ds_ofdm_upper == 0:
                self.connection.send('no rf-chan 158\n')
                self.connection.send('no rf-chan 159\n')
            elif i_ds_ofdm_upper == 1:
                self.connection.send('no rf-chan 158\n')
                self.connection.send('no rf-chan 159\n')
                self.connection.send('rf-chan 158\n')
                self.connection.send('power-adjust 0.0\n')
                self.connection.send('docsis-channel-id 159\n')
                self.connection.send('ofdm channel-profile 21 start-frequency 580000000 width 192000000 plc 676000000\n')
            elif i_ds_ofdm_upper == 2:
                self.connection.send('no rf-chan 158\n')
                self.connection.send('rf-chan 158\n')
                self.connection.send('power-adjust 0.0\n')
                self.connection.send('docsis-channel-id 159\n')
                self.connection.send('ofdm channel-profile 21 start-frequency 580000000 width 192000000 plc 676000000\n')
                self.connection.send('exit\n')
                self.connection.send('no rf-chan 159\n')
                self.connection.send('rf-chan 159\n')
                self.connection.send('power-adjust 0.0\n')
                self.connection.send('docsis-channel-id 160\n')
                self.connection.send('ofdm channel-profile 21 start-frequency 780000000 width 192000000 plc 876000000\n')
            else:
                print('CBR8 only support 2 OFDM channel.')
            print('Done')

        # Enter section of controlling E6000. --------------------------------------------------------------------------
        elif self.CMTS_Choices.GetValue() == 'E6000':
            self.DS_SCQAM = int(self.DS_SCQAM_input.GetValue())
            self.DS_OFDM = int(self.DS_OFDM_input.GetValue())
            self.US_SCQAM = int(self.US_SCQAM_input.GetValue())
            self.US_OFDMA = int(self.US_OFDMA_input.GetValue())

            self.session.connect("172.21.38.254", port=22, username="root", password="")
            self.connection = self.session.invoke_shell()
            self.connection.send("enable\n")
            time.sleep(1)
            self.connection.send("config\n")
            time.sleep(1)
            print('-Connected-')

            if self.DS_SCQAM + self.DS_OFDM > 32 or self.DS_OFDM > 1 or self.US_OFDMA > 1:
                print('E6000 only support 32 maximum channels (sum of SC-QAM and OFDM).')
                print('E6000 only support 1 OFDM channel and only on Service Group 1.')
                print('E6000 only support 1 OFDMA channel and only on Service Group 2.')
                print('Please follow all rule mentioned above. Thanks!')
                return
            elif self.Service_Group.GetValue() == 'Service Group 1' and self.US_OFDMA > 0:
                print('Service Group 1 does not support OFDMA Frame.')
                return
            elif self.Service_Group.GetValue() == 'Service Group 2' and self.DS_OFDM > 0:
                print('Service Group 2 does not support OFDM Frame.')
                return
            elif self.Service_Group.GetValue() == 'No Setting' or self.Service_Group.GetValue() == 'Service Group 3':
                print('Only Service Group 1 & 2 supported.')
                return
            elif self.Service_Group.GetValue() == 'Service Group 1':
                if self.Provision_Mode.GetValue() == 'Dual Stack':
                    print('E6000 does not support dual stack mode.')
                    return
                elif self.Provision_Mode.GetValue() == 'IPv4 Only':
                    self.connection.send("interface cable-mac 1\n")
                    self.connection.send("cable cm-ip-prov-mode ipv4only\n")
                elif self.Provision_Mode.GetValue() == 'IPv6 Only':
                    self.connection.send("interface cable-mac 1\n")
                    self.connection.send("cable cm-ip-prov-mode ipv6only\n")
            elif self.Service_Group.GetValue() == 'Service Group 2':
                if self.Provision_Mode.GetValue() == 'Dual Stack':
                    print('E6000 does not support dual stack mode.')
                    return
                elif self.Provision_Mode.GetValue() == 'IPv4 Only':
                    self.connection.send("interface cable-mac 2\n")
                    self.connection.send("cable cm-ip-prov-mode ipv4only\n")
                elif self.Provision_Mode.GetValue() == 'IPv6 Only':
                    self.connection.send("interface cable-mac 2\n")
                    self.connection.send("cable cm-ip-prov-mode ipv6only\n")

            i_ds_sc_upper = self.DS_SCQAM
            if self.Service_Group.GetValue() == 'Service Group 1':
                for i in range(0, 31):
                    if i < i_ds_sc_upper:
                        self.connection.send("interface cable-downstream 13/0/" + str(i) + " cable no shutdown\n")
                    else:
                        self.connection.send("interface cable-downstream 13/0/" + str(i) + " cable shutdown\n")
            elif self.Service_Group.GetValue() == 'Service Group 2':
                for i in range(0, 32):
                    if i < i_ds_sc_upper:
                        self.connection.send("interface cable-downstream 13/1/" + str(i) + " cable no shutdown\n")
                    else:
                        self.connection.send("interface cable-downstream 13/1/" + str(i) + " cable shutdown\n")

            i_ds_ofdm_upper = self.DS_OFDM
            if i_ds_ofdm_upper == 1:
                self.connection.send("interface cable-downstream 13/0/31 ofdm no shutdown\n")
            else:
                self.connection.send("interface cable-upstream 13/0/31 ofdm shutdown\n")

            i_us_sc_upper = self.US_SCQAM
            if self.Service_Group.GetValue() == 'Service Group 1':
                for i in range(0, 8):
                    if i < i_us_sc_upper:
                        self.connection.send("interface cable-upstream 0/0/" + str(i) + " cable no shutdown\n")
                    else:
                        self.connection.send("interface cable-upstream 0/0/" + str(i) + " cable shutdown\n")

            i_us_ofdma_upper = self.US_OFDMA
            if i_us_ofdma_upper == 1:
                self.connection.send("interface cable-upstream 1/0/24 ofdm no shutdown\n")
            else:
                self.connection.send("interface cable-upstream 1/0/24 ofdm shutdown\n")

        # Enter section of controlling C4C. ----------------------------------------------------------------------------
        elif self.CMTS_Choices.GetValue() == '':
            self.DS_SCQAM = int(self.DS_SCQAM_input.GetValue())
            self.DS_OFDM = int(self.DS_OFDM_input.GetValue())
            self.US_SCQAM = int(self.US_SCQAM_input.GetValue())
            self.US_OFDMA = int(self.US_OFDMA_input.GetValue())

            self.session.connect("172.21.37.254", port=22, username="root", password="")
            self.connection = self.session.invoke_shell()
            self.connection.send("enable\n")
            time.sleep(1)
            self.connection.send("config\n")
            time.sleep(1)
            print('-Connected-')

            if self.DS_SCQAM + self.DS_OFDM > 32 or self.DS_OFDM > 1 or self.US_OFDMA > 1:
                print('E6000 only support 32 maximum channels (sum of SC-QAM and OFDM).')
                print('E6000 only support 1 OFDM channel and only on Service Group 1.')
                print('E6000 only support 1 OFDMA channel and only on Service Group 2.')
                print('Please follow all rule mentioned above. Thanks!')
                return
            elif self.Service_Group.GetValue() == 'Service Group 1' and self.US_OFDMA > 0:
                print('Service Group 1 does not support OFDMA Frame.')
                return
            elif self.Service_Group.GetValue() == 'Service Group 2' and self.DS_OFDM > 0:
                print('Service Group 2 does not support OFDM Frame.')
                return
            elif self.Service_Group.GetValue() == 'No Setting' or self.Service_Group.GetValue() == 'Service Group 3':
                print('Only Service Group 1 & 2 supported.')
                return
            elif self.Service_Group.GetValue() == 'Service Group 1':
                if self.Provision_Mode.GetValue() == 'Dual Stack':
                    print('E6000 does not support dual stack mode.')
                    return
                elif self.Provision_Mode.GetValue() == 'IPv4 Only':
                    self.connection.send("interface cable-mac 1\n")
                    self.connection.send("cable cm-ip-prov-mode ipv4only\n")
                elif self.Provision_Mode.GetValue() == 'IPv6 Only':
                    self.connection.send("interface cable-mac 1\n")
                    self.connection.send("cable cm-ip-prov-mode ipv6only\n")
            elif self.Service_Group.GetValue() == 'Service Group 2':
                if self.Provision_Mode.GetValue() == 'Dual Stack':
                    print('E6000 does not support dual stack mode.')
                    return
                elif self.Provision_Mode.GetValue() == 'IPv4 Only':
                    self.connection.send("interface cable-mac 2\n")
                    self.connection.send("cable cm-ip-prov-mode ipv4only\n")
                elif self.Provision_Mode.GetValue() == 'IPv6 Only':
                    self.connection.send("interface cable-mac 2\n")
                    self.connection.send("cable cm-ip-prov-mode ipv6only\n")

            i_ds_sc_upper = self.DS_SCQAM
            if self.Service_Group.GetValue() == 'Service Group 1':
                for i in range(0, 31):
                    if i < i_ds_sc_upper:
                        self.connection.send("interface cable-downstream 13/0/" + str(i) + " cable no shutdown\n")
                    else:
                        self.connection.send("interface cable-downstream 13/0/" + str(i) + " cable shutdown\n")
            elif self.Service_Group.GetValue() == 'Service Group 2':
                for i in range(0, 32):
                    if i < i_ds_sc_upper:
                        self.connection.send("interface cable-downstream 13/1/" + str(i) + " cable no shutdown\n")
                    else:
                        self.connection.send("interface cable-downstream 13/1/" + str(i) + " cable shutdown\n")

            i_ds_ofdm_upper = self.DS_OFDM
            if i_ds_ofdm_upper == 1:
                self.connection.send("interface cable-downstream 13/0/31 ofdm no shutdown\n")
            else:
                self.connection.send("interface cable-upstream 13/0/31 ofdm shutdown\n")

            i_us_sc_upper = self.US_SCQAM
            if self.Service_Group.GetValue() == 'Service Group 1':
                for i in range(0, 8):
                    if i < i_us_sc_upper:
                        self.connection.send("interface cable-upstream 0/0/" + str(i) + " cable no shutdown\n")
                    else:
                        self.connection.send("interface cable-upstream 0/0/" + str(i) + " cable shutdown\n")

            i_us_ofdma_upper = self.US_OFDMA
            if i_us_ofdma_upper == 1:
                self.connection.send("interface cable-upstream 1/0/24 ofdm no shutdown\n")
            else:
                self.connection.send("interface cable-upstream 1/0/24 ofdm shutdown\n")

        else:
            print('Not Ready')

    # Close GUI
    def OnClose(self, event):
        self.Close(True)

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
        reverse = self.ClientReverse.GetValue()
        runtime = self.ClientTime.GetValue()
        parallel = self.ClientParallel.GetValue()
        bw = self.ClientBW.GetValue()
        test = 'iperf3 -c ' + str(ip)
        if udp:
            test = test + ' -u'
        if reverse:
            test = test + ' -R'
        if runtime != '':
            test = test + ' -t ' + str(runtime)
        if bw != '':
            test = test + ' -b ' + str(bw)
        if parallel != '':
            test = test + ' -P ' + str(parallel)
        print('Your entered command is: ' + test)
        print('Please wait for ' + str(runtime) + ' seconds.')
        file = open('Iperf_result.txt', 'w')
        output = subprocess.Popen(test, stdout=subprocess.PIPE)
        for line in output.stdout:
            print(line.decode('ascii'))
            file.write(line.decode('ascii'))
        file.close()
        myfile = open('Iperf_result.txt', 'r')
        for line in myfile:
            tmp = line.find('[SUM]   0.00-' + str(runtime) + '.00   sec')
            if tmp != -1:
                print('Total throughput is ' + line[38:42])
        myfile.close()


def main():
    ex = wx.App()
    ControllerFrame(None)
    ex.MainLoop()


if __name__ == '__main__':
    main()