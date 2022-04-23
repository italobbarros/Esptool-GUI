import PySimpleGUI as sg
import esptool
import os
import requests
import json 
import serial.tools.list_ports

sg.theme('Dark')   # Add a touch of color
# All the stuff inside your window.
section_caminho = [[sg.Text('IP',size=(10,0),justification='center'), sg.InputText(size=(22,0),key='IPLabel',default_text='http://www.smartm.com.br'),sg.Text(':'), sg.InputText(size=(5,0),key='portaLabel',default_text='80'),sg.Text('/'), sg.InputText(size=(30,0),key='caminhoLabel',default_text='firmwares/solplace/solplaceV03.bin'),sg.InputCombo(['GET','MQTT'],size=(10,0),key='protocolLabel',default_value='GET')]]
section_firmware = [[sg.Text('Firmware',size=(10,0),justification='center'), sg.InputText(size=(65,0),key='firmwareLabel'),sg.FileBrowse(target='firmwareLabel')]]

def collapse(layout, key, visible):
    return sg.pin(sg.Column(layout, key=key, visible=visible, pad=(0,0)))


def verificar_portas():
    portas = ['Auto']
    ports = serial.tools.list_ports.comports(include_links=False)
    for port in ports :
        portas.append(port[0])
    return portas

portas_ativas =['Auto']
layout1 = [ [sg.Text('Settings',size=(1000,0),justification='center',font=('Helvitica',18))],
            [sg.Text('Com',size=(5,0),justification='center'),sg.Button('R',size=(3,0)), sg.InputCombo(verificar_portas(),size=(10,0),default_value='Auto',key='comLabel'),sg.Text('Baudrate',size=(10,0),justification='center'), sg.InputCombo(['115200','256000','512000'],size=(10,0),key='uploadSpeedLabel',default_value='115200'),sg.Text('MCU',size=(10,0),justification='center'), sg.InputCombo(['ESP32','ESP8266'],size=(10,0),key='MCULabel')],        
            [sg.Text('Flash mode',size=(10,0),justification='center'), sg.InputCombo(['dio','dout','qio','qout'],size=(10,0),key='flashModeLabel'),sg.Text('Flash freq',size=(10,0),justification='center'), sg.InputCombo(['40m','80m'],size=(10,0),key='flashFreqLabel'),sg.Text('Flash size',size=(10,0),justification='center'), sg.InputCombo(['2MB','4MB','8MB','16MB'],size=(10,0),key='flashSizeLabel')],           
            [sg.Text('_________________________________________________________________________',size=(1000,0),justification='center')],
            [sg.Text('Upload',size=(1000,0),justification='center',font=('Helvitica',18))],
            [sg.Text('Tipo',size=(10,0),justification='center'), sg.InputCombo(['Fisico','Nuvem'],default_value='Fisico',size=(10,0),key='tipoLabel')],
            [collapse(section_firmware,'sec_firmware',False)],
            [collapse(section_caminho,'sec_caminho',True)],
            [sg.Text('Perfil',size=(10,0),justification='center'), sg.InputCombo(['MANUAL','ESP32WROVER','ESP8266'], size=(47,0),key='perfilLabel',default_value='ESP32WROVER'),sg.Button('Save',size=(15,0),button_color='green')],
            [sg.Button('Write',size=(15,0),pad=((238,25),(20,20)),button_color='Green'), sg.Button('Erase',size=(15,0),pad=((25,200),(20,20)),button_color='red')],            
            #[sg.Output(key='-OUT-',size=(90,20))]
            ]
          

def GUI():
    global perfil
    perfil = 0 
    window = sg.Window('Esptool GUI - by Italo Barros', layout1,font=('Helvitica',12),size=(1000,400),margins=((100,20)))
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            break
        if event == 'R':
            reloadCom(window)
        perfilTest(values,window)
        savePerfil(values,event) 
        tipoTest(values,window)
        if event == 'Write': # if user closes window or clicks cancel
            writeMCU(values,window)
        elif event == 'Erase': # if user closes window or clicks cancel
            clearMCU(values)            
    window.close()

def writeMCU(values,window):
    try:
        if(values['tipoLabel'] == 'Nuvem'):
            try:
                print("baixando da nuvem...")
                if(values['protocolLabel']=='GET'):
                    print('GET requisition')
                    response = requests.get(url=(values['IPLabel']+':'+values['portaLabel']+'/'+values['caminhoLabel']))  
                    firmwareData = open("configsetup\\DataFirmware.bin", "wb")
                    firmwareData.write(response.content)
                    firmwareData.flush()
                    print("baixou!")                    
                elif(values['protocolLabel']=='MQTT'):
                    print('MQTT requisition')
                    print('Nao desenvolvido')
                valuesNuvem = values
                valuesNuvem['firmwareLabel'] = 'configsetup\\DataFirmware.bin'
                activeEsptool(valuesNuvem)
            except firmwareData:
                print("ERROR: Não baixou da nuvem!")
        else:
            activeEsptool(values)
    except:
        print("ERROR: NÃO FOI POSSIVEL GRAVAR!")

