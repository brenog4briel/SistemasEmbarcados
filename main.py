from config import utelegram_config
from config import wifi_config

import utelegram
import network
from machine import Pin
import utime

import machine
import time

p25 = machine.Pin(25, machine.Pin.OUT)
emergencia = machine.PWM(p25)
emergencia.freq(1047)
emergencia.deinit()


senha = "973821"
senhaDigitada = ""

estado = False
debug = True

p26 = machine.Pin(26,machine.Pin.IN)

p23 = machine.Pin(23, machine.Pin.OUT)
buzzer = machine.PWM(p23)
buzzer.freq(1047)
buzzer.deinit()

global cols 
global rows

cols = [5,4,2,15]
rows = [27,14,12,13]


for x in range(0,4):
    rows[x] = Pin(rows[x],Pin.OUT)
    rows[x].value(1)

for x in range(0,4):
    cols[x] = Pin(cols[x],Pin.IN,Pin.PULL_UP)


key_map = [['1','2','3','A'],['4','5','6','B'],['7','8','9','C'],['*','0','#','D']]

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.scan()
sta_if.connect(wifi_config['ssid'], wifi_config['password'])

if debug: print('WAITING FOR NETWORK - sleep 20')
utime.sleep(20)




def keypad(cols,rows):
    for r in rows:
        r.value(0)
        result = [cols[0].value(),cols[1].value(),cols[2].value(),cols[3].value()]

        if min(result) == 0:
            key = key_map[int(rows.index(r))] [int(result.index(0))]
            r.value(1)
            return (key)
        r.value(1)

def get_message(message):

  bot.send(message['message']['chat']['id'], "Comando invalido!")

def reply_start(message):

  print(message)
  bot.send(message['message']['chat']['id'], 'Ola, ja estou na sua residencia! Por favor, me informe a senha da fechadura!')

def reply_liberado(message):

  global estado

  if estado == True:
    print("O acesso ja esta liberado!")
  else:
      estado = True
      print(message)
      bot.send(message['message']['chat']['id'], 'Acesso liberado!')

def reply_negado(message):
  global estado

  if estado == True:
      estado = False
  else:	
      estado = False
      print(message)
      bot.send(message['message']['chat']['id'], 'Acesso negado!')

def fechadura(message):
    
    global senhaDigitada
    contador = 0
    while True:
      key = keypad(cols,rows)
      if key != None:
        print("Voce pressionou: "+ key)
        utime.sleep(0.2)
        senhaDigitada += key

        buzzer.init()
        buzzer.duty(20)
        time.sleep(0.1)
        buzzer.deinit()
        time.sleep(0.1)
        contador += 1
        if contador == len(senha):
          break
  
    if (estado == False) and (senhaDigitada == senha):
        print("Uma pessoa não autorizada desbloqueou a fechadura!")

        buzzer.init()
        buzzer.duty(30)
        bot.send(message['message']['chat']['id'], "Pessoa não autorizada na residencia! O alarme ja foi ativado!")

    elif (estado == False) and (senhaDigitada != senha):
        print("Uma pessoa não autorizada tentou desbloquear a fechadura!")

        buzzer.init()
        buzzer.duty(30)
        bot.send(message['message']['chat']['id'], "Pessoa não autorizada na residencia! O alarme ja foi ativado!")

    elif (estado == True) and (senhaDigitada != senha):
        print("Senha incorreta!")
        bot.send(message['message']['chat']['id'], "A senha que o senhor forneceu esta incorreta!")

    elif (estado == True) and (senhaDigitada == senha): 
        print("Estou entrando na residencia!")
        bot.send(message['message']['chat']['id'], "Estou entrando na residencia! Irei colocar o pacote aqui no cantinho.")
        start = 0
        while p26.value():
          start = time.time()

        stop = time.time()
        bot.send(message['message']['chat']['id'], "O entregador ficou " + str(round(stop - start,2)) + " segundos dentro de casa!")




if sta_if.isconnected():

  bot = utelegram.ubot(utelegram_config['token'])
  bot.register('/start', reply_start)
  bot.register('/liberar', reply_liberado)
  bot.register('/negar', reply_negado)
  bot.register('/teclado',fechadura)
  bot.set_default_handler(get_message)
  print("Aguardando comandos...")
  while True:
    bot.read_once()
    time.sleep(3)
else:
    print('NOT CONNECTED - aborting')

