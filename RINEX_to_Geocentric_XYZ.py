# -*- coding: utf-8 -*-
import datetime
from math import sqrt
from math import sin
from math import cos
from math import atan2
mi = 3.986005*(10**14)
oe = 7.2921151467*(10**(-5))

def day_of_week(r,m,d):
    week = datetime.date(r,m,d).weekday()
    if week >= 0 and week <6:
        week += 1
    elif week == 6:
        week = 0
    return week

t = 0
def time(week,h,m,s):
    t = float(week*24*60*60) + float(h*60*60) + float(m*60) + s
    return t

print "Podaj czas w formie dzien/miesiac/rok/godzina/minuty/sekundy np. 4/9/2013/12/30/00.0 (4 wrzesnia 2013, godzina 12:30:00)"
data = raw_input("Podaj czas: ")
p = raw_input("Podaj czas propagacji: ")

#RINEX_d28:
#20/3/2011/18/20/0.0
#0.0738237203352194

full_date = data.split("/")
dzien = int(full_date[0])
miesiac = int(full_date[1])
rok = int(full_date[2])
godzina = int(full_date[3])
minuta = int(full_date[4])
sekunda = float(full_date[5])

dow = day_of_week(rok,miesiac,dzien)
tsv = time(dow,godzina,minuta,sekunda)

RINEX = raw_input("Podaj RINEX: ")
rin = open(RINEX, 'r').read().split('\n')

ortorin = []
for every_line in rin:
    if every_line[0] == "-":
        ortorin.append(every_line)
    else:
        ortorin.append(" "+ str(every_line))

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

vl = []
for every_verse in ortorin:
    vl.append(list(chunkstring(every_verse, 19)))

variable_list = []
for items in vl[1:6]:
    items = [item.replace('D', 'E') for item in items]
    for every_element in items:
        variable_list.append(every_element)

IODE = float(variable_list[0])
Crs = float(variable_list[1])
DELTAn = float(variable_list[2])
M0 = float(variable_list[3])
Cuc = float(variable_list[4])
e = float(variable_list[5])
Cus = float(variable_list[6])
sqrtA = float(variable_list[7])
Toe = float(variable_list[8])
Cic = float(variable_list[9])
OMEGA0 = float(variable_list[10])
Cis = float(variable_list[11])
I0 = float(variable_list[12])
Crc = float(variable_list[13])
omega = float(variable_list[14])
OMEGADOT = float(variable_list[15])
Idot = float(variable_list[16])

a0 = float(ortorin[0][23:42].replace('D','E'))
a1 = float(ortorin[0][42:61].replace('D','E'))
a2 = float(ortorin[0][61:80].replace('D','E'))

#Obliczenia
#1.Poprawka zegara satelity
dt = a0 + a1*(tsv-Toe)+a2*((tsv-Toe)**2)
print "dt", dt
#2.Epoka odniesienia efemeryd
tk = tsv - Toe - dt
print "tk", tk
#3.Duza polos orbity satelity
a = sqrtA**2
print "a", a
#4.Ruch sredni satelity
n0 = sqrt(mi/(a**3))
print "n0", n0
#5.Poprawiony ruch sredni
n = n0 + DELTAn
print "n", n
#6.Anomalia srednia w epoce tk
Mk = M0 + n*tk
print "Mk", Mk
#7.Anomalia mimosrodowa
E=0
Ek=1
epsilon=1*10**(-15)
while abs(Ek-E)>epsilon:
    E=Ek
    Ek=Mk+e*sin(E)
print "Ek", Ek
#8.Anomalia prawdziwa (w = vk)
vk = atan2((sqrt(1-e**2)*sin(Ek)),(cos(Ek)-e))
print "vk", vk
#9.Argument szerokosci (u = Fik)
u = omega + vk
print "u", u
#10.Poprawka dla argumentu szerokosci
duk = Cus*sin(2*u)+Cuc*cos(2*u)
print "duk", duk
#11.Poprawka do promienia wodzacego
drk = Crs*sin(2*u)+Crc*cos(2*u)
print "drk", drk
#12.Poprawka dla kata nachylenia orbity
dik = Cis*sin(2*u)+Cic*cos(2*u)+Idot*tk
print "dik", dik
#13.Poprawiony argument szereokosci
uk = u + duk
print "uk", uk
#14.Poprawiony promien wodzacy
rk = a*(1-e*cos(Ek))+drk
print "rk", rk
#15.Poprawiona wartosc kata nachylenia orbity
ik = I0 + dik
print "ik", ik
#16.Poprawiona dlugosc wezla wstepujacego orbity
OMEGAk = OMEGA0 + (OMEGADOT-oe)*tk - oe*Toe
print "OMEGAk", OMEGAk
#17.Wspolrzedne satleity w plaszczyznie orbity (x', y' = s, ni)
s = rk*cos(uk)
ni = rk*sin(uk)
print "s", s
print "ni", ni
#18.Wspolrzedne geocentryczne
XG = s*cos(OMEGAk)-ni*cos(ik)*sin(OMEGAk)
YG = s*sin(OMEGAk)+ni*cos(ik)*cos(OMEGAk)
ZG = ni*sin(ik)

print
print "Wspolrzende w ukladzie XYZ:"
print "X:",XG
print "Y:",YG
print "Z:",ZG
print
print "dt:", dt
print tsv