def activeEsptool(values):
    try:
        print("Gravando...")
        if(values['MCULabel']== 'ESP8266'):
            if(values['comLabel'] =='Auto'):
                writeFlash = ['--baud', values['uploadSpeedLabel'],'--chip','ESP8266' ,'write_flash','--flash_mode', values['flashModeLabel'],'--flash_freq',values['flashFreqLabel'],'--flash_size',values['flashSizeLabel'],'0x0000', values['firmwareLabel']]                                        
            else:
                writeFlash = ['--baud', values['uploadSpeedLabel'],'-p',values['comLabel'],'--chip','ESP8266' ,'write_flash','--flash_mode', values['flashModeLabel'],'--flash_freq',values['flashFreqLabel'],'--flash_size',values['flashSizeLabel'],'0x0000', values['firmwareLabel']]                                  
                closeSerial(values)
        elif(values['MCULabel']== 'ESP32'):
            if(values['comLabel'] =='Auto'):
                writeFlash = ['--baud', values['uploadSpeedLabel'],'--chip','ESP32', 'write_flash','--flash_mode', values['flashModeLabel'],'--flash_freq',values['flashFreqLabel'],'--flash_size',values['flashSizeLabel'],'0x1000',str(os.getcwd())+'\\configsetup\\bootloaderESP32\\bootloader_'+values['flashModeLabel']+'_'+values['flashFreqLabel']+'.bin','0x8000', str(os.getcwd())+'\\configsetup\\partitions.bin', '0Xe000', str(os.getcwd())+'\\configsetup\\boot_app0.bin', '0X10000', values['firmwareLabel']]                                                     
            else:
                writeFlash = ['--baud', values['uploadSpeedLabel'],'-p',values['comLabel'],'--chip','ESP32', 'write_flash','--flash_mode', values['flashModeLabel'],'--flash_freq',values['flashFreqLabel'],'--flash_size',values['flashSizeLabel'],'0x1000',str(os.getcwd())+'\\configsetup\\bootloaderESP32\\bootloader_'+values['flashModeLabel']+'_'+values['flashFreqLabel']+'.bin','0x8000', str(os.getcwd())+'\\configsetup\\partitions.bin', '0Xe000', str(os.getcwd())+'\\configsetup\\boot_app0.bin', '0X10000', values['firmwareLabel']]                                                         
                closeSerial(values)
        esptool.main(writeFlash)
        sg.Popup('Firmware Carregado!')
    except:
        print("ERROR: Não gravou!")

def closeSerial(values):
    ser = serial.Serial()
    ser.port = values['comLabel']
    ser.close() 

def clearMCU(values):
    try:
        if(values['comLabel'] =='Auto'):
            eraseFlash = ['--baud', values['uploadSpeedLabel'], 'erase_flash']
        else:              
            eraseFlash = ['--baud', values['uploadSpeedLabel'],'-p',values['comLabel'], 'erase_flash']           
        esptool.main(eraseFlash)
        closeSerial(values)
        sg.Popup('Flash Limpa')
    except:
        print("ERROR: NÃO FOI POSSIVEL LIMPAR!")   


def tipoTest(values,window):
    if(values['tipoLabel'] == 'Fisico'):
        window['sec_firmware'].update(visible=True)
        window['sec_caminho'].update(visible=False)
    elif(values['tipoLabel'] == 'Nuvem'):
        window['sec_firmware'].update(visible=False)
        window['sec_caminho'].update(visible=True)

def savePerfil(values,event):
    if(event == 'Save'):
        try:
            print("Salvando Perfil"+values['perfilLabel'])
            json_object = json.dumps(values)
            jsonPerfil = open('configsetup\\perfil\\'+values['perfilLabel'] + ".json", "w")
            jsonPerfil.write(json_object)
            jsonPerfil.flush()
        except:
            print("Não foi possivel salvar!")
def readPerfil(values,event):
    try:
        print("Read Perfil"+values['perfilLabel'])
        jsonPerfil = open('perfil/'+values['perfilLabel'] + ".json", "r")
        json_object = json.load(jsonPerfil)
        print(json_object)
        return json_object
    except:
        print("Não foi possivel ler!")

def listPerfil():
    print("listando perfis...")

def reloadCom(window):
    window['comLabel'].Update(value='',values=verificar_portas())

def perfilTest(values,window):
    global perfil
    if((values['perfilLabel']== 'MANUAL') and (perfil != 1)):
        print('Perfil manual carregado')
        perfil = 1   
    elif((values['perfilLabel']== 'ESP32WROVER') and (perfil != 2)):
        window['flashModeLabel'].Update('dio')
        window['flashFreqLabel'].Update('80m')
        window['flashSizeLabel'].Update('4MB')
        window['MCULabel'].Update('ESP32')
        print('Perfil ESP32WROVER carregado')
        perfil = 2
    elif((values['perfilLabel']== 'ESP8266') and (perfil != 3)):
        #sg.Popup('Perfil ESP8266 nao desenvolvido!')
        window['flashModeLabel'].Update('dout')
        window['flashFreqLabel'].Update('40m')
        window['flashSizeLabel'].Update('2MB')
        window['MCULabel'].Update('ESP8266')
        print('Perfil ESP8266 carregado')
        perfil = 3
                
if __name__ == '__main__':
    GUI()
    print('Exiting Program')