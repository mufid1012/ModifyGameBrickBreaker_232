import tkinter as tk

class ObjekGame(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def posisi(self):
        return self.canvas.coords(self.item)

    def gerak(self, x, y):
        self.canvas.move(self.item, x, y)

    def hapus(self):
        self.canvas.delete(self.item)

class Bola(ObjekGame):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.arah = [1, -1]
        self.kecepatan = 5
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='black')
        super(Bola, self).__init__(canvas, item)

    def update(self):
        coords = self.posisi()
        lebar = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= lebar:
            self.arah[0] *= -1
        if coords[1] <= 0:
            self.arah[1] *= -1
        x = self.arah[0] * self.kecepatan
        y = self.arah[1] * self.kecepatan
        self.gerak(x, y)

    def tabrak(self, objek_game):
        coords = self.posisi()
        x = (coords[0] + coords[2]) * 0.5
        if len(objek_game) > 1:
            self.arah[1] *= -1
        elif len(objek_game) == 1:
            objek = objek_game[0]
            coords = objek.posisi()
            if x > coords[2]:
                self.arah[0] = 1
            elif x < coords[0]:
                self.arah[0] = -1
            else:
                self.arah[1] *= -1

        for objek in objek_game:
            if isinstance(objek, Blok):
                objek.kena()

class Paddle(ObjekGame):
    def __init__(self, canvas, x, y):
        self.lebar = 80
        self.tinggi = 10
        self.bola = None
        item = canvas.create_rectangle(x - self.lebar / 2,
                                       y - self.tinggi / 2,
                                       x + self.lebar / 2,
                                       y + self.tinggi / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)

    def set_bola(self, bola):
        self.bola = bola

    def gerak(self, offset):
        coords = self.posisi()
        lebar = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= lebar:
            super(Paddle, self).gerak(offset, 0)
            if self.bola is not None:
                self.bola.gerak(offset, 0)

class Blok(ObjekGame):
    WARNA = ['#FF0000', '#FFFF00', '#00FF00', '#0000FF', '#800080']

    def __init__(self, canvas, x, y, hits, warna):
        self.lebar = 60
        self.tinggi = 20
        self.hits = hits
        item = canvas.create_rectangle(x - self.lebar / 2,
                                       y - self.tinggi / 2,
                                       x + self.lebar / 2,
                                       y + self.tinggi / 2,
                                       fill=warna, tags='blok')
        super(Blok, self).__init__(canvas, item)

    def kena(self):
        self.hits -= 1
        if self.hits == 0:
            self.hapus()

class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.nyawa = 3
        self.lebar = 610
        self.tinggi = 400
        self.canvas = tk.Canvas(self, bg='#FFFFFF', width=self.lebar, height=self.tinggi)
        self.canvas.pack()
        self.pack()

        self.objek = {}
        self.bola = None
        self.paddle = Paddle(self.canvas, self.lebar/2, 360)
        self.objek[self.paddle.item] = self.paddle

        warna_blok = Blok.WARNA
        for baris in range(6):  # Baris penuh blok
            for kolom in range(10):  # Kolom penuh blok
                x = 35 + kolom * 61
                y = 35 + baris * 25
                warna = warna_blok[baris % len(warna_blok)]
                self.tambah_blok(x, y, 1, warna)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.gerak(-30))  # Sensitivitas tinggi
        self.canvas.bind('<Right>', lambda _: self.paddle.gerak(30))

    def setup_game(self):
        self.tambah_bola()
        self.update_nyawa()
        self.teks = self.tulis_teks(300, 200, 'Tekan Spasi untuk Memulai')
        self.canvas.bind('<space>', lambda _: self.mulai_game())

    def tambah_bola(self):
        if self.bola is not None:
            self.bola.hapus()
        coords_paddle = self.paddle.posisi()
        x = (coords_paddle[0] + coords_paddle[2]) * 0.5
        self.bola = Bola(self.canvas, x, 340)
        self.paddle.set_bola(self.bola)

    def tambah_blok(self, x, y, hits, warna):
        blok = Blok(self.canvas, x, y, hits, warna)
        self.objek[blok.item] = blok

    def tulis_teks(self, x, y, teks, ukuran='40'):
        font = ('Forte', ukuran)
        return self.canvas.create_text(x, y, text=teks, font=font)

    def update_nyawa(self):
        teks = f'Nyawa: {self.nyawa}'
        if self.hud is None:
            self.hud = self.tulis_teks(50, 20, teks, 15)
        else:
            self.canvas.itemconfig(self.hud, text=teks)

    def mulai_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.teks)
        self.paddle.bola = None
        self.loop_game()

    def loop_game(self):
        self.cek_tabrakan()
        jumlah_blok = len(self.canvas.find_withtag('blok'))
        if jumlah_blok == 0:
            self.bola.kecepatan = None
            self.tulis_teks(300, 200, 'Kamu Menang! Semua Blok Hancur.')
        elif self.bola.posisi()[3] >= self.tinggi:
            self.bola.kecepatan = None
            self.nyawa -= 1
            if self.nyawa < 0:
                self.tulis_teks(300, 200, 'Kamu Kalah! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.bola.update()
            self.after(50, self.loop_game)

    def cek_tabrakan(self):
        coords_bola = self.bola.posisi()
        item = self.canvas.find_overlapping(*coords_bola)
        objek = [self.objek[x] for x in item if x in self.objek]
        self.bola.tabrak(objek)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Hancurkan Blok!')
    game = Game(root)
    game.mainloop()
