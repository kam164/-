import socket
import time
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import pygame

def find(vector:str):
    first=vector.find("<")
    second=vector.find(">")
    if first<second and first>=0:
        result=vector[first+1:second]
        result=result.split(",")
        result=list(map(float,result))
        return result
    return ""

pygame.init()
WIDTH_ROOM, HEIGHT_ROOM = 4000, 4000
WIDTH_SERVER, HEIGHT_SERVER = 300,300
FPS=100
screen = pygame.display.set_mode((WIDTH_SERVER, HEIGHT_SERVER))
pygame.display.set_caption('Сервер')
clock = pygame.time.Clock()

engine=create_engine("postgresql+psycopg2://postgres:123456@localhost/bakterii")
Session=sessionmaker(bind=engine)
Base=declarative_base()
s=Session()
class Players(Base):
    __tablename__="gamers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    address = Column(String)
    x=Column(Integer, default=500)
    y=Column(Integer,default=500)
    size=Column(Integer,default=50)
    errors=Column(Integer,default=1)
    abs_speed = Column(Integer,default=2)
    speed_x = Column(Integer,default=2)
    speed_y = Column(Integer,default=2)

    def __init__(self,name,address):
        self.name=name
        self.address=address
Base.metadata.create_all(engine)
#Base.metadata.drop_all(engine)
class LocalPlayer:
    def __init__(self,id, name,sock, addr):
        self.id=id
        self.db: Players=s.get(Players, self.id)
        self.sock=sock
        self.name = name
        self.addr=addr
        self.x=500
        self.y=500
        self.size=50
        self.errors=0
        self.abs_speed=1
        self.speed_x=0
        self.speed_y=0
    def update(self):
        self.x+=self.speed_x
        self.y+=self.speed_y
    def chnge_speed(self, vector):
        vector=find(vector)
        if vector[0]==0 and vector[1]==0:
            self.speed_x=self.speed_y=0
        else:
            vector=vector[0]*self.abs_speed,vector[1]*self.abs_speed
            self.speed_x=vector[0]
            self.speed_y=vector[1]

main_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(("localhost",10000))
main_socket.setblocking(False)
main_socket.listen(5)
print("Сокет создался")
players={}
server_works=True
while server_works:
    clock.tick(FPS)
    try:
        new_socket, addr=main_socket.accept()
        new_socket.setblocking(False)
        print("Подключился", addr)
        player=Players("Алла",addr)
        s.merge(player)
        s.commit()
        addr=f'({addr[0]},{addr[1]})'
        data=s.query(Players).filter(Players.address==addr)
        for user in data:
            player=LocalPlayer(user.id,user.name,new_socket, addr)
            players[user.id]=player
    except BlockingIOError:
        pass
    for id in list(players):
        try:
            data=players[id].sock.recv(1024).decode()
            #print("Получил", data)
            print(data)
            players[id].chnge_speed(data)
        except:
            pass
    for id in list(players):
        try:
            players[id].sock.send("Игра".encode())
        except:
            #players.remove(sock)
            players[id].sock.close()
            del players[id]
            s.query(Players).filter(Players.id==id).delete()
            s.commit()
            print("Сокет закрыт")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server_works=False
    screen.fill('black')
    for id in players:
        player=players[id]
        x=player.x*WIDTH_SERVER//WIDTH_ROOM
        y=player.y*HEIGHT_SERVER//HEIGHT_ROOM
        size=player.size*WIDTH_SERVER//WIDTH_ROOM
        pygame.draw.circle(screen, "yellow2",(x,y),size)
    for id in list(players):
        player=players[id]
        players[id].update()
    pygame.display.update()



pygame.quit()
main_socket.close()
s.query(Players).delete()
s.commit()
