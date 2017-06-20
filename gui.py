#!/usr/bin/python3
# -*- coding: utf-8 -*-

#Nacteni knihoven 
from tkinter import *
from tkinter.font import *
from random import randint
from time import sleep, localtime, strftime
import locale, urllib.request, json, math
import teplota

#Promenne
current_pozdrav = -1
pozdravy = ["Dobré ráno", "Dobré dopoledne", "Dobré poledne", "Dobré odpoledne", "Dobrý večer", "Dobrou noc"]
top = Tk()
needupdate = False
greeting_text = StringVar()

screen_width = top.winfo_screenwidth()
screen_height = top.winfo_screenheight()

#Promenne pro hodnoty hodin, data, teploty a vlhkosti - StringVar je funkci knihovny Tkinter, ze ktere nacitaji hodnoty popisky
hour_val = StringVar()
minute_val = StringVar()
date_val = StringVar()

city_val = StringVar()
status_val = StringVar()
icon_val = StringVar()
temp_val = StringVar()

act_temp_val = StringVar()
act_hum_val = StringVar()

#Promenne pro globalni ulozeni popisku stavu pocasi
status_label = ""
status_frame = ""

#Dvojtecka, ktera se nachazi v case
colon = StringVar()
colon.set(":")

json_icons = ""

sequence=0
dots=True

#Nastaveni vychohzich hodnot - cerne pozadi a beh aplikace na celou obrazovku
def set_fullscreen():
        global top
        top.attributes("-fullscreen", True)
        top.configure(background="black")


#Nastaveni labelu, ktery obsahuje pozdravy - Dobre rano, dopoledne, ...
def show_greeting():
        global top, labeltext, pozdravy
        label = Label(top, textvariable=greeting_text, bg="black", fg="white", font=("Roboto thin", 44), pady = 20)
        new_greeting()

        label.pack(side=BOTTOM)

#Zobrazeni hlavicky; nastaveni vysky (200px); zavolani funkci, ktere obsluhuji dalsi casti hlavicky a nacteni hodnot
def show_header():
        global top, screen_width, cas_label, cas_val, screen_height
        parent_forecast_frame = Frame(top, height=200)
        parent_forecast_frame.pack(side=TOP, fill=X)

        show_center_datetime(parent_forecast_frame)
        show_left_actual_temp(parent_forecast_frame)
        show_right_forecast(parent_forecast_frame)
        update_forecast()
        update_act_temp()
        update_act_hum()

#Zobrazeni prostredni casti hlavicky - casu a data
def show_center_datetime(parent):
		global hour_val, minute_val, colon, date_val, screen_width

		#Cely time a date frame, zabira 1/3 sirky obrazovky a 200px vysky
		center_time_frame = Frame(parent, bg="black")
		center_time_frame.place(height=200, width=screen_width/3, x=screen_width/3, y=0)
		
		#Main time frame - snizuje vysku na 150px, zarovnava dolu
		main_time_frame = Frame(center_time_frame, bg="black")

		#Time frame, pouze pro hodiny bez data, sirku prizpusobuje obsahu, horizontalne se centruje, obsahuje veskere time labely
		time_frame = Frame(main_time_frame, bg="black")		

		#Time labely a date label, carka je oddelena kvuli blikani
		hour_label = Label(time_frame, textvariable=hour_val, bg="black", fg="white", font=("Roboto thin", 72))
		colon_frame = Frame(time_frame, width=20, height=133, bg="black")
		colon_label = Label(colon_frame, textvariable=colon, bg="black", fg="white", font=("Roboto thin", 72))
		minute_label = Label(time_frame, textvariable=minute_val, bg="black", fg="white", font=("Roboto thin", 72))
		date_label = Label(center_time_frame, textvariable=date_val, bg="black", fg="white", font=("Roboto thin", 25))

		#Zobrazeni time a date labelu (place zarovnava na stred, grid rozmistuje obsah hodin)
		main_time_frame.place(x=0, height=150, width=screen_width/3, y=0)
		time_frame.place(relx=0.5, y=66, anchor=CENTER)
		hour_label.grid(column=0, row=0, sticky=W)
		colon_frame.grid(column=1, row=0, sticky=W)
		minute_label.grid(column=2, row=0, sticky=W)
		colon_label.place(x=0, y=0)
		date_label.place(x=0, height=50, width=screen_width/3, y=150)

		#Aktualizace hodin a data
		time_update()
		date_update()

		#Funkce update zajisti, aby se data okamzite zobrazila na obrazovce
		center_time_frame.update()


