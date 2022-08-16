# ----------------------------------------------------------------------------
# Russian Roulette
# Copyright © 2022 Sergey Chernov aka Gamer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk, colorchooser
from tkinter import messagebox as mb
from random import randint
from enum import Enum
import codecs
import time
from threading import Timer
root = tk.Tk()
root.geometry("1060x800")
root.resizable(width=False, height=False)
canvas = tk.Canvas(root, width=640, height=480, bg='#ffffff')
PLACES_X = [2, 1, 1, 2, 3, 3]
PLACES_Y = [3.7, 3, 2, 1.3, 2, 3]
place_answers = []
place_ans1 = [[20, 560], [270, 560]]
place_answers.append(place_ans1)
place_ans2 = [[20, 560], [270, 560], [20, 660]]
place_answers.append(place_ans2)
place_ans3 = [[20, 560], [270, 560], [20, 660], [270, 660]]
place_answers.append(place_ans3)
place_ans4 = [[20, 560], [200, 560], [380, 560], [110, 660], [290, 660]]
place_answers.append(place_ans4)
blinking_colors = ['#cfcfcf', '#ffffff']
KOLVO_IGROKOV = 5 #5
TIMER = 20
TIMER_FINAL = 10
canvas.place(x=10, y=19)
hatches = []
saved = []
player_start = [] #поле для ввода имён игроков
start_names = [] #переменные с именами игроков
igroki_na_liukah = []
playerlabels, playermoney = [], []
class stadija(Enum):
    pre_round = 1
    after_wrong = 2
    bonus_round = 3
    noone_dropped = 4
    during_round = 5
who_asks_q = None
who_answers_q = None
pre_game = True
game_stage = stadija.pre_round
spalvos = ["#ff0000", "#009fff", "#ffffff"]
round_number = 6-KOLVO_IGROKOV #1
questions_in_round = [7, 6, 5, 4] #7654
for_correct = [1000, 2000, 3000, 4000]
final_tree = [0, 50000, 100000, 1000000]
final_hatchesopen = [None, 3, 4, 5]
dropzones_1234 = []
mex_num = 0
base_for_round = []
num_q_active = None
time_left = 0
timer_started = False
podsvetka = [[0], [0, 3], [0, 2, 4], [0, 1, 3, 4]]
host_center = [280, 230, 294, 244]
class stadija_scheta(Enum):
    before = 1
    during = 2
    posle = 3
stage_final = 0
pereschet = stadija_scheta.before
i = 0
will_fall = None
winner = None
occupied_by_winner, occupied_by_host = None, None
winner_islookingfor_hatch = False
final_read = False
log = open('log.txt', 'a')
vopros_finala = 0

class answer_in_final(Enum):
    wrong = 0
    right = 1
    no_final = 2

final = answer_in_final.no_final
#start_timerok, start_timerok2, start_timerok3 = None, None, None


def doSomething():
    if tk.messagebox.askyesno("Exit", "Do you want to quit the application?"):
        log.close()
        root.destroy()


def mex_works():
    global mex_num, canvas, game_stage, will_fall, round_number, stage_final
    root.after_cancel(root.mex_spin)
    if (round_number in (1,2,3,4)):
        if game_stage == stadija.pre_round:
            #print('pre-round')
            mex_begin_st_round()
            mex_num +=1
            for j in range(6):
                if (mex_num % 6 == j):
                    canvas.itemconfig(hatches[j], fill = "#ffffff")
                else:
                    canvas.itemconfig(hatches[j], fill = "#cfcfcf")
        elif game_stage == stadija.noone_dropped:
            for j in range(6):
                canvas.itemconfig(hatches[j], fill="#cfcfcf")
            mex_num += 1
            for k in range(KOLVO_IGROKOV):
                if (k in saved) or (aux_list[k]['in_game'] is False):
                    pass
                else:
                    canvas.itemconfig(hatches[k+1], fill = blinking_colors[mex_num % 2])
            while True:
                will_fall = randint(0, KOLVO_IGROKOV-1)
                if (will_fall not in saved) and (aux_list[will_fall]['in_game']): #nujno
                    break #nujno
            #print('Механизм крутится. Игру покинет ' + aux_list[will_fall]['name'])
        elif game_stage == stadija.after_wrong:
            for uj in range(len(podsvetka[round_number-1])):
                podsvetka[round_number-1][uj] += 1
                if podsvetka[round_number-1][uj] > 5:
                    podsvetka[round_number - 1][uj] = podsvetka[round_number-1][uj] % 6
            for j in range(6):
                if (j % 6 in podsvetka[round_number-1]):
                    canvas.itemconfig(hatches[j], fill = "#ff0000")
                else:
                    canvas.itemconfig(hatches[j], fill = "#00ffff")
            playingrr_1234(round_number) #(round_number)
            #print('after-wrong')
    else:
        mex_num += 1
        mex_bonus_round(stage_final)
        for e in range(6):
            canvas.itemconfig(hatches[e], fill = blinking_colors[randint(0, len(blinking_colors)-1)])
    root.mex_spin = root.after(250, mex_works)

