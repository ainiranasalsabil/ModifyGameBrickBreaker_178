import tkinter as tk
import random


# Kelas dasar untuk objek permainan yang dapat digambar di canvas
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas  # Canvas tempat objek digambar
        self.item = item  # ID item (digunakan untuk operasi canvas)

    # Mendapatkan posisi objek saat ini
    def get_position(self):
        return self.canvas.coords(self.item)

    # Menggerakkan objek sebanyak (x, y)
    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    # Menghapus objek dari canvas
    def delete(self):
        self.canvas.delete(self.item)


# Kelas Ball (bola) yang mewakili bola dalam permainan
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 12  # Radius bola
        self.direction = [1, -1]  # Arah pergerakan bola (x dan y)
        self.speed = 5  # Kecepatan bola
        # Membuat bola di canvas (bentuk oval)
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#FFD700', outline='gold', width=2)  # Bola emas dengan efek cahaya
        super(Ball, self).__init__(canvas, item)

    # Memperbarui posisi bola
    def update(self):
        coords = self.get_position()  # Mendapatkan koordinat bola saat ini
        width = self.canvas.winfo_width()  # Mendapatkan lebar canvas
        # Membalik arah bola jika mengenai dinding kiri atau kanan
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # Membalik arah bola jika mengenai dinding atas
        if coords[1] <= 0:
            self.direction[1] *= -1
        # Menggerakkan bola berdasarkan arah dan kecepatan
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    # Menangani tabrakan dengan objek lain
    def collide(self, game_objects):
        coords = self.get_position()  # Mendapatkan posisi bola
        x = (coords[0] + coords[2]) * 0.5  # Titik tengah bola di sumbu x
        if len(game_objects) > 1:
            self.direction[1] *= -1  # Membalik arah bola di sumbu y untuk tabrakan ganda
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()  # Mendapatkan posisi objek yang ditabrak
            # Membalik arah bola berdasarkan posisi tabrakan
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1  # Membalik arah bola jika mengenai sisi objek

        # Menangani objek seperti Brick (balok) yang dihantam bola
        for game_object in game_objects:
            if isinstance(game_object, Brick):  # Jika tabrakan dengan balok, maka balok dihantam
                game_object.hit()


# Kelas Paddle (paddle) yang mewakili paddle pemain
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100  # Lebar paddle
        self.height = 15  # Tinggi paddle
        self.ball = None  # Bola yang terhubung dengan paddle (bola mengikuti paddle)
        # Membuat paddle di canvas (bentuk persegi panjang)
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FF5733', outline='darkred')  # Paddle berwarna oranye dengan outline lebih gelap
        super(Paddle, self).__init__(canvas, item)

    # Menetapkan bola yang akan mengikuti paddle
    def set_ball(self, ball):
        self.ball = ball

    # Menggerakkan paddle ke kiri atau kanan berdasarkan offset
    def move(self, offset):
        coords = self.get_position()  # Mendapatkan posisi paddle saat ini
        width = self.canvas.winfo_width()  # Mendapatkan lebar canvas
        # Memastikan paddle tidak keluar batas (kiri dan kanan)
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)  # Menggerakkan paddle
            if self.ball is not None:
                self.ball.move(offset, 0)  # Menggerakkan bola bersama paddle

    # Mengubah ukuran paddle (digunakan untuk power-up)
    def resize(self, new_width):
        self.width = new_width  # Memperbarui lebar
        # Memperbarui koordinat paddle berdasarkan lebar baru
        self.canvas.coords(self.item,
                           self.get_position()[0] - new_width / 2,
                           self.get_position()[1],
                           self.get_position()[0] + new_width / 2,
                           self.get_position()[1] + self.height)


# Kelas Brick (balok) yang mewakili balok yang akan dihancurkan oleh bola
class Brick(GameObject):
    COLORS = {1: '#FF6347', 2: '#F39C12', 3: '#27AE60', 'indestructible': '#8E44AD'}  # Skema warna balok

    def __init__(self, canvas, x, y, hits, indestructible=False):
        self.width = 75  # Lebar balok
        self.height = 20  # Tinggi balok
        self.hits = hits  # Jumlah hit yang diperlukan untuk menghancurkan balok
        self.indestructible = indestructible  # Apakah balok tidak bisa dihancurkan
        color = Brick.COLORS['indestructible'] if self.indestructible else Brick.COLORS[hits]
        # Membuat balok di canvas (bentuk persegi panjang)
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick', outline='black')  # Warna balok
        super(Brick, self).__init__(canvas, item)

    # Menangani balok yang dihantam bola
    def hit(self):
        if not self.indestructible:  # Balok yang tidak bisa dihancurkan tidak berubah
            self.hits -= 1  # Mengurangi jumlah hit
            if self.hits == 0:
                self.delete()  # Menghapus balok jika sudah dihancurkan
            else:
                self.canvas.itemconfig(self.item,
                                       fill=Brick.COLORS[self.hits])  # Mengubah warna balok berdasarkan jumlah hit yang tersisa