# Zobrazi pravou cast hlavicky, rozdeli tuto cast na ctyri mensi casti, ktere obsahuji jednotlive hodnoty
def show_right_forecast(parent):
		#Vytvori zakladni frame pro pravou cast hlavicky
		global screen_width, temp_val, city_val, status_val, icon_val, status_label, status_frame
		right_forecast_frame = Frame(parent, bg="black")
		right_forecast_frame.place(height=200, width=screen_width/3, x=screen_width/3*2, y=0)
		right_forecast_frame.update()

		#Frame a label pro zobrazeni teploty, na sirku zabira 1/2 prave casti, na vysku zabira 3/4 prave casti
		temp_frame = Frame(right_forecast_frame, bg="black")
		temp_frame.place(x=screen_width/6, height=150, width=screen_width/6, y=0)
		temp_label = Label(temp_frame, textvariable=temp_val, bg="black", fg="white", font=("Roboto thin", 50), anchor=NE)
		temp_label.place(relx=0.5, rely=0.5, anchor=CENTER)

		#Frame a label pro zobrazeni ikony aktualniho stavu pocasu, na sirku zabira 1/2 prave casti, na vysku zabira 3/4 prave casti, pro zobrazeni se vyuziva specialni pismo Weather Icons, ktere obsahuje znaky pro jednotlive druhy pocasi. Stavy a ikony se prirazuji v souboru icons.json, ze ktereho program cte.
		icon_frame = Frame(right_forecast_frame, bg="black")
		icon_frame.place(x=0, height=150, width=screen_width/6, y=0)
		icon_label = Label(icon_frame, textvariable=icon_val, bg="black", fg="white", font=("Weather Icons", 50), anchor=NE)
		icon_label.place(relx=0.5, rely=0.5, anchor=CENTER)

		#Frame a label pro zobrazeni nazvu mesta, na sirku zabira 1/2 prave casti, na vysku zabira 1/4 prave casti
		city_frame = Frame(right_forecast_frame, bg="black")
		city_frame.place(x=screen_width/6, height=50, width=screen_width/6, y=150)
		city_label = Label(city_frame, textvariable=city_val, bg="black", fg="white", font=("Roboto thin", 25), anchor=NE)
		city_label.place(relx=0.5, rely=0.5, anchor=CENTER)

		#Frame a label pro zobrazeni akutalniho stavu pocasi, na sirku zabira 1/2 prave casti, na vysku zabira 1/4 prave casti
		status_frame = Frame(right_forecast_frame, bg="black")
		status_frame.place(x=0, height=50, width=screen_width/6, y=150)
		status_label = Label(status_frame, textvariable=status_val, bg="black", fg="white", font=("Roboto thin", 20), anchor=NE)
		status_label.place(relx=0.5, rely=0.5, anchor=CENTER)