def update_money():
    for j in range(KOLVO_IGROKOV):
        playermoney[j]['text'] = aux_list[j]['money']

def playingrr_1234(dd):
    global dropzones_1234
    dropzones_1234 = []
    for qq in range(dd): #dd
        while True:
            aux = randint(0, 5)
            if not (aux in dropzones_1234):
                dropzones_1234.append(aux)
                break
    #print(dropzones_1234)


def host_move(variable):
    x, y, x1, y1 = canvas.coords(igroki_na_liukah[variable])
    #_x, _y, _x1, _y1 = None, None, None, None
    canvas.coords(host, ((host_center[0]+x)//2, (host_center[1]+y)//2,(host_center[2]+x1)//2,(host_center[3]+y1)//2))





def wrong_answer(x, y):
    aux_list[x]['money'], aux_list[y]['money'] = aux_list[x]['money'] + \
                                                                      aux_list[y]['money'], 0
    if (aux_list[x]['money'] % 1000) in (998, 999, 1, 2):
        aux_list[x]['money'] = round(aux_list[x]['money'], -3)
    update_money()
    playingrr_1234(round_number) #количество пустых ячеек совпадает с номером раунда playingrr_1234(round_number)
    host_move(who_answers_q)
    #root.mex_num = 0


    #for j in range(5):
        #print(playermoney[j]['text'])
    empezar.place(x=450, y=2)
    terminar.place(x=450, y=30)

def choose(x):
    if x!=0:
        #tim3.cancel()
        root.after_cancel(start_timerok3)
        for j in range(5):
            varianty[j]['state'] = 'disabled'
        intrigue = Timer(1.6, intrigue_if_correct, [x])
        intrigue.start()
        #print('otvet dan')
        log.write('Ответ игрока: '+ base_for_round[num_q_active]['v'][x - 1]+'\n')
    else:
        #print('otvet ne dan')
        intrigue_if_correct(x)


def intrigue_if_correct(n):
    global game_stage
    log.write("Правильный ответ: " + base_for_round[num_q_active]['v'][base_for_round[num_q_active]['c'] - 1]+'\n')
    if (n == base_for_round[num_q_active]['c']):
        pole_qu["bg"]="#00ff2f"
        #mb.showinfo("Ответ правильный!", aux_list[who_answers_q]['name']+', вы получаете '+str(for_correct[round_number-1]))
        root.title("Ответ правильный! "+aux_list[who_answers_q]['name'] + ', вы получаете ' + str(for_correct[round_number - 1]))
        canvas.itemconfig(hatches[who_asks_q+1], fill = "#00ffff")
        reward(round_number-1)
        update_money()
        # for j in range(round_number+1):
        #     varianty[j].place_forget()
        base_for_round.pop(num_q_active)
        if (len(base_for_round))>0:
            root.after(2000, rodyti_klausima)
        else:
            mb.showinfo("Раунд окончен", "Это был последний вопрос раунда")
            game_stage = stadija.noone_dropped
            rr_noonedropped()


    else:
        pole_qu['bg'] = "#ff0000"
        canvas.itemconfig(hatches[who_answers_q+1], fill = "#ff0000")
        if (n == 0):
            root.title("Время вышло! "+"Правильный ответ - " + base_for_round[num_q_active]['v'][base_for_round[num_q_active]['c'] - 1])
            #mb.showinfo("Время вышло!",
                        #"Правильный ответ - " + base_for_round[num_q_active]['v'][base_for_round[num_q_active]['c']-1])
        else:
            root.title("Вы ошиблись! "+"Правильный ответ - " + base_for_round[num_q_active]['v'][base_for_round[num_q_active]['c'] - 1])
            #mb.showinfo("Вы ошиблись!",
                        #"Правильный ответ - " + base_for_round[num_q_active]['v'][
                            #base_for_round[num_q_active]['c'] - 1])
        game_stage = stadija.after_wrong
        af_wr = Timer(2, wrong_answer, [who_asks_q, who_answers_q])
        af_wr.start()
        #root.after(2000, wrong_answer(who_asks_q, who_answers_q))



def timer_cont():
    global time_left, timer_started, start_timerok3
    time_left = time_left - 1
    #print(str(time_left))
    paliktas_laikas["text"] = str(time_left)
    #print('time_left = '+str(time_left))
    if (time_left == 0):
        for j in range(5):
            varianty[j]['state'] = 'disabled'
        log.write("Игрок не даёт ответа. "+'\n')
        choose(0)
    else:
        #root.tim3 = Timer(1, timer_cont)
        #tim3.start()
        for i in range(round_number + 1):
            varianty[i]['state'] = 'normal'
        start_timerok3 = root.after(1000, timer_cont)


def start_timer(jpg):
    global timer_started, time_left, start_timerok, start_timerok2
    #root.after_cancel(start_timerok)
    if (jpg<=4):
        # for i in range(round_number + 1):
        #     varianty[i]['state'] = 'normal'
        #paliktas_laikas["text"] = str(time_left)
        time_left += 1
        #print(time_left)
        if (timer_started is False):
            timer_started = True
            #ip = Timer(1, timer_cont)
            #ip.start()
            root.ifconfig = root.after(1000, timer_cont) #start_timerok2
        #print('timer_started is '+str(timer_started))

        # else:
        #     time_left -=1
        #     paliktas_laikas["text"] = str(time_left)
        #     if (time_left == 0):
        #         choose(0)
        #     else:
        #         start_timerok = root.after(1000, start_timer(jpg))






def show_variants(x):
    global place_answers, timer_started, start_timerok
    #xyz = len(pole_qu['text'])
    for j in range(x+1):
        varianty[j]['text'] = base_for_round[num_q_active]['v'][j]
        varianty[j].place(x=place_answers[round_number-1][j][0], y=place_answers[round_number-1][j][1])
        varianty[j]['state'] = 'disabled'
        log.write(str(j+1)+'. '+base_for_round[num_q_active]['v'][j] + '\n')
        #xyz += len(varianty[j]["text"])
    timer_started = False
    _123chooseemul = Timer(4, start_timer, [x])
    _123chooseemul.start()
    #root.after(4000, start_timer(x)) #start_timerok
    #print('timer_started is ' + str(timer_started))







def challengee(u):
    global who_answers_q, round_number, time_left
    for j in range(KOLVO_IGROKOV):
        pasirinkti_atsakysianti[j].place_forget()
    time_left = TIMER
    #print('time_left_restore = '+str(time_left))
    paliktas_laikas["text"] = str(time_left)
    #paliktas_laikas.update_idletasks()
    who_answers_q = u
    canvas.itemconfig(hatches[u+1], fill = "#ffffff")
    paliktas_laikas.place(x=690, y= 520)
    #mb.showinfo(aux_list[u]['name'], 'Вы будете отвечать на этот вопрос')
    root.title(aux_list[u]['name']+ ',вы будете отвечать на этот вопрос')
    log.write('Отвечает: ' + aux_list[u]['name'] + '\n')
    show_variants(round_number)
    pass #дописать


def reward(ro):
    global pereschet, i, pre_game, who_asks_q, who_answers_q, game_stage
    if (ro == 0) :
        if pereschet == stadija_scheta.before and (game_stage==stadija.pre_round):
            pereschet = stadija_scheta.during
        if (pre_game is True):
            for we in range(KOLVO_IGROKOV):
                aux_list[we]['money'] +=for_correct[ro]
                playermoney[we]['text'] = str(aux_list[we]['money'])
            game_stage=stadija.during_round
            pereschet = stadija_scheta.posle
            pre_game = False
        else:
            #print('верно')
            aux_list[who_answers_q]['money']+=for_correct[ro]
            playermoney[who_answers_q]['text'] = str(aux_list[who_answers_q]['money'])
            who_asks_q = who_answers_q
    elif (ro in (1,2,3)):
        #print('верно')
        aux_list[who_answers_q]['money']+=for_correct[ro]
        playermoney[who_answers_q]['text'] = str(aux_list[who_answers_q]['money'])
        who_asks_q = who_answers_q


def rodyti_klausima():
    global round_number, num_q_active, pereschet, who_asks_q, who_answers_q, base_for_round
    #print('1')
    pole_qu.place(x=10, y=510)
    pole_qu['bg'] = '#8f8f8f'
    for j in range(5):
        varianty[j].place_forget()
    paliktas_laikas.place_forget()
    num_q_active = randint(0, len(base_for_round)-1)
    pole_qu['text'] = base_for_round[num_q_active]['q']
    if (round_number in (1,2,3,4)):
        log.write('Вопрос '+str(questions_in_round[round_number-1]-len(base_for_round)+1)+'\n'+base_for_round[num_q_active]['q']+'\n')
    if (round_number == 1) and len(base_for_round) == questions_in_round[0]: #т.е. если игра не началась
        pereschet = stadija_scheta.before
        reward(0)
    if (round_number in (1,2,3)):
        for j in range(KOLVO_IGROKOV):
            if (j!=who_asks_q) and (aux_list[j]["in_game"]):
                pasirinkti_atsakysianti[j].place(x=219, y=10 + j * 71)
        #print(aux_list[who_asks_q]['name']+' asks the next question')
        log.write('Задаёт: '+aux_list[who_asks_q]['name']+'\n')
    elif (round_number == 4):
        for j in range(KOLVO_IGROKOV):
            if (j != who_asks_q) and (aux_list[j]["in_game"]):
                who_answers_q = j
                break
        _4chooseemul = Timer(5, challengee, [who_answers_q])
        _4chooseemul.start()
    elif (round_number == 5):
        test.place(x=130, y=560)




def mex_defwhoasks():
    global mex_num, count, canvas, who_asks_q, round_number
    root.after_cancel(root.spin_defwhoasks)
    mex_num+=1
    for j in range(6):
        if (mex_num % 6 == j):
            canvas.itemconfig(hatches[j], fill="#ffffff")
        else:
            canvas.itemconfig(hatches[j], fill="#cfcfcf")
    if (mex_num <count):
        root.spin_defwhoasks = root.after(250, mex_defwhoasks)
    else:
        canvas.itemconfig(hatches[0], fill="#00ffff")
        for j in range (5):
            if (who_asks_q != j):
                canvas.itemconfig(hatches[j+1], fill="#00ffff")
        mb.showinfo(aux_list[who_asks_q]['name'], 'Первый вопрос раунда задавать будете вы.')
        for j in range (questions_in_round[round_number-1]):
            while True:
                q = randint(0, len(base)-1)
                if base[q]['round'] == round_number:
                    base_for_round.append(base[q])
                    base.pop(q)
                    break
            #print(base_for_round[j])
        root.showq = root.after(1000, rodyti_klausima())


def mex_begin_end_round():
    pass


def endround_1234():
    global game_stage, round_number, base_for_round, winner
    for jj in range(6):
        canvas.itemconfig(hatches[jj], fill='#ffffff')
    for jj in range(5):
        varianty[jj].place_forget()
    round_number +=1
    if (round_number<=4):
        game_stage = stadija.pre_round
    else:
        for jj in range(KOLVO_IGROKOV):
            if (aux_list[jj]['in_game']):
                winner = jj
                break
        canvas.coords(igroki_na_liukah[winner], host_center[0] + 25, host_center[1], host_center[2] + 25,
                      host_center[3])
    base_for_round = []
    pole_qu.place_forget()
    rr_st_1234()

def fate(w):
    global dropzones_1234, who_asks_q, who_answers_q, game_stage
    if (game_stage!=stadija.noone_dropped):
        if (w in dropzones_1234):
            canvas.delete(igroki_na_liukah[w])
            canvas.itemconfig(hatches[w+1], fill='#000000')
            playermoney[w].place_forget()
            playerlabels[w].place_forget()
            aux_list[w]['in_game'] = False
            log.write(aux_list[who_answers_q]['name'] + ' покидает игру.' + '\n')
            #mb.showerror('Проиграл')
            close_hatch = Timer(3.5, endround_1234)
            close_hatch.start()

        else:
            canvas.itemconfig(hatches[0], fill='#00ffff')
            for k in range(5): #rectify
                if (k == who_answers_q):
                    canvas.itemconfig(hatches[k+1], fill='#ffffff')
                else:
                    canvas.itemconfig(hatches[k+1], fill='#00ffff')
            log.write(aux_list[who_answers_q]['name']+ ' остаётся в игре.'+'\n')
            who_asks_q = who_answers_q
            mb.showinfo(aux_list[who_asks_q]['name'], 'Остался в игре')
            base_for_round.pop(num_q_active)
            if (len(base_for_round))>0:
                root.after(2000, rodyti_klausima)
            else:
                mb.showinfo("Раунд окончен", "Это был последний вопрос раунда")
                game_stage = stadija.noone_dropped
                rr_noonedropped()
        canvas.coords(host, host_center[0], host_center[1], host_center[2], host_center[3])
    else:
        canvas.delete(igroki_na_liukah[w])
        canvas.itemconfig(hatches[w + 1], fill='#000000')
        playermoney[w].place_forget()
        playerlabels[w].place_forget()
        aux_list[w]['in_game'] = False
        log.write('Из игры выбывает ' +aux_list[w]['name'] +'.\n')
        if (aux_list[w]['money']>0):
            mb.showinfo('','Деньги игрока '+aux_list[w]['name']+' разделяются поровну между всеми оставшимися игроками')
            foo = 0
            for tt in range(KOLVO_IGROKOV):
                if (aux_list[tt]['in_game']):
                    foo +=1
            for tt in range(KOLVO_IGROKOV):
                if (aux_list[tt]['in_game']):
                    aux_list[tt]['money'] += aux_list[w]['money']//foo
                    # x, y, x1, y1 = canvas.coords(hatches[tt + 1])
                    # canvas.coords(igroki_na_liukah[tt], (x + x1) // 2 - 7, (y + y1) // 2 - 7, (x + x1) // 2 + 8,
                    #               (y + y1) // 2 + 8)
        for tt in range(KOLVO_IGROKOV):
            if (aux_list[tt]['in_game']):
                x, y, x1, y1 = canvas.coords(hatches[tt + 1])
                canvas.coords(igroki_na_liukah[tt], (x + x1) // 2 - 7, (y + y1) // 2 - 7, (x + x1) // 2 + 8,
                              (y + y1) // 2 + 8)
        for tt in range(KOLVO_IGROKOV):
            if (aux_list[tt]['money'] % 1000) in (998, 999, 1, 2):
                aux_list[tt]['money'] = round(aux_list[tt]['money'], -3)
        update_money()
        close_hatch = Timer(3.5, endround_1234)
        close_hatch.start()


def mex_bonus_round(variable):
    global dropzones_1234
    dropzones_1234 = []
    for i in range(final_hatchesopen[variable]):
        while True:
            t = randint(0, 5)
            if not (t in dropzones_1234):
                dropzones_1234.append(t)
                break
    #print(dropzones_1234)


def mex_start():
    global mex_num, stage_final, round_number, dropzones_1234
    empezar['state'] = 'disabled'
    terminar['state'] = 'normal'
    root.mex_spin = root.after(250, mex_works)
    mex_num = 0
    if (round_number > 4):
        mex_bonus_round(stage_final)



def mex_stop():
    global mex_num, count, canvas, who_asks_q, who_answers_q, will_fall, round_number, winner_islookingfor_hatch
    root.after_cancel(root.mex_spin)
    empezar.place_forget()
    terminar.place_forget()
    empezar['state'], terminar['state'] = 'normal', 'disabled'
    if round_number in (1,2,3,4):
        for j in range (6):
            canvas.itemconfig(hatches[j], fill = "#ffffff")
        if (game_stage == stadija.pre_round) or (game_stage == stadija.during_round):
            count = who_asks_q + 1 + (6 * randint(1, 4)) #1,4
            mex_num = 0
            root.spin_defwhoasks = root.after(250, mex_defwhoasks)
        elif (game_stage == stadija.after_wrong):
            los = Timer(randint(5, 12), fate, [who_answers_q]) #5,12
            los.start()
        elif (game_stage == stadija.noone_dropped):
            los = Timer(randint(5, 12), fate, [will_fall]) #5, 12
            los.start()
    else:
        for j in range (6):
            canvas.itemconfig(hatches[j], fill = "#cfcfcf")
        winner_islookingfor_hatch = True
        count = 0


def uk():
    global occupied_by_winner, occupied_by_host
    while True:
        f = randint(0, 5)
        if (f != occupied_by_winner):
            break
    occupied_by_host = f
    x, y, x1, y1 = canvas.coords(hatches[occupied_by_host])
    canvas.coords(host, (x + x1) // 2 - 7, (y + y1) // 2 - 7, (x + x1) // 2 + 8,
                  (y + y1) // 2 + 8)
    canvas.itemconfig(hatches[occupied_by_host], fill="#ffffff")
    host_na_liuk_2 = Timer(3, rodyti_klausima)
    host_na_liuk_2.start()




def place(event, t):
    global winner_islookingfor_hatch, occupied_by_winner, occupied_by_host
    if (round_number>4):
        if (winner_islookingfor_hatch):
            winner_islookingfor_hatch = False
            for a in range(6):
                if a !=t:
                    canvas.itemconfig(hatches[a], fill = "#cfcfcf")
                else:
                    canvas.itemconfig(hatches[a], fill="#ffffff")
            x,y,x1,y1=canvas.coords(hatches[t])
            canvas.coords(igroki_na_liukah[winner], (x+x1)//2-7, (y+y1)//2-7, (x+x1)//2+8, (y+y1)//2+8) #заменить player на игрока
            occupied_by_winner = t
            if (stage_final<3): #если это не вопрос на миллион
                rodyti_klausima()
            else:
                host_na_liuk = Timer(2, uk)
                host_na_liuk.start()
                # while True:
                #     f = randint(0, 5)
                #     if (f != occupied_by_winner):
                #         break
                # occupied_by_host = f
                # x, y, x1, y1 = canvas.coords(hatches[occupied_by_host])
                # canvas.coords(host, (x + x1) // 2 - 7, (y + y1) // 2 - 7, (x + x1) // 2 + 8,
                #               (y + y1) // 2 + 8)
                #root.after(3500, rodyti_klausima())




for d in range(6):
    a = canvas.create_oval(120*PLACES_X[d], 120*(PLACES_Y[d]-1), 120*PLACES_X[d]+90, 120*(PLACES_Y[d]-1)+90, width=2, fill="#cfcfcf")
    hatches.append(a)
    canvas.tag_bind(hatches[d], "<Button-1>", lambda event, h=d: place(event, h))


kolo = canvas.create_oval(80, 30, 480, 430, width=2, fill="#cfcfcf" )
canvas.tag_lower(kolo)
host = canvas.create_oval(host_center[0], host_center[1], host_center[2], host_center[3], width=2, fill = "#1f1f1f")
#a = canvas.create_oval(100, 25, 150, 75, width=1, fill='#00ffff')
#b = canvas.create_oval()
#p = canvas.create_polygon(100, 10, 20, 90, 180, 90, fill="#7f7f7f")
#canvas.tag_lower(p)
count = 0
zaidejai = ttk.LabelFrame(root, text = "Игроки", width = 305, height=370)
zaidejai.place(x=660, y = 19)
# spalvos = ["#ff0000", "#007fff", "#ffffff"]

def yt(ae, bbq):
    global canvas, count, stage_final, occupied_by_winner, occupied_by_host
    #canvas.move(a, 20, 10)
    #canvas.itemconfig(a, fill="#ff0000")
    count += 1
    orly = ae
    yarly = bbq
    canvas.itemconfig(hatches[ae], fill=spalvos [count % len(spalvos)])
    if (stage_final ==3):
        canvas.itemconfig(hatches[occupied_by_host], fill=spalvos[count % len(spalvos)])
    if (count>=bbq):
        ar_kris_finale(stage_final)
    else:
        error_bonus = Timer(0.25, yt, [orly, yarly])
        error_bonus.start()
        #root.r = root.after(250, yt(ae, bbq))



def ar_kris_finale(h):
    for i in range(6):
        if (i in dropzones_1234):
            canvas.itemconfig(hatches[i], fill='#000000')
            if (h == 3) and (occupied_by_host == i):
                canvas.delete(host)
            if (occupied_by_winner == i):
                canvas.delete(igroki_na_liukah[winner])
                playermoney[winner]['text'] = str(aux_list[winner]['money'] + final_tree[0])
                if (h == 3) and (occupied_by_host == i):
                    log.write('И ведущий, и финалист исчезли с площадки. \n Выигрыш: '+playermoney[winner]['text'])
                else:
                    log.write(aux_list[winner]['name']+' покидает игру. \n Выигрыш: ' + playermoney[winner]['text'])
        else:
            canvas.itemconfig(hatches[i], fill = '#ffffff')
    if not(occupied_by_winner in dropzones_1234):
        if (h==3):
            playermoney[winner]['text'] = str(aux_list[winner]['money'] + final_tree[h])
            log.write('Ведущий исчезает с площадки, а '+aux_list[winner]['name'] + ' остаётся в игре. \n'+'Выигрыш: '+playermoney[winner]['text'])
            mb.showinfo('Поздравляем!', aux_list[winner]['name']+' выигрывает '+playermoney[winner]['text'])
            log.close()
            root.destroy()
        else:
            mb.showinfo('Вам повезло!', aux_list[winner]['name']+' остаётся в игре')
            log.write(aux_list[winner]['name'] + ' остаётся в игре. \n')
            for i in range(6):
                canvas.itemconfig(hatches[i], fill='#cfcfcf')
            canvas.coords(igroki_na_liukah[winner], host_center[0]+25, host_center[1], host_center[2]+25, host_center[3])
            #print('Вопросов финала осталось: ' + str(len(base_for_round)))
            log.write('Вопрос ' + str(vopros_finala - len(base_for_round) + 1) + ' (' + str(
                final_tree[stage_final]) + ')' + '\n')
            empezar.place(x=450, y=2)
            terminar.place(x=450, y=30)


#
# root.r = root.after(300, yt)
#
# t = randint(9, 27)
# print(t)
#b=tk.Button (root, width=32, height=1, command=yt, text="Переместить")
#b.place(x=50, y=550)
def mex_begin_st_round():
    global who_asks_q, game_stage
    if (game_stage == stadija.pre_round):
        while True:
            who_asks_q = randint(0, KOLVO_IGROKOV-1)
            if (aux_list[who_asks_q]['in_game']):
                break
        #print(who_asks_q)


def final_pre_question():
    global base_for_round, stage_final, final_read, winner, igroki_na_liukah, vopros_finala
    for i in range(6):
        canvas.itemconfig(hatches[i], fill="#cfcfcf")
    empezar.place(x=450, y=2)
    terminar.place(x=450, y=30)
    if (final == answer_in_final.no_final) and (final_read is False):
        base_for_round = []
        for j in range(len(base)):
            if (base[j]['round'] == 5):
                base_for_round.append(base[j])
        vopros_finala = len(base_for_round)
        log.write('Финал'+'\n')
        log.write('Финалист игры - '+aux_list[winner]['name']+', банк игры - '+str(aux_list[winner]['money'])+'\n')
        final_read = True
    canvas.coords(igroki_na_liukah[winner], host_center[0] + 25, host_center[1], host_center[2] + 25,
                  host_center[3])
    #print('Вопросов финала осталось: '+str(len(base_for_round)))
    log.write('Вопрос '+str(vopros_finala-len(base_for_round)+1)+' ('+str(final_tree[stage_final])+')'+'\n')





def rr_st_1234():
    global who_asks_q, winner, stage_final, final
    z = []
    if (round_number in (1,2,3,4)):
        for y in range(len(aux_list)):
            z.append(aux_list[y]["money"])
        x = max(aux_list, key=lambda f: f['money'])
        log.write("Раунд "+str(round_number)+'\n'+'Счёт игроков: '+'\n')
        if (round_number == 1):
            for oi in range(KOLVO_IGROKOV):
                if (aux_list[oi]['in_game']):
                    log.write(aux_list[oi]['name']+': 1000'+'\n')
        else:
            for oi in range(KOLVO_IGROKOV):
                if (aux_list[oi]['in_game']):
                    log.write(aux_list[oi]['name']+': '+str(aux_list[oi]['money'])+'\n')
        #print(z.count(x['money']))
        if z.count(x['money'])>1: #если нет явного лидера
            empezar.place(x=450, y=2)
            terminar.place(x=450, y=30)
            mex_begin_st_round()
        else:
            canvas.itemconfig(hatches[0], fill="#00ffff")
            who_asks_q = z.index(x['money'])
            for i in range(KOLVO_IGROKOV):
                if (i == z.index(x['money'])):
                    canvas.itemconfig(hatches[i+1], fill="#ffffff")
                else:
                    canvas.itemconfig(hatches[i+1], fill="#00ffff")
            for j in range (questions_in_round[round_number-1]):
                while True:
                    q = randint(0, len(base)-1)
                    if base[q]['round'] == round_number:
                        base_for_round.append(base[q])
                        base.pop(q)
                        break
            rodyti_klausima()
            pass # написать код, при котором игрок сразу задавал бы вопрос
    else:
        if (final == answer_in_final.no_final):
            stage_final = 1
        elif (final == answer_in_final.right) and (stage_final<3):
            stage_final += 1
        final_pre_question()

def check(*args):
    global num_q_active, stage_final, winner
    odgovor = guess.get()
    if (odgovor!=''):
        log.write(base_for_round[num_q_active]['q'] + '\n')
        log.write('Ответ игрока: ' + odgovor+ '\n')
        otvety = []
        for i in range(len(base_for_round[num_q_active]["c"])):
            otvety.append(base_for_round[num_q_active]["c"][i])
            otvety[i] = otvety[i].replace(' ', '')
            otvety[i]=otvety[i].lower()
        odgovor = odgovor.lower()
        odgovor = odgovor.replace(' ', '')
        test.place_forget()
        if (odgovor in otvety):
            j = otvety.index(odgovor)
            pole_qu['bg'] = '#00ff2f'
            if (j==0):
                mb.showinfo('Верно!', 'Вы дали правильный ответ!')
            #     log.write("Правильный ответ: "+base_for_round[num_q_active]["c"][j]+'\n')
            else:
                mb.showinfo('Верно!', "Правильный ответ: "+base_for_round[num_q_active]["c"][0])
            #     log.write("Правильный ответ: "+base_for_round[num_q_active]["c"][j]+" ("+base_for_round[num_q_active]["c"][0]+")"+'\n')
            log.write('Ответ верен.'+'\n')
            playermoney[winner]['text'] = str(aux_list[winner]['money'] + final_tree[stage_final])
            base_for_round.pop(num_q_active)
            if (stage_final in (1,2)):
                if mb.askyesno('Решение', 'Играем дальше?'):
                    stage_final += 1
                    final_pre_question()
                else:
                    mb.showinfo(aux_list[winner]['name'], 'Вы выиграли '+ playermoney[winner]['text']+'. Спасибо за участие в игре!')
                    log.write('Игрок забирает деньги. '+'\n.'+'Выигрыш: '+playermoney[winner]['text'])
                    log.close()
                    root.destroy()
        else:
            pole_qu['bg'] = '#ff0000'
            test_random = randint(3, 10)*3
            mb.showerror('Вы ошиблись!', "Правильный ответ: " + base_for_round[num_q_active]["c"][0])
            log.write('Правильный ответ: ' + base_for_round[num_q_active]["c"][0] + '\n')
            base_for_round.pop(num_q_active)
            yt(occupied_by_winner, test_random)
    guess.set("")


            # log.write("Ответ игрока: " + guess.get()+'\n')
            # log.write("Правильный ответ: "+baza_zamen_round[s]["A"][0]+'\n')




def rr_noonedropped():
    global will_fall, saved
    pole_qu.place_forget()
    for us in range(5):
        varianty[us].place_forget()
    z = []
    for y in range(len(aux_list)):
        z.append(aux_list[y]["money"])
    x = max(aux_list, key=lambda f: f['money'])
    empezar.place(x=450, y=2)
    terminar.place(x=450, y=30)
    log.write('Вопросы раунда закончились.'+'\n')
    if z.count(x['money'])>1: #если нет явного лидера
        #print("Нет явного лидера, значит любой может выбыть.")
        saved = []
    elif (round_number == 4):
        #print("В четвёртом раунде никто не считается спасённым.")
        saved = []
    else:
        canvas.coords(igroki_na_liukah[z.index(x['money'])], host_center[0]+25, host_center[1], host_center[2]+25, host_center[3])
        saved = [z.index(x['money'])]
        log.write(aux_list[saved[0]]['name']+" в безопасности."+'\n')
    while True:
        will_fall = randint(0, KOLVO_IGROKOV-1)
        if (will_fall not in saved) and (aux_list[will_fall]['in_game']):
            break
    #who_drops_in_endround(saved)
    #print('Игру покинет '+aux_list[will_fall]['name'])





def kwalif():
    global aux_list
    for a in range(len(start_names)):
        if start_names[a].get()=="":
            tk.messagebox.showwarning("Имена", "По меньшей мере у одного из игроков пустое имя. Исправьте")
            break
    else:
        rich.place_forget()
        log.write('\n'+'Игроки: '+'\n')
        #log.write('Игроки: '+'\n')
        aux_list = []
        for b in range(KOLVO_IGROKOV):
            player_start[b].place_forget()
        for b in range (KOLVO_IGROKOV):
            aux_dict = {}
            aux_dict['name'] = start_names[b].get()
            aux_dict['money'] = 0
            aux_dict['in_game'] = True
            x,y,x1,y1=canvas.coords(hatches[b+1])
            #canvas.coords(player, (x+x1)//2-7, (y+y1)//2-7, (x+x1)//2+8, (y+y1)//2+8) #заменить player на игрока
            mb.showinfo(aux_dict['name'], "Выберите цвет игрока")
            (rgb, hx) = colorchooser.askcolor()
            x, y, x1, y1 = canvas.coords(hatches[b+1])
            igrok_m = canvas.create_oval(10, 10+50*b, 24, 10+50*b+14, width=2, fill = "#7f7f7f")
            igroki_na_liukah.append(igrok_m)
            canvas.coords(igroki_na_liukah[b], (x + x1) // 2 - 7, (y + y1) // 2 - 7, (x + x1) // 2 + 8,
                          (y + y1) // 2 + 8)  # заменить player на игрока
            canvas.itemconfig(igroki_na_liukah[b], fill=hx)
            aux_list.append(aux_dict)
        for b in range(KOLVO_IGROKOV):
            q = tk.Label(zaidejai, width=15, height=3)
            w = tk.Label(zaidejai, width=8, height=1, text=str(aux_list[b]['money']))
            c = canvas.itemconfig(igroki_na_liukah[b])
            playerlabels.append(q)
            playermoney.append(w)
            playerlabels[b]["bg"] = c["fill"][4]
            playerlabels[b]["fg"] = "#000000"
            playerlabels[b]["text"] = aux_list[b]['name']
            playerlabels[b]["justify"] = tk.LEFT
            playerlabels[b].place(x=5, y=5 + b * 71)
            playermoney[b].place(x=135, y=10 + b * 71)
            log.write(str(b+1)+'. '+aux_list[b]['name']+'\n')
        rr_st_1234()

            #log.write(aux_list[b]['name'] + ': ' + str(aux_list[b]['sgor']) + ' + ' + str(aux_list[b]['nesgor']) + ' = ' + str(aux_list[b]['sgor'] + aux_list[b]['nesgor'])+'\n')

        #tk.messagebox.showinfo("Готово", "Мы начинаем игру")
        #root.qu_sh = root.after(1000, lambda b=q_number: show(b))



for x in range(KOLVO_IGROKOV):
    dummy = tk.StringVar()
    dummy.set("Игрок "+str(x+1))
    start_names.append(dummy)

for pl_field in range (KOLVO_IGROKOV):
    nombre = ttk.Entry(root, textvariable = start_names[pl_field])
    player_start.append(nombre)
    player_start[pl_field].place(width=140, x = 50, y=500+pl_field*(40))

rich = tk.Button(root, text="Начать игру", command=kwalif, width = 14, height = 10)
rich.place(x = 400, y=500)


empezar = tk.Button(root, text="Старт механизма", width=20, height = 1, command = mex_start, state="normal")
terminar = tk.Button(root, text="Остановить механизм", width=20, height=1, command = mex_stop, state="disabled")


base = []
testa = codecs.open("questions.txt", 'r', "utf_8_sig")
testb = testa.readlines()
testc = len(testb)
testd = 0
while True:
    testf = {}
    testf["round"] = int(testb[testd].rstrip('\n'))
    testd+=1
    testf["q"] = testb[testd].rstrip('\n')
    testf["v"] = []
    if (testf["round"]<=4):
        for testg in range(testf["round"]+1):
            testd+=1
            testf["v"].append(testb[testd].rstrip('\n'))
        testd+=1
        testf["c"] = int(testb[testd].rstrip('\n'))
    else:
        testf["v"] = None
        testd+=1
        testf["c"] = list(map(str, testb[testd].split(", ")))
        testf["c"][-1]=testf["c"][-1].rstrip("\n")
    base.append(testf)
    testd+=1
    if (testd >= testc-1 ):
        break

testa.close()
del testb, testc, testd, testf
paliktas_laikas = tk.Label(width = 3, height = 1, fg="#ffffff", bg="#000000")
# for counter in range (len(base)):
#     print(counter, base[counter]['q'])
pasirinkti_atsakysianti=[]
varianty = []
pole_qu = tk.Label(root, width = 72, height=16, justify = tk.CENTER, wraplength=390, text="", bg="#8f8f8f", fg = "#ffffff", anchor = "n")
for pp in range(KOLVO_IGROKOV):
    kto_otv = tk.Button(zaidejai, text="Выбор", width = 6, height=1, command=lambda rtt=pp: challengee(rtt))
    pasirinkti_atsakysianti.append(kto_otv)
for pp in range (5):
    v = tk.Button(root, width=14, height = 1, command = lambda kj=pp+1: choose(kj))
    varianty.append(v)

#tim3 = Timer(1, timer_cont)
guess = tk.StringVar()
test = ttk.Entry(root, width=29, textvariable=guess)
test.bind("<Return>", check)
root.protocol('WM_DELETE_WINDOW', doSomething)
root.mainloop()
