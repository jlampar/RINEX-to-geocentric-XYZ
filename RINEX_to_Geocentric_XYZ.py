# -*- coding: utf-8 -*-
import datetime
from math import sqrt
from math import sin
from math import cos
from math import atan2

class SateliteTime(object):
    def __init__(self,d,mth,y,h,min,s,prop):
        self.d = d
        self.mth = mth
        self.y = y
        self.h = h
        self.min = min
        self.s = s
        self.prop = prop

    def time(self):
        week = datetime.date(self.y, self.mth, self.d).weekday()
        if week >= 0 and week < 6:
            week += 1
        elif week == 6:
            week = 0
        return float(week * 24 * 60 * 60) + float(self.h * 60 * 60) + float(self.min * 60) + self.s

class RINEX(object):

    mi = 3.986005*(10**14)
    oe = 7.2921151467*(10**(-5))

    def __init__(self,file):
        self.file = file

    def extract(self):
        open_file = open(self.file, 'r').read().split('\n')
        first_iter = []
        for every_line in open_file:
            if every_line[0] == "-":
                first_iter.append(every_line)
            else:
                first_iter.append(" " + str(every_line))

        second_iter = []
        for every_verse in first_iter:
            second_iter.append(list(every_verse[0 + i:19 + i] for i in range(0, len(every_verse), 19)))

        variables = []
        for items in second_iter[1:6]:
            items = [item.replace('D', 'E') for item in items]
            for every_element in items:
                variables.append(float(every_element))

        variables.append(float(first_iter[0][23:42].replace('D', 'E')))
        variables.append(float(first_iter[0][42:61].replace('D', 'E')))
        variables.append(float(first_iter[0][61:80].replace('D', 'E')))

        return variables
        # [33.0(IODE), 56.1875(Crs), 4.54483216765e-09(DELTAn), -2.88842646276(M0), 2.83680856228e-06(Cuc), 0.0169634080958(e), 5.29177486897e-06(Cus), 5153.68485069(sqrtA), 64800.0(Toe), 2.14204192162e-07(Cic), -1.79229306516(OMEGA0), -1.26659870148e-07(Cis), 0.973313017457(I0), 282.21875(Crc), -1.89637567079(omega), -7.93497338063e-09(OMEGADOT), 5.64666377764e-10(Idot), 1.0(nd), 1628.0(nd), 0.0(nd), 2.63666734099e-05(a0), 2.27373675443e-12(a1), 0.0(a2)]
        # [IODE(0), Crs(1), DELTAn(2), M0(3), Cuc(4), e(5), Cus(6), sqrtA(7), Toe(8), Cic(9), OMEGA0(10), Cis(11), I0(12), Crc(13), omega(14), OMEGADOT(15), Idot(16), nd(17), nd(18), nd(19), a0(20), a1(21), a2(22)]

    def dt(self,mat,t):
        return (mat[20] + mat[21]*(t-mat[8]) + mat[22]*((t-mat[8])**2))

    def get_coordinates(self,arr,t,dt):
        tk = t - arr[8] - dt # epoka odniesienia efemeryd
        a = arr[7] ** 2 # duza polos orbity satelity
        n0 = sqrt(self.mi / (a ** 3)) # ruch sredni satelity
        n = n0 + arr[2] # poprawiony ruch sredni
        Mk = arr[3] + n * tk # 6.Anomalia srednia w epoce tk
        E = 0
        Ek = 1
        epsilon = 1 * 10 ** (-15)
        while abs(Ek - E) > epsilon:
            E = Ek
            Ek = Mk + arr[5] * sin(E) # anomalia mimosrodowa
        vk = atan2((sqrt(1 - arr[5] ** 2) * sin(Ek)), (cos(Ek) - arr[5])) # anomalia prawdziwa (w = vk)
        u = arr[14] + vk # argument szerokosci (u = Fik)
        duk = arr[6] * sin(2 * u) + arr[4] * cos(2 * u) # poprawka dla argumentu szerokosci
        drk = arr[1] * sin(2 * u) + arr[13] * cos(2 * u) # poprawka do promienia wodzacego
        dik = arr[11] * sin(2 * u) + arr[9] * cos(2 * u) + arr[16] * tk # poprawka dla kata nachylenia orbity
        uk = u + duk # poprawiony argument szereokosci
        rk = a * (1 - arr[5] * cos(Ek)) + drk # poprawiony promien wodzacy
        ik = arr[12] + dik # poprawiona wartosc kata nachylenia orbity
        OMEGAk = arr[10] + (arr[15] - self.oe) * tk - self.oe * arr[8] # poprawiona dlugosc wezla wstepujacego orbity
        s = rk * cos(uk)
        ni = rk * sin(uk) # wspolrzedne satleity w plaszczyznie orbity (x', y' = s, ni)
        # Wspolrzedne geocentryczne:
        XG = s * cos(OMEGAk) - ni * cos(ik) * sin(OMEGAk)
        YG = s * sin(OMEGAk) + ni * cos(ik) * cos(OMEGAk)
        ZG = ni * sin(ik)

        return (XG, YG, ZG)

#Przykładowe dane dla pliku RINEX_d28
#20.03.2011, 18:20:00
#czas propagacji: 0.0738237203352194

path = raw_input("Podaj ścieżkę do pliku RINEX: ")
print
print "Podaj dokładny czas obserwacji:"
dzien = int(raw_input("Dzień: "))
miesiac = int(raw_input("Miesiąc: "))
rok = int(raw_input("Rok: "))
godzina = int(raw_input("Godzina: "))
minuta = int(raw_input("Minuta: "))
sekunda = float(raw_input("Sekunda: "))
print
propag = float(raw_input("Podaj czas propagacji: "))
print

time = SateliteTime(dzien,miesiac,rok,godzina,minuta,sekunda,propag).time()
print "Sekundy zegara satelity: ", time

rinex_file = RINEX(path)

matrix = rinex_file.extract()
delta = rinex_file.dt(matrix,time)
coordinates = rinex_file.get_coordinates(matrix,time,delta)

print "Poprawka zegara satelity: ", delta
print "Współrzędne geocentryczne XYZ: ", coordinates