#Zobrazi levou cast hlavicky, ktera obsahuje aktualni teplotu a vlhkost merenou senzorem DHT11, ktery se nachazi pod RPi (viz Schema zapojeni)
def show_left_actual_temp(parent):
		#Vytvori zakladni frame pro levou cast hlavicky
		global screen_width, act_temp_val, act_hum_val
		left_forecast_frame = Frame(parent, bg="black")
		left_forecast_frame.place(height=200, width=screen_width/3, x=0, y=0)
		left_forecast_frame.update()
		
		#Frame a label pro zobrazeni teploty, na sirku zabira celou levou cast, ale obsah se centruje doprostred, na vysku zabira 3/4 leve casti
		left_temp_frame = Frame(left_forecast_frame, bg="black")
		left_temp_frame.place(x=0, height=150, width=screen_width/3, y=0)
		left_temp_label = Label(left_temp_frame, textvariable=act_temp_val, bg="black", fg="white", font=("Roboto thin", 50), anchor=CENTER)
		left_temp_label.place(relx=0.5, rely=0.5, anchor=CENTER)

		#Frame a label pro zobrazeni teploty, na sirku zabira celou levou cast, ale obsah se centruje doprostred, na vysku zabira 1/4 leve casti
		left_hum_frame = Frame(left_forecast_frame, bg="black")
		left_hum_frame.place(x=0, height=50, width=screen_width/3, y=150)
		left_hum_label = Label(left_hum_frame, textvariable=act_hum_val, bg="black", fg="white", font=("Roboto thin", 25), anchor=CENTER)
		left_hum_label.place(relx=0.5, rely=0.5, anchor=CENTER)

#Slouzi pro zobrazeni spravneho pozdravu podle casu. Hodiny, ve ktere se pozdravy meni jsou 4 (Dobre rano), 8 (Dobre dopoledne), 12 (Dobre poledne), 13 (Dobre odpoledne), 18 (Dobry vecer) a 22 (Dobrou noc). Casy se nacitaji z pole pozdravy, umistenem na zacatku kodu.
def new_greeting():
		global greeting_text, current_pozdrav, hour_val, pozdravy
		hodina = hour_val.get()
		if(hodina == "4" and current_pozdrav != 0):
				current_pozdrav = 0
				greeting_text.set(pozdravy[0])
		if(hodina == "8" and current_pozdrav != 1):
				current_pozdrav = 1
				greeting_text.set(pozdravy[1])
		if(hodina == "12" and current_pozdrav != 2):
				current_pozdrav = 2
				greeting_text.set(pozdravy[2])
		if(hodina == "13" and current_pozdrav != 3):
				current_pozdrav = 3
				greeting_text.set(pozdravy[3])
		if(hodina == "18" and current_pozdrav != 4):
				current_pozdrav = 4
				greeting_text.set(pozdravy[4])
		if(hodina == "22" and current_pozdrav != 5):
				current_pozdrav = 5
				greeting_text.set(pozdravy[5])
				
				
#Funkce nacita aktualni cas. Zajistuje take, aby dvojtecka kazdou vterinu blikala
def time_update():
        global hour_val, minute_val, colon, dots
        hour_val.set(strftime("%H", localtime()))
        minute_val.set(strftime("%M", localtime()))
        if (colon.get() == ":" and dots == False):
        		colon.set("")
        else:
        		colon.set(":")
        #O pulnoci zavola funkci pro nacteni noveho data
        if strftime("%H:%M", localtime()) == "00:00":
                date_update()
#Nacte nove datum ze systemu
def date_update():
        global date_val
        date_val.set(strftime("%d. %B %Y", localtime()))

#Nacte aktualni stav pocasi z api openweathermap.org
def update_forecast():
		global icon_val, temp_val, status_val, city_val, json_icons, status_label, status_frame

		raw_data = get_url('http://api.openweathermap.org/data/2.5/weather?id=3068293&appid=1b16cf7d15e5e1b535b8379f469b8cc4&units=metric')

		#Nacte json data do pole
		data = json.loads(raw_data)

		#Nastavi ikonu, kterou vybere ze souboru icons.json podle ID stavu pocasi - viz https://openweathermap.org/current
		icon_val.set(json_icons[str(data["weather"][0]["id"])]["icon"])

		#Pomoci funkce translate prelozi anglicky stav pocasi a nastavi ho 
		translated_status = translate(data["weather"][0]["description"])
		status_val.set(translated_status)

		#Nastavi teplotu a prelozeny nazev mesta
		temp_val.set(str(round(data["main"]["temp"])) + "°C")
		city_val.set(translate(data["name"]))

		#Odstrani label status a vytvori novy - tento postup se provadi z duvodu nastaveni libovolne velikosti pisma - dlouhe stavy pocasi se do popisku normalni velikosti nevesly
		status_label.destroy()
		status_label = Label(status_frame, textvariable=status_val, bg="black", fg="white", font=("Roboto thin", font_size(translated_status, "Roboto thin", 25, 176)), anchor=NE)
		status_label.place(relx=0.5, rely=0.5, anchor=CENTER)