# Kelas PowerUp yang mewakili power-up yang jatuh dari balok yang dihancurkan
class PowerUp(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 20  # Lebar power-up
        self.height = 20  # Tinggi power-up
        # Membuat power-up di canvas (bentuk lingkaran)
        item = canvas.create_oval(x - self.width / 2, y - self.height / 2,
                                  x + self.width / 2, y + self.height / 2,
                                  fill='yellow', outline='gold')
        super(PowerUp, self).__init__(canvas, item)

    # Menggerakkan power-up ke bawah (jatuh)
    def move(self):
        self.canvas.move(self.item, 0, 5)  # Power-up jatuh sebanyak 5 pixel


# Kelas Game yang mengontrol permainan utama, termasuk loop permainan dan event
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3  # Nyawa awal
        self.width = 610  # Lebar canvas
        self.height = 400  # Tinggi canvas
        # Membuat canvas dengan latar belakang biru muda
        self.canvas = tk.Canvas(self, bg='#B0E0E6',  # Warna latar belakang biru muda
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}  # Dictionary untuk menyimpan objek permainan
        self.ball = None  # Objek bola
        self.paddle = Paddle(self.canvas, self.width / 2, 326)  # Membuat paddle
        self.items[self.paddle.item] = self.paddle
        # Menambahkan balok dengan kapasitas hit yang berbeda
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)  # Menambahkan balok level 3
            self.add_brick(x + 37.5, 70, 2)  # Menambahkan balok level 2
            self.add_brick(x + 37.5, 90, 1)  # Menambahkan balok level 1
            # Menambahkan balok yang tidak bisa dihancurkan secara acak
            if random.choice([True, False]):
                self.add_brick(x + 37.5, 110, 1, True)

        self.hud = None  # Status untuk nyawa dan skor
        self.setup_game()  # Menyiapkan permainan
        self.canvas.focus_set()
        # Mengatur tombol untuk menggerakkan paddle
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))  # Menggerakkan paddle ke kiri
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))  # Menggerakkan paddle ke kanan

    # Menyiapkan permainan, termasuk menambahkan bola dan menampilkan teks awal
    def setup_game(self):
        self.add_ball()
        self.update_lives_text()  # Memperbarui teks nyawa
        self.text = self.draw_text(300, 200, 'Press Space to start')  # Menampilkan pesan untuk memulai permainan
        self.canvas.bind('<space>', lambda _: self.start_game())  # Mulai permainan saat tombol space ditekan

    # Menambahkan bola baru pada posisi paddle
    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()  # Menghapus bola lama
        paddle_coords = self.paddle.get_position()  # Mendapatkan posisi paddle
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5  # Posisi bola di tengah paddle
        self.ball = Ball(self.canvas, x, 310)  # Membuat bola baru
        self.paddle.set_ball(self.ball)  # Menetapkan bola pada paddle

    # Menambahkan balok baru pada posisi tertentu dengan jumlah hit tertentu
    def add_brick(self, x, y, hits, indestructible=False):
        brick = Brick(self.canvas, x, y, hits, indestructible)  # Membuat balok baru
        self.items[brick.item] = brick  # Menambahkan balok ke dalam daftar objek

    # Menambahkan teks di canvas dengan posisi tertentu
    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)  # Mengatur font untuk teks
        return self.canvas.create_text(x, y, text=text,
                                       font=font, fill='#2C3E50')  # Menggambar teks

    # Memperbarui teks nyawa
    def update_lives_text(self):
        text = 'Lives: %s' % self.lives  # Menampilkan jumlah nyawa
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)  # Jika belum ada, menggambar teks pertama kali
        else:
            self.canvas.itemconfig(self.hud, text=text)  # Memperbarui teks

    # Memulai permainan saat tombol space ditekan
    def start_game(self):
        self.canvas.unbind('<space>')  # Menghapus binding tombol space
        self.canvas.delete(self.text)  # Menghapus teks 'Press Space to start'
        self.paddle.ball = None  # Mengatur bola pada paddle menjadi None
        self.game_loop()  # Memulai loop permainan

    # Loop permainan utama yang akan berjalan terus menerus
    def game_loop(self):
        self.check_collisions()  # Mengecek tabrakan antara bola dan objek lainnya
        num_bricks = len(self.canvas.find_withtag('brick'))  # Menghitung jumlah balok
        if num_bricks == 0:  # Jika semua balok sudah dihancurkan
            self.ball.speed = None  # Menghentikan bola
            self.draw_text(300, 200, 'You win! Breaker of Bricks!')  # Menampilkan pesan menang
        elif self.ball.get_position()[3] >= self.height:  # Jika bola jatuh ke bawah (kalah)
            self.ball.speed = None  # Menghentikan bola
            self.lives -= 1  # Mengurangi nyawa
            if self.lives < 0:  # Jika nyawa habis
                self.draw_text(300, 200, 'You Lose! Game Over!')  # Menampilkan pesan kalah
            else:
                self.after(1000, self.setup_game)  # Mengatur ulang permainan setelah 1 detik
        else:
            self.ball.update()  # Memperbarui posisi bola
            self.after(50, self.game_loop)  # Mengulang game loop setiap 50ms

    # Mengecek tabrakan antara bola dan objek-objek lainnya
    def check_collisions(self):
        ball_coords = self.ball.get_position()  # Mendapatkan posisi bola
        items = self.canvas.find_overlapping(*ball_coords)  # Mengetahui objek yang tumpang tindih dengan bola
        objects = [self.items[x] for x in items if x in self.items]  # Mengambil objek dari daftar objek
        self.ball.collide(objects)  # Memproses tabrakan dengan bola

        # Mengecek apakah bola bertabrakan dengan power-up
        for obj in objects:
            if isinstance(obj, PowerUp):  # Jika tabrakan dengan power-up
                self.paddle.resize(self.paddle.width * 1.2)  # Memperbesar paddle
                obj.delete()  # Menghapus power-up



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()
