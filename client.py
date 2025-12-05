import socket

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox

import pygame
import math
pygame.init()

def scrol(event):
    global color
    color=combo.get()
    style.configure("TCombobox", fieldbackground=color, background="white")

def login():
    global name
    name=row.get()
    if name and color:
        root.quit()
        root.destroy()
    else:
        tk.messagebox.showerror("Ошибка", "Ты не выбрал цвет или не ввёл имя!")

def find(vector: str):
    first = vector.find("<")
    second = vector.find(">")
    if first < second and first >= 0:
        result = vector[first + 1:second]
        return result
    return ""
def draw_bacteries(data:list[str]):
    for bact in data:
        data=bact.split(" ")
        x=CC[0]+int(data[0])
        y=CC[1]+int(data[1])
        size=int(data[2])
        color=data[3]
        pygame.draw.circle(screen,color,(x,y),size)

name=""
color=""
root=tk.Tk()
root.geometry("300x200")
root.title("Логин")
style=ttk.Style()
style.theme_use("default")

name_label=tk.Label(root, text="Введи свой никнейм")
name_label.pack()
row=tk.Entry(root, width=30,  justify="center")
row.pack()
color_label=tk.Label(root, text="Выбери цвет")
color_label.pack()
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
        'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
        'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
        'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue',
        'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']
combo = ttk.Combobox(root, values=colors, textvariable=color)
combo.bind("<<ComboboxSelected>>", scrol)
combo.pack()
name_btn=tk.Button(root, text="Войти в игру", command=login)
name_btn.pack()
root.mainloop()

WIDTH = 800
HEIGHT = 600
CC=(WIDTH//2,HEIGHT//2)
radius=50
old=(0,0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Бактерии")


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(("localhost", 10000))
sock.send(("color:<"+name+","+ color + ">").encode())
run=True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
        if pygame.mouse.get_focused():
            pos = pygame.mouse.get_pos()
            vector=(pos[0]-CC[0],pos[1]-CC[1])
            lenv=math.sqrt(vector[0]**2+vector[1]**2)
            vector=vector[0]/lenv,vector[1]/lenv
            if lenv<=radius:
                vector=0,0
            if vector!=old:
                old=vector
                msg=f"<{vector[0]},{vector[1]}>"
                sock.send(msg.encode())

    data = sock.recv(1024).decode()
    print(data)
    data=find(data).split(",")
    screen.fill('gray')
    pygame.draw.circle(screen,color,CC,radius)
    if data!=[""]:
        draw_bacteries(data)
    font = pygame.font.Font(None, 200)
    text = font.render("cat", True, (255, 255, 255))
    screen.blit(text, (100,100))
    pygame.display.update()
pygame.quit()