#Vypocte maximalni velikost pisma, aby se text vesel do zadaneho popisku
def font_size(text, ff, fs, max_width):
		size = fs

		#Funkce zmeri, jak dlouhy je text. Pokud je prilis dlouhy, zmensi velikost pisma o jeden pixel a zmeri znovu. Pokud se text vejde do zadaneho popisku, vrati velikost pisma.
		while measure(text, ff, size) > max_width:
				size = size - 1
		return size

#Funkce, ktera meri sirku a vysku textu (pouziva se pouze sirka)
def measure(text, ff, fs):
		#Vytvori novy Tkinter modul
		root = Tk()

		#Nastavi velikost a druh pisma
		font = Font(family=ff, size=fs)

		#Zmeri, jak je zadany text siroky a vysoky
		w, h = (font.measure(text), font.metrics("linespace"))

		#Odstrani modul, ktery se pouzil pro mereni
		root.destroy()

		#vrati sirku, kterou zmeril
		return w

#Zavola funkci z nasi knihovny pro zmereni teploty a nastavi ji
def update_act_temp():
		global act_temp_val

		act_temp_val.set(str(teplota.read_temp()) + "°C")

#Zavola funkci z nasi knihovny pro zmereni vlhkosti a nastavi ji
def update_act_hum():
		global act_hum_val

		act_hum_val.set(str(teplota.read_hum()) + " %")

#Odesle GET pozadavek obsahujici cilovy jazyk a puvodni text na API Google prekladace, ktery vrati prelozeny text. 
def translate(data):
		url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=cs&dt=t&q=" + urllib.parse.quote(data)
		data = json.loads(get_url(url))

		#Vrati pouze prelozeny text
		return data[0][0][0]

#Pomoci knihovny urllib vyvola pozadavek na stranku, zpracuje a vrati zdrojovy kod
def get_url(url):
		#Pro zajisteni nejvetsi kompatibility se pouziva User Agent z prohlizece Chrome verze 58
		rq = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", 'content-type': 'application/json'})
		return urllib.request.urlopen(rq).read().decode('UTF-8')

#Nacte veskere zmeny provedene v GUI (zmena textu, ...)
def do_update():
        global top
        top.update()
        top.update_idletasks()

#Zajistuje provedeni veskerych zmen. Nektere zmeny se oprakuji pouze kazdych 5 sekund, nektere kazdych 5 minut. Jako prevence preteceni promenne sequence tuto promenou po 5 minutach nastavime na 0
def update_tasks():
        global sequence
        time_update()
        if sequence % 5 == 0:
                new_greeting()

        if sequence == 300:
        		update_act_temp()
        		update_act_hum()
        		update_forecast()
        		sequence = 0

#Nacte hodnoty ze souboru icons.json - tyto hodnoty ulozi do promenne json_icons, ktere se pouzivaji pro zobrazovani ikon pocasi
def load_icons():
		global json_icons

		file = open("icons.json", "r")
		json_icons = json.loads(file.read())
		file.close()


#Start programu, pomocí funkce locale nastavi ceskou lokalizaci
set_fullscreen()
locale.setlocale(locale.LC_ALL, "cs_CZ.UTF8")
load_icons()
show_header()
show_greeting()

do_update()
dots = False

#Nekonecna smycka, ktera zajistuje aby se program aktualizoval a neukoncil.
while 1:
        sequence = sequence + 1
        update_tasks()
        do_update()
        sleep(1)
